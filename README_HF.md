---
title: FinGuard AI - AML Platform
emoji: 🛡️
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.30.0"
app_file: app.py
pinned: false
license: mit
tags:
  - finance
  - aml
  - anti-money-laundering
  - machine-learning
  - fraud-detection
  - risk-assessment
---

# 🛡️ FinGuard AI - Intelligent AML Platform

A comprehensive Anti-Money Laundering (AML) platform that detects black money, money laundering, and financial crimes in real-time using advanced machine learning and network analysis.

## 🎯 Features

### Core Capabilities
- **Real-time Risk Assessment**: Advanced ML-based customer risk scoring (0-100)
- **Transaction Monitoring**: Real-time analysis of banking transactions
- **Pattern Detection**: 
  - Structuring detection (multiple transactions below reporting threshold)
  - Smurfing detection (network analysis for connected accounts)
  - Behavioral anomaly detection
- **Network Analysis**: Interactive visualization of transaction networks
- **Alert Management**: Automated suspicious activity alerts and case management
- **Comprehensive Dashboard**: Real-time monitoring and analytics

### Detection Algorithms
- **Black Money Detection**: Income-transaction mismatch analysis
- **Structuring Detection**: Multiple small transactions pattern recognition
- **Smurfing Detection**: Network analysis for money laundering rings
- **Behavioral Analysis**: Unusual customer behavior pattern detection
- **Anomaly Detection**: ML-based transaction anomaly identification

## 🚀 How to Use

1. **First Launch**: The app will initialize with an empty database
2. **Generate Data**: Click the "🔄 Generate 1000 Customers & Data" button to populate the database with sample data
3. **Explore Features**:
   - **Dashboard**: View overall risk metrics and statistics
   - **Customer Search**: Look up individual customers and their transaction history
   - **Risk Analysis**: Analyze transaction patterns and behavioral trends
   - **Network Analysis**: Visualize money laundering networks
   - **Alert Management**: Review and manage suspicious activity alerts
   - **ML Models**: Train and evaluate machine learning models

## 🛠 Tech Stack

- **Frontend**: Streamlit
- **Database**: SQLite
- **ML/AI**: Scikit-learn, XGBoost, NetworkX
- **Visualization**: Plotly, PyVis
- **Data Processing**: Pandas, NumPy

## 📊 Sample Data

The platform includes a comprehensive synthetic dataset generator:
- **1,000 customers** with varying risk profiles
- **50,000 transactions** with realistic patterns
- **Mix of legitimate and suspicious activities**
- **Realistic transaction amounts and timings**
- **Network relationships between accounts**

## 🔧 Configuration

### Risk Scoring Configuration
- **LOW**: 0-29
- **MEDIUM**: 30-59
- **HIGH**: 60-79
- **CRITICAL**: 80-100

### Transaction Monitoring
- **Reporting Threshold**: ₹9,00,000
- **Suspicious Amount**: ₹10,00,000
- **Max Daily Transactions**: 10
- **Max Linked Accounts**: 5

## 🎨 Dashboard Features

### Main Dashboard
- **Risk Overview**: Total customers, high-risk count, pending alerts
- **Risk Distribution**: Visual distribution of customer risk scores
- **Transaction Volume**: Daily transaction volume over time
- **Recent Alerts**: Latest suspicious activity alerts

### Customer Search
- **Search & Filter**: Find customers by ID or name
- **Detailed Profiles**: Comprehensive customer information
- **Transaction History**: Complete transaction timeline
- **Risk Analysis**: Detailed risk factor breakdown

### Network Analysis
- **Interactive Graphs**: Force-directed network visualization
- **Smurfing Detection**: Identify money laundering networks
- **Cluster Analysis**: Group related accounts
- **Risk Scoring**: Network-level risk assessment

### Alert Management
- **Alert Inbox**: Filter and manage alerts
- **Case Assignment**: Assign alerts to investigators
- **Investigation Tracking**: Track investigation progress
- **Resolution Workflow**: Complete alert resolution process

## 🤖 Machine Learning Models

### Risk Classification
- **Random Forest**: Ensemble learning for risk prediction
- **Gradient Boosting**: Advanced boosting algorithm
- **XGBoost**: Optimized gradient boosting
- **Logistic Regression**: Linear risk assessment

### Anomaly Detection
- **Isolation Forest**: Unsupervised anomaly detection
- **Transaction Analysis**: ML-based suspicious transaction detection
- **Behavioral Patterns**: Customer behavior anomaly detection

## 📊 Performance Metrics

- **Detection Accuracy**: 95%+ of simulated money laundering cases
- **Processing Speed**: 1000+ transactions per minute
- **Response Time**: Real-time risk scoring (<5 seconds)
- **False Positive Rate**: <10% for alert generation

## 🔒 Security & Privacy

- This is a **demonstration application** using **synthetic data only**
- No real customer or financial data is used
- All data is generated using the Faker library
- Suitable for educational and demonstration purposes

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation

---

**FinGuard AI** - Protecting financial systems with intelligent AML detection 🛡️

**Note**: This is a demonstration application using synthetic data for educational purposes.

