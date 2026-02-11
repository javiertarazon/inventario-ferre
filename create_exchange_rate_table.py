"""
Create exchange_rates table.
"""
from app import create_app
from app.extensions import db
from app.models import ExchangeRate
from datetime import date
from decimal import Decimal

app = create_app()

with app.app_context():
    try:
        print("Creating exchange_rates table...")
        
        # Create table
        db.create_all()
        
        print("✓ Table created successfully")
        
        # Create initial rate for today
        today = date.today()
        existing = ExchangeRate.query.filter_by(date=today).first()
        
        if not existing:
            initial_rate = ExchangeRate(
                date=today,
                rate=Decimal('36.50'),  # Default rate
                created_by=1  # Admin user
            )
            db.session.add(initial_rate)
            db.session.commit()
            print(f"✓ Created initial exchange rate: {initial_rate.rate} Bs/$ for {today}")
        else:
            print(f"✓ Exchange rate already exists for {today}: {existing.rate} Bs/$")
        
        print("\n✅ Exchange rate system ready!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
