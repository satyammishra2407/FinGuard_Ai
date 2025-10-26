"""
Machine Learning models for AML risk assessment and pattern detection
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb
import joblib
import os
from datetime import datetime
import config

class MLRiskAssessment:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_importance = {}
        self.model_performance = {}
        
    def prepare_features(self, customers, transactions):
        """
        Prepare features for ML models from customer and transaction data
        """
        features = []
        labels = []
        
        for customer in customers:
            customer_transactions = [t for t in transactions if t.customer_id == customer.customer_id]
            
            if len(customer_transactions) == 0:
                continue
            
            # Extract customer features
            customer_features = self._extract_customer_features(customer, customer_transactions)
            features.append(customer_features)
            
            # Create binary label (1 for high risk, 0 for low risk)
            risk_label = 1 if customer.risk_score > 70 else 0
            labels.append(risk_label)
        
        return np.array(features), np.array(labels)
    
    def _extract_customer_features(self, customer, transactions):
        """
        Extract comprehensive features for a customer
        """
        features = []
        
        # Basic customer features
        features.extend([
            customer.declared_income,
            len(transactions),
            (datetime.now() - customer.account_opening_date).days,
            1 if customer.kyc_status == 'VERIFIED' else 0,
            1 if customer.kyc_status == 'REJECTED' else 0
        ])
        
        if len(transactions) == 0:
            # Pad with zeros if no transactions
            features.extend([0] * 20)
            return features
        
        # Transaction amount features
        amounts = [t.amount for t in transactions]
        features.extend([
            np.mean(amounts),
            np.std(amounts),
            np.max(amounts),
            np.min(amounts),
            np.median(amounts),
            np.sum(amounts)
        ])
        
        # Transaction frequency features
        transaction_dates = [t.timestamp for t in transactions]
        if len(transaction_dates) > 1:
            time_diffs = [(transaction_dates[i+1] - transaction_dates[i]).days 
                         for i in range(len(transaction_dates)-1)]
            features.extend([
                np.mean(time_diffs),
                np.std(time_diffs),
                np.min(time_diffs)
            ])
        else:
            features.extend([0, 0, 0])
        
        # Transaction type features
        transaction_types = [t.transaction_type for t in transactions]
        type_counts = pd.Series(transaction_types).value_counts()
        
        features.extend([
            type_counts.get('CASH_DEPOSIT', 0),
            type_counts.get('CASH_WITHDRAWAL', 0),
            type_counts.get('INTERNATIONAL_TRANSFER', 0),
            type_counts.get('UPI', 0),
            type_counts.get('NEFT', 0)
        ])
        
        # Timing features
        hours = [t.timestamp.hour for t in transactions]
        features.extend([
            len([h for h in hours if h < 6 or h > 22]),  # Night transactions
            len([t for t in transactions if t.timestamp.weekday() >= 5])  # Weekend transactions
        ])
        
        # Beneficiary features
        beneficiaries = [t.beneficiary for t in transactions if t.beneficiary]
        features.extend([
            len(set(beneficiaries)),  # Unique beneficiaries
            len([b for b in beneficiaries if b == 'UNKNOWN'])  # Unknown beneficiaries
        ])
        
        # Amount pattern features
        large_transactions = len([a for a in amounts if a > config.SUSPICIOUS_AMOUNT_THRESHOLD])
        below_threshold = [a for a in amounts if a < config.REPORTING_THRESHOLD]
        
        features.extend([
            large_transactions,
            len(below_threshold),
            np.sum(below_threshold) if below_threshold else 0
        ])
        
        return features
    
    def train_risk_classification_model(self, customers, transactions):
        """
        Train a model to classify customers as high/low risk
        """
        print("Preparing features for risk classification...")
        X, y = self.prepare_features(customers, transactions)
        
        if len(X) == 0:
            print("No data available for training")
            return
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['risk_classification'] = scaler
        
        # Train multiple models
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(random_state=42),
            'xgboost': xgb.XGBClassifier(random_state=42),
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000)
        }
        
        best_model = None
        best_score = 0
        
        for name, model in models.items():
            print(f"Training {name}...")
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            print(f"{name} - Train Score: {train_score:.4f}, Test Score: {test_score:.4f}")
            
            # Store model and performance
            self.models[name] = model
            self.model_performance[name] = {
                'train_score': train_score,
                'test_score': test_score
            }
            
            # Select best model based on test score
            if test_score > best_score:
                best_score = test_score
                best_model = name
        
        # Store feature importance for the best model
        if hasattr(self.models[best_model], 'feature_importances_'):
            self.feature_importance['risk_classification'] = self.models[best_model].feature_importances_
        
        print(f"Best model: {best_model} with test score: {best_score:.4f}")
        
        # Save models
        self.save_models()
        
        return best_model
    
    def predict_risk_score(self, customer, transactions):
        """
        Predict risk score for a customer using trained models
        """
        if 'risk_classification' not in self.models:
            print("Model not trained yet")
            return 0
        
        # Extract features
        features = self._extract_customer_features(customer, transactions)
        features = np.array(features).reshape(1, -1)
        
        # Scale features
        if 'risk_classification' in self.scalers:
            features = self.scalers['risk_classification'].transform(features)
        
        # Get predictions from all models
        predictions = {}
        for name, model in self.models.items():
            if name in ['random_forest', 'gradient_boosting', 'xgboost']:
                # Get probability of high risk
                prob = model.predict_proba(features)[0][1]
                predictions[name] = prob * 100  # Convert to 0-100 scale
            else:
                # For logistic regression, get probability
                prob = model.predict_proba(features)[0][1]
                predictions[name] = prob * 100
        
        # Return average prediction
        return np.mean(list(predictions.values()))
    
    def train_transaction_anomaly_model(self, transactions):
        """
        Train a model to detect anomalous transactions
        """
        print("Training transaction anomaly detection model...")
        
        # Extract transaction features
        features = []
        labels = []
        
        for txn in transactions:
            feature_vector = [
                txn.amount,
                txn.timestamp.hour,
                txn.timestamp.weekday(),
                len(txn.beneficiary) if txn.beneficiary else 0,
                1 if txn.transaction_type == 'CASH_DEPOSIT' else 0,
                1 if txn.transaction_type == 'INTERNATIONAL_TRANSFER' else 0,
                1 if txn.amount > config.SUSPICIOUS_AMOUNT_THRESHOLD else 0,
                1 if txn.timestamp.hour < 6 or txn.timestamp.hour > 22 else 0,
                1 if txn.timestamp.weekday() >= 5 else 0
            ]
            features.append(feature_vector)
            labels.append(1 if txn.is_suspicious else 0)
        
        X = np.array(features)
        y = np.array(labels)
        
        if len(X) == 0:
            print("No transaction data available for training")
            return
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['transaction_anomaly'] = scaler
        
        # Train XGBoost for transaction anomaly detection
        model = xgb.XGBClassifier(random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        print(f"Transaction Anomaly Model - Train Score: {train_score:.4f}, Test Score: {test_score:.4f}")
        
        self.models['transaction_anomaly'] = model
        self.model_performance['transaction_anomaly'] = {
            'train_score': train_score,
            'test_score': test_score
        }
        
        # Store feature importance
        self.feature_importance['transaction_anomaly'] = model.feature_importances_
        
        # Save models
        self.save_models()
    
    def detect_transaction_anomalies(self, transactions):
        """
        Detect anomalous transactions using trained model
        """
        if 'transaction_anomaly' not in self.models:
            print("Transaction anomaly model not trained yet")
            return []
        
        anomalies = []
        
        for txn in transactions:
            # Extract features
            features = np.array([
                txn.amount,
                txn.timestamp.hour,
                txn.timestamp.weekday(),
                len(txn.beneficiary) if txn.beneficiary else 0,
                1 if txn.transaction_type == 'CASH_DEPOSIT' else 0,
                1 if txn.transaction_type == 'INTERNATIONAL_TRANSFER' else 0,
                1 if txn.amount > config.SUSPICIOUS_AMOUNT_THRESHOLD else 0,
                1 if txn.timestamp.hour < 6 or txn.timestamp.hour > 22 else 0,
                1 if txn.timestamp.weekday() >= 5 else 0
            ]).reshape(1, -1)
            
            # Scale features
            if 'transaction_anomaly' in self.scalers:
                features = self.scalers['transaction_anomaly'].transform(features)
            
            # Get anomaly probability
            model = self.models['transaction_anomaly']
            anomaly_prob = model.predict_proba(features)[0][1]
            
            if anomaly_prob > 0.7:  # Threshold for anomaly
                anomalies.append({
                    'transaction_id': txn.transaction_id,
                    'amount': txn.amount,
                    'timestamp': txn.timestamp,
                    'anomaly_probability': anomaly_prob,
                    'transaction_type': txn.transaction_type
                })
        
        return anomalies
    
    def get_feature_importance(self, model_name):
        """
        Get feature importance for a specific model
        """
        if model_name in self.feature_importance:
            return self.feature_importance[model_name]
        return None
    
    def get_model_performance(self):
        """
        Get performance metrics for all trained models
        """
        return self.model_performance
    
    def save_models(self):
        """
        Save trained models to disk
        """
        os.makedirs('models', exist_ok=True)
        
        for name, model in self.models.items():
            joblib.dump(model, f'models/{name}_model.pkl')
        
        for name, scaler in self.scalers.items():
            joblib.dump(scaler, f'models/{name}_scaler.pkl')
        
        print("Models saved successfully")
    
    def load_models(self):
        """
        Load pre-trained models from disk
        """
        model_files = {
            'risk_classification': ['random_forest', 'gradient_boosting', 'xgboost', 'logistic_regression'],
            'transaction_anomaly': ['transaction_anomaly']
        }
        
        for category, models in model_files.items():
            for model_name in models:
                model_path = f'models/{model_name}_model.pkl'
                scaler_path = f'models/{model_name}_scaler.pkl'
                
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
                    print(f"Loaded {model_name} model")
                
                if os.path.exists(scaler_path):
                    self.scalers[model_name] = joblib.load(scaler_path)
                    print(f"Loaded {model_name} scaler")
        
        print("Model loading completed")
