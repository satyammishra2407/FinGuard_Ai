"""
Enhanced synthetic data generator for FinGuard AI with smurfing patterns
"""
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd
import numpy as np
from database import Customer, Transaction, Alert, RiskFactor, SessionLocal
import config

fake = Faker('en_IN')

class EnhancedDataGenerator:
    def __init__(self):
        self.db = SessionLocal()
        self.customer_risk_profiles = {
            'LOW': {'income_range': (500000, 2000000), 'risk_weight': 0.1},
            'MEDIUM': {'income_range': (2000000, 10000000), 'risk_weight': 0.3},
            'HIGH': {'income_range': (10000000, 50000000), 'risk_weight': 0.6},
            'CRITICAL': {'income_range': (50000000, 200000000), 'risk_weight': 0.9}
        }
        
        self.transaction_types = [
            'CASH_DEPOSIT', 'CASH_WITHDRAWAL', 'TRANSFER', 'UPI', 
            'NEFT', 'RTGS', 'IMPS', 'CARD_PAYMENT', 'INTERNATIONAL_TRANSFER'
        ]
        
        self.beneficiary_types = [
            'INDIVIDUAL', 'BUSINESS', 'GOVERNMENT', 'NGO', 'UNKNOWN'
        ]
        
        self.locations = [
            'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 
            'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'
        ]
        
        # Common beneficiaries for smurfing networks
        self.smurf_beneficiaries = [
            "ABC Trading Co", "XYZ Enterprises", "Global Finance Ltd", 
            "Metro Business Corp", "Capital Investment Group", "Trade Solutions Inc"
        ]

    def generate_customers(self, count=1000):
        """Generate synthetic customer data"""
        customers = []
        
        for i in range(count):
            # Assign risk profile
            risk_profile = random.choices(
                list(self.customer_risk_profiles.keys()),
                weights=[0.4, 0.3, 0.2, 0.1]
            )[0]
            
            profile = self.customer_risk_profiles[risk_profile]
            income = random.uniform(*profile['income_range'])
            
            customer = Customer(
                customer_id=f"CUST_{str(uuid.uuid4())[:8].upper()}",
                name=fake.name(),
                declared_income=income,
                occupation=fake.job(),
                kyc_status=random.choices(['VERIFIED', 'PENDING', 'REJECTED'], weights=[0.8, 0.15, 0.05])[0],
                account_opening_date=fake.date_time_between(start_date='-5y', end_date='now'),
                risk_score=random.uniform(0, 100) * profile['risk_weight']
            )
            customers.append(customer)
        
        return customers

    def create_smurfing_networks(self, customers, num_networks=5):
        """Create smurfing networks with shared beneficiaries"""
        networks = []
        high_risk_customers = [c for c in customers if c.risk_score > 60]
        
        for i in range(min(num_networks, len(high_risk_customers) // 3)):
            # Select 3-6 customers for each network
            network_size = random.randint(3, 6)
            network_customers = random.sample(high_risk_customers, network_size)
            
            # Assign a common beneficiary
            common_beneficiary = random.choice(self.smurf_beneficiaries)
            
            networks.append({
                'customers': network_customers,
                'common_beneficiary': common_beneficiary,
                'network_id': f"NET_{i+1}"
            })
        
        return networks

    def generate_smurfing_transactions(self, network, transactions_per_customer=20):
        """Generate transactions for a smurfing network"""
        transactions = []
        start_date = datetime.now() - timedelta(days=180)
        
        for customer in network['customers']:
            # Generate multiple small transactions to the common beneficiary
            for i in range(transactions_per_customer):
                # Small amounts below reporting threshold
                amount = random.uniform(50000, config.REPORTING_THRESHOLD * 0.8)
                
                transaction = Transaction(
                    transaction_id=f"TXN_{str(uuid.uuid4())[:8].upper()}",
                    customer_id=customer.customer_id,
                    amount=amount,
                    timestamp=fake.date_time_between(start_date=start_date, end_date='now'),
                    transaction_type=random.choice(['NEFT', 'IMPS', 'UPI']),
                    beneficiary=network['common_beneficiary'],
                    beneficiary_type='BUSINESS',
                    location=random.choice(self.locations),
                    currency="INR",
                    status='COMPLETED',
                    device_id=f"DEV_{random.randint(1000, 9999)}",
                    ip_address=fake.ipv4(),
                    is_suspicious=True  # Mark as suspicious for smurfing
                )
                transactions.append(transaction)
        
        return transactions

    def generate_transactions(self, customers, count=50000):
        """Generate synthetic transaction data with smurfing patterns"""
        transactions = []
        start_date = datetime.now() - timedelta(days=365)
        
        # Create smurfing networks
        smurf_networks = self.create_smurfing_networks(customers)
        
        # Generate regular transactions
        for i in range(count):
            customer = random.choice(customers)
            transaction_type = random.choice(self.transaction_types)
            
            # Generate amount based on customer profile and transaction type
            base_amount = self._generate_transaction_amount(customer, transaction_type)
            
            # Add some suspicious patterns
            if random.random() < 0.05:  # 5% suspicious transactions
                base_amount = self._make_transaction_suspicious(base_amount, transaction_type)
            
            transaction = Transaction(
                transaction_id=f"TXN_{str(uuid.uuid4())[:8].upper()}",
                customer_id=customer.customer_id,
                amount=base_amount,
                timestamp=fake.date_time_between(start_date=start_date, end_date='now'),
                transaction_type=transaction_type,
                beneficiary=fake.name() if random.random() < 0.7 else "UNKNOWN",
                beneficiary_type=random.choice(self.beneficiary_types),
                location=random.choice(self.locations),
                currency="INR",
                status=random.choices(['COMPLETED', 'PENDING', 'FAILED'], weights=[0.95, 0.03, 0.02])[0],
                device_id=f"DEV_{random.randint(1000, 9999)}",
                ip_address=fake.ipv4(),
                is_suspicious=base_amount > config.SUSPICIOUS_AMOUNT_THRESHOLD
            )
            transactions.append(transaction)
        
        # Add smurfing network transactions
        for network in smurf_networks:
            network_transactions = self.generate_smurfing_transactions(network)
            transactions.extend(network_transactions)
        
        return transactions

    def _generate_transaction_amount(self, customer, transaction_type):
        """Generate transaction amount based on customer and transaction type"""
        base_amount = random.uniform(1000, 100000)
        
        # Adjust based on customer risk profile
        risk_profile = self.get_customer_risk_profile(customer)
        if risk_profile == 'HIGH':
            base_amount *= random.uniform(1.5, 3)
        elif risk_profile == 'CRITICAL':
            base_amount *= random.uniform(2, 5)
        
        # Adjust based on transaction type
        if transaction_type == 'INTERNATIONAL_TRANSFER':
            base_amount *= random.uniform(2, 8)
        elif transaction_type in ['RTGS', 'NEFT']:
            base_amount *= random.uniform(1.2, 3)
        elif transaction_type == 'UPI':
            base_amount = min(base_amount, 200000)  # UPI limits
        
        return base_amount

    def _make_transaction_suspicious(self, amount, transaction_type):
        """Make a transaction suspicious"""
        if transaction_type == 'CASH_DEPOSIT':
            # Large cash deposits
            return amount * random.uniform(3, 10)
        elif transaction_type == 'INTERNATIONAL_TRANSFER':
            # Very large international transfers
            return amount * random.uniform(5, 15)
        else:
            # Just make it larger
            return amount * random.uniform(2, 5)

    def get_customer_risk_profile(self, customer):
        """Get risk profile for a customer"""
        if customer.risk_score >= 80:
            return 'CRITICAL'
        elif customer.risk_score >= 60:
            return 'HIGH'
        elif customer.risk_score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'

    def generate_alerts(self, customers, transactions):
        """Generate suspicious activity alerts"""
        alerts = []
        
        for customer in customers:
            if customer.risk_score > 70:
                customer_transactions = [t for t in transactions if t.customer_id == customer.customer_id]
                
                # Generate alerts based on patterns
                if self.detect_structured_transactions(customer_transactions):
                    alert = Alert(
                        alert_id=f"ALT_{str(uuid.uuid4())[:8].upper()}",
                        customer_id=customer.customer_id,
                        alert_type="STRUCTURING",
                        risk_score=customer.risk_score,
                        triggered_rules="Multiple transactions below reporting threshold",
                        timestamp=datetime.now(),
                        status="OPEN"
                    )
                    alerts.append(alert)
                
                if len([t for t in customer_transactions if t.is_suspicious]) > 5:
                    alert = Alert(
                        alert_id=f"ALT_{str(uuid.uuid4())[:8].upper()}",
                        customer_id=customer.customer_id,
                        alert_type="SUSPICIOUS_ACTIVITY",
                        risk_score=customer.risk_score,
                        triggered_rules="Multiple suspicious transactions",
                        timestamp=datetime.now(),
                        status="OPEN"
                    )
                    alerts.append(alert)
        
        return alerts

    def detect_structured_transactions(self, transactions):
        """Detect structuring pattern"""
        if len(transactions) < 3:
            return False
        
        # Group by date
        daily_groups = {}
        for txn in transactions:
            date = txn.timestamp.date()
            if date not in daily_groups:
                daily_groups[date] = []
            daily_groups[date].append(txn)
        
        # Check for structuring
        for date, daily_txns in daily_groups.items():
            if len(daily_txns) >= 3:
                below_threshold = [t for t in daily_txns if t.amount < config.REPORTING_THRESHOLD]
                if len(below_threshold) >= 3:
                    total_amount = sum(t.amount for t in below_threshold)
                    if total_amount > config.REPORTING_THRESHOLD:
                        return True
        
        return False

    def populate_database(self, num_customers=1000, num_transactions_per_customer=50):
        """Generate and populate database with enhanced data"""
        print(f"Generating {num_customers} customers...")
        customers = self.generate_customers(num_customers)
        
        num_transactions = num_customers * num_transactions_per_customer
        print(f"Generating {num_transactions} transactions with smurfing patterns...")
        transactions = self.generate_transactions(customers, num_transactions)
        
        print("Generating alerts...")
        alerts = self.generate_alerts(customers, transactions)
        
        print("Saving to database...")
        try:
            # Clear existing data
            self.db.query(Transaction).delete()
            self.db.query(Alert).delete()
            self.db.query(Customer).delete()
            self.db.commit()
            
            # Insert new data
            self.db.add_all(customers)
            self.db.add_all(transactions)
            self.db.add_all(alerts)
            self.db.commit()
            
            print(f"Successfully generated {len(customers)} customers, {len(transactions)} transactions, {len(alerts)} alerts")
            print("Smurfing networks created with shared beneficiaries")
            
        except Exception as e:
            print(f"Error saving to database: {e}")
            self.db.rollback()
        finally:
            self.db.close()

if __name__ == "__main__":
    generator = EnhancedDataGenerator()
    generator.populate_database()
