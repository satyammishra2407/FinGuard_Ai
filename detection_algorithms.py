"""
Advanced detection algorithms for AML pattern recognition
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import networkx as nx
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import config

class AMLDetectionEngine:
    def __init__(self):
        self.structuring_threshold = config.REPORTING_THRESHOLD
        self.suspicious_amount_threshold = config.SUSPICIOUS_AMOUNT_THRESHOLD
        self.max_daily_transactions = config.MAX_DAILY_TRANSACTIONS
        self.max_linked_accounts = config.MAX_LINKED_ACCOUNTS

    def calculate_risk_score(self, customer_data, transactions):
        """
        Calculate comprehensive risk score for a customer
        """
        risk_score = 0
        risk_factors = []
        
        # Income-Transaction Mismatch (Black Money Detection)
        if len(transactions) > 0:
            total_amount = sum(t.amount for t in transactions)
            income_ratio = total_amount / customer_data.declared_income if customer_data.declared_income > 0 else 0
            
            if income_ratio > 2:
                income_risk = min(25, income_ratio * 10)
                risk_score += income_risk
                risk_factors.append(f"Income mismatch: {income_ratio:.2f}x declared income")
            
            # Structuring Detection
            if self.detect_structured_transactions(transactions):
                risk_score += 20
                risk_factors.append("Structuring pattern detected")
            
            # Multiple Accounts (simulated)
            if hasattr(customer_data, 'linked_accounts') and customer_data.linked_accounts > self.max_linked_accounts:
                risk_score += 15
                risk_factors.append(f"Multiple linked accounts: {customer_data.linked_accounts}")
            
            # Cross-border Transactions
            international_count = len([t for t in transactions if t.transaction_type == 'INTERNATIONAL_TRANSFER'])
            if international_count > 10:
                risk_score += 15
                risk_factors.append(f"High international transactions: {international_count}")
            
            # Unusual Timing
            if self.detect_unusual_timing(transactions):
                risk_score += 10
                risk_factors.append("Unusual transaction timing")
            
            # Network Complexity
            network_complexity = self.calculate_network_complexity(customer_data, transactions)
            if network_complexity > config.NETWORK_COMPLEXITY_THRESHOLD:
                risk_score += 15
                risk_factors.append(f"High network complexity: {network_complexity:.2f}")
            
            # Large Transaction Frequency
            large_transactions = [t for t in transactions if t.amount > self.suspicious_amount_threshold]
            if len(large_transactions) > 5:
                risk_score += 12
                risk_factors.append(f"Frequent large transactions: {len(large_transactions)}")
            
            # Rapid Succession Transactions
            if self.detect_rapid_succession(transactions):
                risk_score += 8
                risk_factors.append("Rapid succession transactions")
        
        # KYC Status
        if customer_data.kyc_status == 'REJECTED':
            risk_score += 20
            risk_factors.append("KYC rejected")
        elif customer_data.kyc_status == 'PENDING':
            risk_score += 5
            risk_factors.append("KYC pending")
        
        # Account Age
        account_age_days = (datetime.now() - customer_data.account_opening_date).days
        if account_age_days < 30:
            risk_score += 5
            risk_factors.append("New account (< 30 days)")
        
        return min(risk_score, 100), risk_factors

    def detect_structured_transactions(self, transactions):
        """
        Detect structuring pattern - multiple transactions below reporting threshold
        """
        if len(transactions) < 3:
            return False
        
        # Group transactions by date
        daily_groups = defaultdict(list)
        for txn in transactions:
            date = txn.timestamp.date()
            daily_groups[date].append(txn)
        
        for date, daily_txns in daily_groups.items():
            if len(daily_txns) >= 3:
                below_threshold = [t for t in daily_txns if t.amount < self.structuring_threshold]
                if len(below_threshold) >= 3:
                    total_amount = sum(t.amount for t in below_threshold)
                    if total_amount > self.structuring_threshold:
                        return True
        
        return False

    def detect_smurfing_network(self, customers, transactions):
        """
        Detect smurfing networks using graph analysis
        """
        smurf_networks = []
        
        # Build transaction graph
        G = self.build_transaction_graph(transactions)
        
        if len(G.nodes()) < 3:
            return smurf_networks
        
        # Find connected components
        connected_components = list(nx.connected_components(G))
        
        for component in connected_components:
            if len(component) >= config.MIN_CLUSTER_SIZE:
                # Analyze component for smurfing patterns
                component_transactions = [t for t in transactions 
                                       if t.customer_id in component]
                
                # Check for common beneficiaries
                common_beneficiaries = self.find_common_beneficiaries(component, component_transactions)
                
                # Also check for structuring patterns in the network
                has_structuring = self.detect_network_structuring(component_transactions)
                
                # Lower threshold for detection
                if len(common_beneficiaries) >= 1 or has_structuring:
                    total_volume = sum(t.amount for t in component_transactions)
                    
                    smurf_networks.append({
                        'accounts': list(component),
                        'common_beneficiaries': common_beneficiaries,
                        'total_volume': total_volume,
                        'transaction_count': len(component_transactions),
                        'risk_score': self.calculate_network_risk_score(component_transactions),
                        'has_structuring': has_structuring
                    })
        
        return smurf_networks

    def build_transaction_graph(self, transactions):
        """
        Build a graph of connected accounts based on transactions
        """
        G = nx.Graph()
        
        # Add nodes (customers)
        for txn in transactions:
            G.add_node(txn.customer_id)
        
        # Add edges based on common beneficiaries
        beneficiary_accounts = defaultdict(set)
        for txn in transactions:
            if txn.beneficiary and txn.beneficiary != "UNKNOWN":
                beneficiary_accounts[txn.beneficiary].add(txn.customer_id)
        
        # Connect accounts that share beneficiaries
        for beneficiary, accounts in beneficiary_accounts.items():
            if len(accounts) > 1:
                accounts_list = list(accounts)
                for i in range(len(accounts_list)):
                    for j in range(i + 1, len(accounts_list)):
                        G.add_edge(accounts_list[i], accounts_list[j])
        
        return G

    def find_common_beneficiaries(self, accounts, transactions):
        """
        Find common beneficiaries among a group of accounts
        """
        account_beneficiaries = defaultdict(set)
        
        for txn in transactions:
            if txn.customer_id in accounts and txn.beneficiary:
                account_beneficiaries[txn.customer_id].add(txn.beneficiary)
        
        if len(account_beneficiaries) < 2:
            return []
        
        # Find intersection of all beneficiary sets
        common = set.intersection(*account_beneficiaries.values())
        return list(common)

    def detect_network_structuring(self, transactions):
        """
        Detect structuring patterns across a network of transactions
        """
        if len(transactions) < 6:
            return False
        
        # Group by date
        daily_groups = defaultdict(list)
        for txn in transactions:
            date = txn.timestamp.date()
            daily_groups[date].append(txn)
        
        # Check for structuring across multiple days
        structuring_days = 0
        for date, daily_txns in daily_groups.items():
            if len(daily_txns) >= 3:
                below_threshold = [t for t in daily_txns if t.amount < self.structuring_threshold]
                if len(below_threshold) >= 3:
                    total_amount = sum(t.amount for t in below_threshold)
                    if total_amount > self.structuring_threshold:
                        structuring_days += 1
        
        # If structuring detected on 2+ days, it's a network pattern
        return structuring_days >= 2

    def calculate_network_complexity(self, customer_data, transactions):
        """
        Calculate network complexity score for a customer
        """
        if len(transactions) < 2:
            return 0.0
        
        # Simple complexity based on unique beneficiaries and transaction types
        unique_beneficiaries = len(set(t.beneficiary for t in transactions if t.beneficiary))
        unique_types = len(set(t.transaction_type for t in transactions))
        unique_locations = len(set(t.location for t in transactions))
        
        # Normalize complexity score
        complexity = (unique_beneficiaries * 0.4 + unique_types * 0.3 + unique_locations * 0.3) / 10
        return min(complexity, 1.0)

    def detect_unusual_timing(self, transactions):
        """
        Detect unusual transaction timing patterns
        """
        if len(transactions) < 5:
            return False
        
        # Check for night transactions (10 PM to 6 AM)
        night_transactions = [t for t in transactions 
                            if t.timestamp.hour >= 22 or t.timestamp.hour <= 6]
        
        night_ratio = len(night_transactions) / len(transactions)
        
        # Check for weekend transactions
        weekend_transactions = [t for t in transactions 
                              if t.timestamp.weekday() >= 5]
        weekend_ratio = len(weekend_transactions) / len(transactions)
        
        # Unusual if more than 30% are night transactions or 80% are weekend
        return night_ratio > 0.3 or weekend_ratio > 0.8

    def detect_rapid_succession(self, transactions):
        """
        Detect rapid succession of transactions
        """
        if len(transactions) < 3:
            return False
        
        # Sort transactions by timestamp
        sorted_txns = sorted(transactions, key=lambda x: x.timestamp)
        
        # Check for 3+ transactions within 1 hour
        for i in range(len(sorted_txns) - 2):
            time_diff = (sorted_txns[i + 2].timestamp - sorted_txns[i].timestamp).total_seconds()
            if time_diff < 3600:  # 1 hour
                return True
        
        return False

    def calculate_network_risk_score(self, transactions):
        """
        Calculate risk score for a network of transactions
        """
        if not transactions:
            return 0
        
        risk_score = 0
        
        # Volume-based risk
        total_volume = sum(t.amount for t in transactions)
        if total_volume > 10000000:  # 1 crore
            risk_score += 30
        elif total_volume > 5000000:  # 50 lakhs
            risk_score += 20
        elif total_volume > 1000000:  # 10 lakhs
            risk_score += 10
        
        # Frequency-based risk
        if len(transactions) > 100:
            risk_score += 20
        elif len(transactions) > 50:
            risk_score += 10
        
        # Pattern-based risk
        if self.detect_structured_transactions(transactions):
            risk_score += 25
        
        return min(risk_score, 100)

    def detect_behavioral_anomalies(self, customer_data, transactions):
        """
        Detect behavioral anomalies using machine learning
        """
        if len(transactions) < 10:
            return []
        
        anomalies = []
        
        # Prepare features for anomaly detection
        features = self.extract_transaction_features(transactions)
        
        if len(features) < 5:
            return anomalies
        
        # Use Isolation Forest for anomaly detection
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomaly_labels = iso_forest.fit_predict(features)
        
        # Identify anomalous transactions
        for i, (txn, is_anomaly) in enumerate(zip(transactions, anomaly_labels)):
            if is_anomaly == -1:  # Anomaly detected
                anomalies.append({
                    'transaction_id': txn.transaction_id,
                    'amount': txn.amount,
                    'timestamp': txn.timestamp,
                    'anomaly_score': iso_forest.decision_function([features[i]])[0]
                })
        
        return anomalies

    def extract_transaction_features(self, transactions):
        """
        Extract features from transactions for ML analysis
        """
        features = []
        
        for txn in transactions:
            feature_vector = [
                txn.amount,
                txn.timestamp.hour,
                txn.timestamp.weekday(),
                len(txn.beneficiary) if txn.beneficiary else 0,
                1 if txn.transaction_type == 'CASH_DEPOSIT' else 0,
                1 if txn.transaction_type == 'INTERNATIONAL_TRANSFER' else 0,
                1 if txn.amount > self.suspicious_amount_threshold else 0
            ]
            features.append(feature_vector)
        
        return np.array(features)

    def generate_risk_report(self, customer_data, transactions):
        """
        Generate comprehensive risk assessment report
        """
        risk_score, risk_factors = self.calculate_risk_score(customer_data, transactions)
        
        # Determine risk level
        if risk_score >= config.RISK_THRESHOLDS['CRITICAL']:
            risk_level = 'CRITICAL'
        elif risk_score >= config.RISK_THRESHOLDS['HIGH']:
            risk_level = 'HIGH'
        elif risk_score >= config.RISK_THRESHOLDS['MEDIUM']:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # Detect patterns
        patterns = {
            'structuring': self.detect_structured_transactions(transactions),
            'unusual_timing': self.detect_unusual_timing(transactions),
            'rapid_succession': self.detect_rapid_succession(transactions)
        }
        
        # Behavioral anomalies
        anomalies = self.detect_behavioral_anomalies(customer_data, transactions)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'patterns': patterns,
            'anomalies': anomalies,
            'total_transactions': len(transactions),
            'total_volume': sum(t.amount for t in transactions),
            'assessment_date': datetime.now()
        }
