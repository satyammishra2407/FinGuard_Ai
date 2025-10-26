"""
Setup database with sample data for Streamlit Cloud deployment
Run this automatically on first app load
"""
import os
from database import Base, engine
from data_generator import EnhancedDataGenerator

def setup_database():
    """Initialize database with sample data if it doesn't exist"""
    from sqlalchemy import inspect
    
    db_file = "finguard_ai.db"
    
    # Check if database has data
    needs_data = False
    
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Check if database has any customers
        from database import SessionLocal, Customer
        db = SessionLocal()
        customer_count = db.query(Customer).count()
        db.close()
        
        needs_data = (customer_count == 0)
        
        if needs_data:
            print("[INFO] Database is empty, generating sample data...")
            
            # Generate sample data
            try:
                generator = EnhancedDataGenerator()
                generator.populate_database(num_customers=1000, num_transactions_per_customer=50)
                print("[SUCCESS] Sample data generated successfully!")
                print("[SUCCESS] Created 1000 customers with ~50,000 transactions")
            except Exception as e:
                print(f"[ERROR] Error generating sample data: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[INFO] Database already has {customer_count} customers")
        
        print("[SUCCESS] Database setup complete!")
    except Exception as e:
        print(f"[ERROR] Database setup failed: {e}")
        import traceback
        traceback.print_exc()
    
    return True

if __name__ == "__main__":
    setup_database()

