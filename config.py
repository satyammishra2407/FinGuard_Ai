"""
Configuration settings for FinGuard AI AML Platform
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finguard_ai.db")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "finguard_ai")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Application Configuration
APP_NAME = "FinGuard AI - AML Platform"
VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Risk Scoring Configuration
RISK_THRESHOLDS = {
    "LOW": 0,
    "MEDIUM": 30,
    "HIGH": 60,
    "CRITICAL": 80
}

# Transaction Monitoring Configuration
REPORTING_THRESHOLD = 900000  # ₹9 lakhs
SUSPICIOUS_AMOUNT_THRESHOLD = 1000000  # ₹10 lakhs
MAX_DAILY_TRANSACTIONS = 10
MAX_LINKED_ACCOUNTS = 5

# ML Model Configuration
MODEL_RETRAIN_INTERVAL = 24  # hours
FEATURE_IMPORTANCE_THRESHOLD = 0.1

# Alert Configuration
ALERT_RETENTION_DAYS = 90
AUTO_ALERT_THRESHOLD = 70

# Network Analysis Configuration
MIN_CLUSTER_SIZE = 3
COMMON_BENEFICIARY_THRESHOLD = 2
NETWORK_COMPLEXITY_THRESHOLD = 0.7
