"""
FinGuard AI - Main Streamlit Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import networkx as nx
from pyvis.network import Network
import tempfile
import os

from database import Customer, Transaction, Alert, SessionLocal, create_tables
from detection_algorithms import AMLDetectionEngine
from ml_models import MLRiskAssessment
import config

# Page configuration (MUST be first!)
st.set_page_config(
    page_title="FinGuard AI - AML Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first run (for Streamlit Cloud)
@st.cache_resource
def initialize_database():
    """Initialize database with sample data - runs once per session"""
    try:
        from setup_database import setup_database
        result = setup_database()
        return {"success": True, "message": "Database initialized"}
    except Exception as e:
        import traceback
        error_msg = f"Database setup failed: {e}\n{traceback.format_exc()}"
        return {"success": False, "message": error_msg}

# Run database initialization
db_status = initialize_database()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .risk-high {
        color: #d62728;
        font-weight: bold;
    }
    .risk-medium {
        color: #ff7f0e;
        font-weight: bold;
    }
    .risk-low {
        color: #2ca02c;
        font-weight: bold;
    }
    .risk-critical {
        color: #8b0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_metrics():
    """Load summary metrics efficiently"""
    from database import get_customer_count, get_high_risk_customer_count, get_transaction_count, get_alert_count_by_status
    db = SessionLocal()
    try:
        total_customers = get_customer_count(db)
        high_risk_customers = get_high_risk_customer_count(db, 70)
        total_transactions = get_transaction_count(db)
        pending_alerts = get_alert_count_by_status(db, 'OPEN')
        return total_customers, high_risk_customers, total_transactions, pending_alerts
    finally:
        db.close()

@st.cache_data(ttl=300)
def load_customers_paginated(limit=100, offset=0):
    """Load customers with pagination"""
    from database import get_customers_paginated
    db = SessionLocal()
    try:
        return get_customers_paginated(db, limit, offset)
    finally:
        db.close()

@st.cache_data(ttl=300)
def load_customer_risk_scores():
    """Load only risk scores for distribution chart"""
    db = SessionLocal()
    try:
        return [c.risk_score for c in db.query(Customer.risk_score).all()]
    finally:
        db.close()

@st.cache_data(ttl=300)
def load_recent_alerts(limit=10):
    """Load recent alerts"""
    from database import get_recent_alerts
    db = SessionLocal()
    try:
        return get_recent_alerts(db, limit)
    finally:
        db.close()

def get_db_session():
    """Get database session"""
    return SessionLocal()

def get_risk_color(risk_score):
    """Get color based on risk score"""
    if risk_score >= 80:
        return "risk-critical"
    elif risk_score >= 60:
        return "risk-high"
    elif risk_score >= 30:
        return "risk-medium"
    else:
        return "risk-low"

def create_risk_overview_metrics():
    """Create risk overview metrics"""
    total_customers, high_risk_customers, total_transactions, pending_alerts = load_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Customers",
            value=f"{total_customers:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="High Risk Customers",
            value=f"{high_risk_customers:,}",
            delta=f"{(high_risk_customers/total_customers*100):.1f}%" if total_customers > 0 else "0%"
        )
    
    with col3:
        st.metric(
            label="Pending Alerts",
            value=f"{pending_alerts:,}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Total Transactions",
            value=f"{total_transactions:,}",
            delta=None
        )

def create_risk_distribution_chart():
    """Create risk score distribution chart"""
    risk_scores = load_customer_risk_scores()
    
    fig = px.histogram(
        x=risk_scores,
        nbins=20,
        title="Customer Risk Score Distribution",
        labels={'x': 'Risk Score', 'y': 'Number of Customers'},
        color_discrete_sequence=['#1f77b4']
    )
    
    # Add risk level lines
    fig.add_vline(x=30, line_dash="dash", line_color="orange", annotation_text="Medium Risk")
    fig.add_vline(x=60, line_dash="dash", line_color="red", annotation_text="High Risk")
    fig.add_vline(x=80, line_dash="dash", line_color="darkred", annotation_text="Critical Risk")
    
    fig.update_layout(
        xaxis_title="Risk Score",
        yaxis_title="Number of Customers",
        showlegend=False
    )
    
    return fig

def create_transaction_volume_chart(transactions):
    """Create transaction volume over time chart"""
    if not transactions:
        return None
    
    # Group transactions by date
    df = pd.DataFrame([{
        'date': t.timestamp.date(),
        'amount': t.amount,
        'is_suspicious': t.is_suspicious
    } for t in transactions])
    
    daily_volume = df.groupby('date').agg({
        'amount': 'sum',
        'is_suspicious': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    
    # Add total volume
    fig.add_trace(go.Scatter(
        x=daily_volume['date'],
        y=daily_volume['amount'],
        mode='lines',
        name='Total Volume',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Add suspicious volume
    fig.add_trace(go.Scatter(
        x=daily_volume['date'],
        y=daily_volume['is_suspicious'],
        mode='lines',
        name='Suspicious Volume',
        line=dict(color='#d62728', width=2)
    ))
    
    fig.update_layout(
        title="Daily Transaction Volume",
        xaxis_title="Date",
        yaxis_title="Amount (₹)",
        hovermode='x unified'
    )
    
    return fig

def create_network_visualization():
    """Create network visualization for smurfing detection - optimized version"""
    from database import get_customers_for_network_analysis, get_suspicious_transactions_sample
    
    db = get_db_session()
    try:
        customers = get_customers_for_network_analysis(db, limit=200)
        transactions = get_suspicious_transactions_sample(db, limit=2000)
        
        if not customers or not transactions:
            st.warning("Not enough data for network analysis")
            return None
        
        detection_engine = AMLDetectionEngine()
        smurf_networks = detection_engine.detect_smurfing_network(customers, transactions)
        
        if not smurf_networks:
            st.warning("No smurfing networks detected")
            return None
        
        G = nx.Graph()
        for network in smurf_networks[:3]:
            accounts = network['accounts'][:10]
            for i, account in enumerate(accounts):
                G.add_node(account, risk_score=next((c.risk_score for c in customers if c.customer_id == account), 0), group=1)
                for j in range(i+1, len(accounts)):
                    G.add_edge(account, accounts[j], weight=network['total_volume'])
        
        net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
        
        for node in G.nodes():
            risk_score = G.nodes[node]['risk_score']
            color_class = get_risk_color(risk_score).replace('risk-', '')
            color_map = {'low': '#2ca02c', 'medium': '#ff7f0e', 'high': '#d62728', 'critical': '#8b0000'}
            color = color_map.get(color_class, '#1f77b4')
            net.add_node(node, label=f"{node}\nRisk: {risk_score:.1f}", color=color, size=20)
        
        for edge in G.edges():
            net.add_edge(edge[0], edge[1], width=2)
        
        net.set_options("""{"physics": {"enabled": true, "stabilization": {"iterations": 50}}}""")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w') as tmp:
            tmp_path = tmp.name
        net.save_graph(tmp_path)
        
        try:
            with open(tmp_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        finally:
            try:
                os.unlink(tmp_path)
            except (PermissionError, OSError):
                pass
        
        return html_content
    finally:
        db.close()





def main():
    """Main application function"""
    st.markdown('<h1 class="main-header">🛡️ FinGuard AI - AML Platform</h1>', unsafe_allow_html=True)
    
    # Database status check
    db = SessionLocal()
    try:
        customer_count = db.query(Customer).count()
        
        # Show status banner
        if customer_count == 0:
            st.error("⚠️ **Database is empty!** Click the button below to generate sample data.")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Generate 1000 Customers & Data", type="primary", use_container_width=True):
                    with st.spinner("Generating data... This may take 2-3 minutes..."):
                        try:
                            from data_generator import EnhancedDataGenerator
                            generator = EnhancedDataGenerator()
                            generator.populate_database(num_customers=1000, num_transactions_per_customer=50)
                            st.success("✅ Successfully generated 1000 customers with 50,000 transactions!")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating data: {e}")
                            import traceback
                            st.code(traceback.format_exc())
        else:
            st.success(f"✅ Database loaded: **{customer_count:,} customers** ready!")
    finally:
        db.close()
    
    st.markdown("---")
    
    # Initialize detection engine and ML models
    detection_engine = AMLDetectionEngine()
    ml_models = MLRiskAssessment()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Dashboard", "Customer Search", "Risk Analysis", "Network Analysis", "Alert Management", "ML Models"]
    )
    
    if page == "Dashboard":
        st.header("📊 Risk Overview Dashboard")
        
        # Risk overview metrics (optimized - no data loading needed)
        create_risk_overview_metrics()
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_risk_distribution_chart(), use_container_width=True)
        
        with col2:
            # Load sample transactions for chart
            db = get_db_session()
            try:
                transactions_sample = db.query(Transaction).order_by(Transaction.timestamp.desc()).limit(5000).all()
                if transactions_sample:
                    st.plotly_chart(create_transaction_volume_chart(transactions_sample), use_container_width=True)
            finally:
                db.close()
        
        # Recent alerts
        st.subheader("🚨 Recent Alerts")
        recent_alerts = load_recent_alerts(10)
            
        if recent_alerts:
            db = get_db_session()
            try:
                for alert in recent_alerts:
                    customer = db.query(Customer).filter(Customer.customer_id == alert.customer_id).first()
                    if customer:
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**{customer.name}** - {alert.alert_type}")
                        
                        with col2:
                            st.write(f"Risk: {alert.risk_score:.1f}")
                        
                        with col3:
                            st.write(f"Status: {alert.status}")
                        
                        with col4:
                            st.write(alert.timestamp.strftime("%Y-%m-%d %H:%M"))
            finally:
                db.close()
        else:
            st.info("No alerts found")

    
    elif page == "Customer Search":
        st.header("🔍 Customer Search & Profile")
        
        # Search functionality
        search_term = st.text_input("Search by Customer ID or Name")
        
        db = get_db_session()
        try:
            if search_term:
                filtered_customers = db.query(Customer).filter(
                    (Customer.customer_id.ilike(f"%{search_term}%")) | 
                    (Customer.name.ilike(f"%{search_term}%"))
                ).limit(100).all()
            else:
                # Use pagination for all customers
                page_num = st.number_input("Page", min_value=1, value=1, step=1)
                per_page = 50
                offset = (page_num - 1) * per_page
                filtered_customers = load_customers_paginated(limit=per_page, offset=offset)
            
            if filtered_customers:
                # Customer selection
                customer_options = {f"{c.name} ({c.customer_id})": c for c in filtered_customers}
                selected_customer_name = st.selectbox("Select Customer", list(customer_options.keys()))
                selected_customer = customer_options[selected_customer_name]
                
                # Customer profile
                st.subheader(f"👤 Customer Profile: {selected_customer.name}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Customer ID", selected_customer.customer_id)
                    st.metric("Declared Income", f"₹{selected_customer.declared_income:,.2f}")
                    st.metric("Occupation", selected_customer.occupation)
                
                with col2:
                    st.metric("KYC Status", selected_customer.kyc_status)
                    st.metric("Account Opening Date", selected_customer.account_opening_date.strftime("%Y-%m-%d"))
                    st.metric("Risk Score", f"{selected_customer.risk_score:.1f}")
                
                with col3:
                    risk_class = get_risk_color(selected_customer.risk_score)
                    st.markdown(f"<div class='{risk_class}'>Risk Level: {risk_class.replace('risk-', '').upper()}</div>", 
                               unsafe_allow_html=True)
                
                # Customer transactions - load only for selected customer
                from database import get_customer_transactions
                customer_transactions = get_customer_transactions(db, selected_customer.customer_id, limit=100)
                
                if customer_transactions:
                    st.subheader("💳 Transaction History")
                    
                    # Transaction summary
                    total_amount = sum(t.amount for t in customer_transactions)
                    suspicious_count = len([t for t in customer_transactions if t.is_suspicious])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Transactions", len(customer_transactions))
                    with col2:
                        st.metric("Total Amount", f"₹{total_amount:,.2f}")
                    with col3:
                        st.metric("Suspicious Transactions", suspicious_count)
                    
                    # Risk analysis
                    st.subheader("🔍 Risk Analysis")
                    risk_report = detection_engine.generate_risk_report(selected_customer, customer_transactions)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Risk Factors:**")
                        for factor in risk_report['risk_factors']:
                            st.write(f"• {factor}")
                    
                    with col2:
                        st.write("**Detected Patterns:**")
                        for pattern, detected in risk_report['patterns'].items():
                            status = "✅" if detected else "❌"
                            st.write(f"{status} {pattern.replace('_', ' ').title()}")
                    
                    # Transaction table
                    st.subheader("📋 Recent Transactions")
                    transaction_df = pd.DataFrame([{
                        'Date': t.timestamp.strftime("%Y-%m-%d %H:%M"),
                        'Amount': f"₹{t.amount:,.2f}",
                        'Type': t.transaction_type,
                        'Beneficiary': t.beneficiary,
                        'Status': t.status,
                        'Suspicious': "⚠️" if t.is_suspicious else "✅"
                    } for t in sorted(customer_transactions, key=lambda x: x.timestamp, reverse=True)[:20]])
                    
                    st.dataframe(transaction_df, use_container_width=True)
                else:
                    st.info("No transactions found for this customer")
            else:
                st.warning("No customers found matching the search criteria")
        finally:
            db.close()

    
    
    elif page == "Risk Analysis":
        st.header("📈 Advanced Risk Analysis")
        
        # Risk analysis options
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Risk Score Distribution", "Transaction Patterns", "Behavioral Analysis", "Anomaly Detection"]
        )
        
        if analysis_type == "Risk Score Distribution":
            st.plotly_chart(create_risk_distribution_chart(), use_container_width=True)
            
            # Risk statistics
            risk_scores = load_customer_risk_scores()
            st.subheader("Risk Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean Risk Score", f"{np.mean(risk_scores):.2f}")
            with col2:
                st.metric("Median Risk Score", f"{np.median(risk_scores):.2f}")
            with col3:
                st.metric("Std Deviation", f"{np.std(risk_scores):.2f}")
            with col4:
                st.metric("Max Risk Score", f"{np.max(risk_scores):.2f}")
        
        elif analysis_type == "Transaction Patterns":
            # Load sample transactions for analysis
            db = get_db_session()
            try:
                transactions_sample = db.query(Transaction).limit(10000).all()
                
                if transactions_sample:
                    # Transaction type distribution
                    transaction_types = [t.transaction_type for t in transactions_sample]
                    type_counts = pd.Series(transaction_types).value_counts()
                    
                    fig = px.pie(
                        values=type_counts.values,
                        names=type_counts.index,
                        title="Transaction Type Distribution (Sample)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Amount distribution
                    amounts = [t.amount for t in transactions_sample]
                    fig = px.histogram(
                        x=amounts,
                        nbins=50,
                        title="Transaction Amount Distribution (Sample)",
                        labels={'x': 'Amount (₹)', 'y': 'Frequency'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No transaction data available")
            finally:
                db.close()
        
        elif analysis_type == "Behavioral Analysis":
            st.subheader("🔍 Customer Behavioral Analysis")
            
            db = get_db_session()
            try:
                # Load sample data for behavioral analysis
                customers_sample = db.query(Customer).limit(500).all()
                transactions_sample = db.query(Transaction).limit(20000).all()
                
                if customers_sample and transactions_sample:
                    # 1. Transaction Timing Analysis
                    st.subheader("⏰ Transaction Timing Patterns")
                    
                    st.info("💡 **What this shows:** When customers make transactions. Suspicious activity often happens outside business hours (10 PM - 6 AM).")
                    
                    # Categorize transactions by time period
                    time_periods = {
                        'Early Morning\n(12 AM - 6 AM)': [],
                        'Morning\n(6 AM - 12 PM)': [],
                        'Afternoon\n(12 PM - 6 PM)': [],
                        'Evening\n(6 PM - 10 PM)': [],
                        'Night\n(10 PM - 12 AM)': []
                    }
                    
                    # Color mapping for risk levels
                    period_colors = {
                        'Early Morning\n(12 AM - 6 AM)': '#d62728',  # Red - High Risk
                        'Morning\n(6 AM - 12 PM)': '#2ca02c',        # Green - Safe
                        'Afternoon\n(12 PM - 6 PM)': '#2ca02c',      # Green - Safe
                        'Evening\n(6 PM - 10 PM)': '#ff7f0e',        # Orange - Medium
                        'Night\n(10 PM - 12 AM)': '#d62728'          # Red - High Risk
                    }
                    
                    for txn in transactions_sample:
                        hour = txn.timestamp.hour
                        if 0 <= hour < 6:
                            time_periods['Early Morning\n(12 AM - 6 AM)'].append(txn)
                        elif 6 <= hour < 12:
                            time_periods['Morning\n(6 AM - 12 PM)'].append(txn)
                        elif 12 <= hour < 18:
                            time_periods['Afternoon\n(12 PM - 6 PM)'].append(txn)
                        elif 18 <= hour < 22:
                            time_periods['Evening\n(6 PM - 10 PM)'].append(txn)
                        else:  # 22-24
                            time_periods['Night\n(10 PM - 12 AM)'].append(txn)
                    
                    # Create data for chart
                    periods = list(time_periods.keys())
                    counts = [len(time_periods[p]) for p in periods]
                    colors = [period_colors[p] for p in periods]
                    
                    # Create professional bar chart
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=periods,
                        y=counts,
                        marker_color=colors,
                        text=counts,
                        textposition='outside',
                        texttemplate='%{text:,} txns',
                        hovertemplate='<b>%{x}</b><br>Transactions: %{y:,}<br><extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title={
                            'text': "Transaction Distribution by Time Period",
                            'font': {'size': 20}
                        },
                        xaxis_title="Time Period",
                        yaxis_title="Number of Transactions",
                        showlegend=False,
                        height=450,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Risk Analysis
                    suspicious_hours = len(time_periods['Early Morning\n(12 AM - 6 AM)']) + len(time_periods['Night\n(10 PM - 12 AM)'])
                    business_hours = len(time_periods['Morning\n(6 AM - 12 PM)']) + len(time_periods['Afternoon\n(12 PM - 6 PM)'])
                    suspicious_percentage = (suspicious_hours / len(transactions_sample)) * 100
                    business_percentage = (business_hours / len(transactions_sample)) * 100
                    
                    st.markdown("### 📊 Time Period Analysis")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(
                            "🟢 Business Hours", 
                            f"{business_hours:,}",
                            delta=f"{business_percentage:.1f}%"
                        )
                    with col2:
                        st.metric(
                            "🔴 Suspicious Hours", 
                            f"{suspicious_hours:,}",
                            delta=f"{suspicious_percentage:.1f}%",
                            delta_color="inverse"
                        )
                    with col3:
                        if suspicious_percentage > 20:
                            risk_status = "🔴 HIGH RISK"
                            risk_color = "red"
                        elif suspicious_percentage > 10:
                            risk_status = "🟡 MEDIUM"
                            risk_color = "orange"
                        else:
                            risk_status = "🟢 NORMAL"
                            risk_color = "green"
                        st.metric("Risk Status", risk_status)
                    with col4:
                        peak_period = max(time_periods.items(), key=lambda x: len(x[1]))[0]
                        st.metric("Peak Period", peak_period.replace('\n', ' '))
                    
                    # Explanation box
                    st.markdown("""
                    **🔍 Understanding the Chart:**
                    - **🟢 Green bars** (Morning, Afternoon): Normal business hours - Low risk
                    - **🟠 Orange bar** (Evening): Transitional period - Medium risk
                    - **🔴 Red bars** (Early Morning, Night): Outside business hours - High risk for suspicious activity
                    
                    **⚠️ Why it matters:**
                    Legitimate business transactions typically happen during 6 AM - 6 PM. 
                    High activity during 10 PM - 6 AM may indicate money laundering attempts.
                    """)
                    
                    st.markdown("---")
                    
                    # 2. Transaction Velocity Analysis
                    st.subheader("🚀 Transaction Velocity Analysis")
                    
                    # Group by customer and analyze frequency
                    customer_txn_counts = {}
                    for txn in transactions_sample:
                        customer_txn_counts[txn.customer_id] = customer_txn_counts.get(txn.customer_id, 0) + 1
                    
                    velocity_data = list(customer_txn_counts.values())
                    
                    fig = px.histogram(
                        x=velocity_data,
                        nbins=30,
                        title="Customer Transaction Frequency Distribution",
                        labels={'x': 'Number of Transactions', 'y': 'Number of Customers'},
                        color_discrete_sequence=['#1f77b4']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Velocity statistics
                    avg_velocity = np.mean(velocity_data)
                    high_velocity_customers = len([v for v in velocity_data if v > avg_velocity * 2])
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Avg Transactions", f"{avg_velocity:.1f}")
                    with col2:
                        st.metric("Max Transactions", f"{max(velocity_data)}")
                    with col3:
                        st.metric("High Velocity Customers", high_velocity_customers)
                    with col4:
                        risk = "🔴 Monitor" if high_velocity_customers > 20 else "🟢 Normal"
                        st.metric("Risk Level", risk)
                    
                    st.markdown("---")
                    
                    # 3. Beneficiary Pattern Analysis
                    st.subheader("👥 Beneficiary Patterns")
                    
                    beneficiaries = [t.beneficiary for t in transactions_sample if t.beneficiary]
                    if beneficiaries:
                        # Find most common beneficiaries
                        beneficiary_counts = pd.Series(beneficiaries).value_counts().head(10)
                        
                        fig = px.bar(
                            x=beneficiary_counts.values,
                            y=beneficiary_counts.index,
                            orientation='h',
                            title="Top 10 Beneficiaries",
                            labels={'x': 'Transaction Count', 'y': 'Beneficiary'},
                            color=beneficiary_counts.values,
                            color_continuous_scale='Reds'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Shared beneficiary analysis
                        shared_beneficiaries = [b for b, count in beneficiary_counts.items() if count >= 5]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total Unique Beneficiaries", len(set(beneficiaries)))
                        with col2:
                            st.metric("Shared Beneficiaries (5+ txns)", len(shared_beneficiaries))
                        
                        if len(shared_beneficiaries) > 10:
                            st.warning("⚠️ High number of shared beneficiaries detected - potential smurfing network!")
                    
                    st.markdown("---")
                    
                    # 4. Geographic Analysis
                    st.subheader("🌍 Geographic Pattern Analysis")
                    
                    locations = [t.location for t in transactions_sample if t.location]
                    if locations:
                        location_counts = pd.Series(locations).value_counts()
                        
                        fig = px.pie(
                            values=location_counts.values,
                            names=location_counts.index,
                            title="Transaction Distribution by Location"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Unique Locations", len(location_counts))
                        with col2:
                            st.metric("Most Active Location", location_counts.index[0])
                    
                else:
                    st.info("No data available for behavioral analysis")
            finally:
                db.close()
        
        elif analysis_type == "Anomaly Detection":
            st.subheader("🎯 Anomaly Detection Analysis")
            
            db = get_db_session()
            try:
                # Load transaction data
                transactions_sample = db.query(Transaction).order_by(Transaction.timestamp.desc()).limit(10000).all()
                
                if transactions_sample:
                    # 1. Amount-based Anomaly Detection
                    st.subheader("💰 Amount-based Anomalies")
                    
                    amounts = [t.amount for t in transactions_sample]
                    mean_amount = np.mean(amounts)
                    std_amount = np.std(amounts)
                    
                    # Define anomalies as transactions > 3 standard deviations
                    threshold = mean_amount + (3 * std_amount)
                    anomalies = [t for t in transactions_sample if t.amount > threshold]
                    
                    # Visualization
                    fig = px.scatter(
                        x=list(range(len(amounts))),
                        y=amounts,
                        title="Transaction Amounts with Anomaly Threshold",
                        labels={'x': 'Transaction Index', 'y': 'Amount (₹)'},
                        color=['Anomaly' if a > threshold else 'Normal' for a in amounts],
                        color_discrete_map={'Normal': '#1f77b4', 'Anomaly': '#d62728'}
                    )
                    fig.add_hline(y=threshold, line_dash="dash", line_color="red", 
                                 annotation_text=f"Anomaly Threshold: ₹{threshold:,.0f}")
                    fig.add_hline(y=mean_amount, line_dash="dash", line_color="green",
                                 annotation_text=f"Mean: ₹{mean_amount:,.0f}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Mean Amount", f"₹{mean_amount:,.0f}")
                    with col2:
                        st.metric("Std Deviation", f"₹{std_amount:,.0f}")
                    with col3:
                        st.metric("Anomalies Detected", len(anomalies))
                    with col4:
                        anomaly_pct = (len(anomalies) / len(transactions_sample)) * 100
                        st.metric("Anomaly Rate", f"{anomaly_pct:.2f}%")
                    
                    st.markdown("---")
                    
                    # 2. Time-based Anomaly Detection
                    st.subheader("⏱️ Time-based Anomalies")
                    
                    # Detect rapid consecutive transactions
                    suspicious_patterns = []
                    customer_transactions = {}
                    
                    for txn in transactions_sample:
                        if txn.customer_id not in customer_transactions:
                            customer_transactions[txn.customer_id] = []
                        customer_transactions[txn.customer_id].append(txn)
                    
                    # Check for rapid transactions (< 5 minutes apart)
                    rapid_txns = 0
                    for customer_id, txns in customer_transactions.items():
                        if len(txns) >= 2:
                            sorted_txns = sorted(txns, key=lambda x: x.timestamp)
                            for i in range(len(sorted_txns) - 1):
                                time_diff = (sorted_txns[i+1].timestamp - sorted_txns[i].timestamp).total_seconds() / 60
                                if time_diff < 5:
                                    rapid_txns += 1
                                    suspicious_patterns.append({
                                        'customer_id': customer_id,
                                        'time_diff': time_diff,
                                        'amount1': sorted_txns[i].amount,
                                        'amount2': sorted_txns[i+1].amount
                                    })
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rapid Transactions", rapid_txns)
                    with col2:
                        st.metric("Customers with Pattern", len(set([p['customer_id'] for p in suspicious_patterns])))
                    with col3:
                        status = "🔴 High Risk" if rapid_txns > 50 else "🟢 Normal"
                        st.metric("Status", status)
                    
                    if suspicious_patterns[:5]:
                        st.write("**Sample Rapid Transaction Patterns:**")
                        pattern_df = pd.DataFrame(suspicious_patterns[:5])
                        pattern_df['time_diff'] = pattern_df['time_diff'].round(2)
                        st.dataframe(pattern_df, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # 3. Structuring Detection
                    st.subheader("📊 Structuring Pattern Detection")
                    
                    # Detect multiple transactions just below threshold
                    threshold_amount = 900000  # ₹9 lakhs
                    below_threshold = [t for t in transactions_sample if 700000 <= t.amount < threshold_amount]
                    
                    # Group by customer and date
                    daily_structuring = {}
                    for txn in below_threshold:
                        date = txn.timestamp.date()
                        key = f"{txn.customer_id}_{date}"
                        if key not in daily_structuring:
                            daily_structuring[key] = []
                        daily_structuring[key].append(txn.amount)
                    
                    # Find suspicious structuring (3+ txns same day below threshold)
                    structuring_cases = {k: v for k, v in daily_structuring.items() if len(v) >= 3}
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Transactions Near Threshold", len(below_threshold))
                    with col2:
                        st.metric("Potential Structuring Cases", len(structuring_cases))
                    with col3:
                        status = "🔴 Alert" if len(structuring_cases) > 5 else "🟢 Normal"
                        st.metric("Status", status)
                    
                    if structuring_cases:
                        st.warning(f"⚠️ {len(structuring_cases)} potential structuring cases detected!")
                        
                        # Show details of structuring cases
                        structuring_details = []
                        for key, amounts in list(structuring_cases.items())[:5]:
                            customer_id, date = key.split('_')
                            structuring_details.append({
                                'Customer ID': customer_id,
                                'Date': date,
                                'Transactions': len(amounts),
                                'Total Amount': f"₹{sum(amounts):,.0f}",
                                'Avg Amount': f"₹{np.mean(amounts):,.0f}"
                            })
                        
                        st.write("**Top Structuring Cases:**")
                        st.dataframe(pd.DataFrame(structuring_details), use_container_width=True)
                    
                    st.markdown("---")
                    
                    # 4. Summary & Recommendations
                    st.subheader("📋 Anomaly Summary & Recommendations")
                    
                    total_anomalies = len(anomalies) + rapid_txns + len(structuring_cases)
                    risk_level = "🔴 HIGH" if total_anomalies > 100 else "🟡 MEDIUM" if total_anomalies > 50 else "🟢 LOW"
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Anomalies Detected", total_anomalies)
                        st.metric("Overall Risk Level", risk_level)
                    
                    with col2:
                        st.write("**Recommendations:**")
                        if len(anomalies) > 20:
                            st.write("• Review high-value transactions")
                        if rapid_txns > 50:
                            st.write("• Investigate rapid transaction patterns")
                        if len(structuring_cases) > 5:
                            st.write("• Flag potential structuring cases for AML review")
                        if total_anomalies < 50:
                            st.write("• ✅ Transaction patterns appear normal")
                
                else:
                    st.info("No transaction data available for anomaly detection")
            finally:
                db.close()
    
    elif page == "Network Analysis":
        st.header("🕸️ Network Analysis & Smurfing Detection")
        
        st.info("Network analysis uses a sample of high-risk customers and suspicious transactions for optimal performance.")
        
        if st.button("Analyze Networks"):
            with st.spinner("Analyzing transaction networks..."):
                html_content = create_network_visualization()
                
                if html_content:
                    st.components.v1.html(html_content, height=600)
                else:
                    st.info("No suspicious networks detected")
    
    elif page == "Alert Management":
        st.header("🚨 Alert Management")
        
        db = get_db_session()
        try:
            # Load alerts with filters
            status_filter = st.selectbox("Filter by Status", ["All", "OPEN", "INVESTIGATING", "RESOLVED"], key="status_filter_top")
            
            query = db.query(Alert)
            if status_filter != "All":
                query = query.filter(Alert.status == status_filter)
            
            alerts = query.order_by(Alert.timestamp.desc()).limit(100).all()
            
            if alerts:
                # Display alerts
                st.write(f"Showing {len(alerts)} most recent alerts")
                
                for alert in alerts:
                    customer = db.query(Customer).filter(Customer.customer_id == alert.customer_id).first()
                    
                    with st.expander(f"Alert {alert.alert_id} - {customer.name if customer else 'Unknown Customer'}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Customer:** {customer.name if customer else 'Unknown'}")
                            st.write(f"**Alert Type:** {alert.alert_type}")
                            st.write(f"**Risk Score:** {alert.risk_score:.1f}")
                            st.write(f"**Status:** {alert.status}")
                        
                        with col2:
                            st.write(f"**Timestamp:** {alert.timestamp.strftime('%Y-%m-%d %H:%M')}")
                            st.write(f"**Assigned Analyst:** {alert.assigned_analyst or 'Unassigned'}")
                            st.write(f"**Triggered Rules:** {alert.triggered_rules}")
                        
                        if alert.investigation_notes:
                            st.write(f"**Investigation Notes:** {alert.investigation_notes}")
                        
                        # Action buttons
                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                        with btn_col1:
                            if st.button(f"Assign to Analyst", key=f"assign_{alert.alert_id}"):
                                st.success("Alert assigned!")
                        with btn_col2:
                            if st.button(f"Mark as Investigating", key=f"investigate_{alert.alert_id}"):
                                st.success("Alert status updated!")
                        with btn_col3:
                            if st.button(f"Resolve Alert", key=f"resolve_{alert.alert_id}"):
                                st.success("Alert resolved!")
            else:
                st.info("No alerts found")
        finally:
            db.close()

    
    elif page == "ML Models":
        st.header("🤖 Machine Learning Models")
        
        st.subheader("Model Training")
        st.info("Model training uses optimized data samples for faster performance.")
        
        if st.button("Train Risk Classification Model"):
            with st.spinner("Training models..."):
                db = get_db_session()
                try:
                    # Load sample data for training
                    customers_sample = db.query(Customer).limit(1000).all()
                    transactions_sample = db.query(Transaction).limit(10000).all()
                    best_model = ml_models.train_risk_classification_model(customers_sample, transactions_sample)
                    st.success(f"Model training completed! Best model: {best_model}")
                finally:
                    db.close()
        
        if st.button("Train Transaction Anomaly Model"):
            with st.spinner("Training transaction anomaly model..."):
                db = get_db_session()
                try:
                    transactions_sample = db.query(Transaction).limit(10000).all()
                    ml_models.train_transaction_anomaly_model(transactions_sample)
                    st.success("Transaction anomaly model training completed!")
                finally:
                    db.close()
        
        # Model performance
        performance = ml_models.get_model_performance()
        if performance:
            st.subheader("Model Performance")
            
            for model_name, metrics in performance.items():
                st.write(f"**{model_name.replace('_', ' ').title()}:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Train Score", f"{metrics['train_score']:.4f}")
                with col2:
                    st.metric("Test Score", f"{metrics['test_score']:.4f}")
                st.markdown("---")

if __name__ == "__main__":
    # Initialize database
    create_tables()
    main()
