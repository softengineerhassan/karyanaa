import sys
import os
from uuid import UUID

# Add the parent directory to sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import get_db
from app.services.venue_service import VenueService
from app.models.venues import Venue
from app.models.pricing import Pricing, PriceRange
from app.models.category import Category
from app.models.subcategory import SubCategory
from app.models.user import User

from app.core.config import settings

# This is a scratch script for verification
def verify_association():
    # Use the existing database engine or a test one
    try:
        db_url = settings.DATABASE_URL
    except RuntimeError:
        # Fallback for manual run if env vars are not set in the shell
        db_url = "postgresql://OMNIA:ali@localhost:5432/omnia_db"
    
    print(f"Connecting to database: {db_url}")
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 1. Setup - get or create a vendor, category, and subcategory
        vendor = db.query(User).first()
        category = db.query(Category).first()
        subcategory = db.query(SubCategory).first()

        if not all([vendor, category, subcategory]):
            print("Missing setup data (vendor, category, or subcategory). Please ensure they exist.")
            return

        service = VenueService(db)

        # 2. Test Venue Creation with "range" price range
        venue_data = {
            "name_en": "Test Venue Range",
            "name_ar": "Test Venue Range Ar",
            "name_fr": "Test Venue Range Fr",
            "tagline_en": "Best range venue",
            "tagline_ar": "Best range venue ar",
            "tagline_fr": "Best range venue fr",
            "description_en": "A very long description for the test venue range.",
            "description_ar": "A very long description for the test venue range ar.",
            "description_fr": "A very long description for the test venue range fr.",
            "latitude": 24.8607,
            "longitude": 67.0011,
            "address_en": "123 Range St",
            "address_ar": "123 Range St ar",
            "address_fr": "123 Range St fr",
            "phone_number": "+1234567890",
            "email": "range@test.com",
            "category_id": category.id,
            "subcategory_id": subcategory.id,
            "vendor_id": vendor.id,
            "base_price": "range"
        }

        print("Creating venue with 'range' price range...")
        venue = service.create_venue(venue_data, None, None, [])
        db.refresh(venue)

        # 3. Verify Pricing record existence
        pricing = db.query(Pricing).filter(Pricing.venue_id == venue.id).first()
        if pricing:
            print(f"SUCCESS: Pricing record found for venue {venue.id}")
            print(f"Price Range: {pricing.price_range}")
            assert pricing.price_range == PriceRange.RANGE
            assert pricing.average_price_per_person == 0.0
        else:
            print(f"FAILURE: Pricing record NOT found for venue {venue.id}")

        # 4. Test with "luxary" typo
        venue_data_luxury = venue_data.copy()
        venue_data_luxury["name_en"] = "Test Venue Luxury"
        venue_data_luxury["email"] = "luxury@test.com"
        venue_data_luxury["base_price"] = "luxary"

        print("\nCreating venue with 'luxary' price range...")
        venue_lux = service.create_venue(venue_data_luxury, None, None, [])
        db.refresh(venue_lux)

        pricing_lux = db.query(Pricing).filter(Pricing.venue_id == venue_lux.id).first()
        if pricing_lux:
            print(f"SUCCESS: Pricing record found for venue {venue_lux.id}")
            print(f"Price Range: {pricing_lux.price_range}")
            assert pricing_lux.price_range == PriceRange.LUXURY
        else:
            print(f"FAILURE: Pricing record NOT found for venue {venue_lux.id}")

        # Cleanup (optional - can leave for manual check)
        # db.delete(pricing)
        # db.delete(venue)
        # db.delete(pricing_lux)
        # db.delete(venue_lux)
        # db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    verify_association()
