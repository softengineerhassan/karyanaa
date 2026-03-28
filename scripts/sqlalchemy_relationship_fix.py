# ============================================================================
# SECTION A — FINAL CORRECTED SQLALCHEMY MODELS
# ============================================================================

# ----------------------------------------------------------------------------
# 1. Category Model
# ----------------------------------------------------------------------------
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from typing import Optional

if TYPE_CHECKING:
    from app.models.subcategory import SubCategory
    from app.models.venues import Venue

class Category(BaseModel):
    __tablename__ = "categories"

    name_en: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    name_ar: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    name_fr: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    icon: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    color_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    slug: Mapped[str] = mapped_column(String(180), nullable=False, unique=True, index=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_ar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_fr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    subcategories: Mapped[list["SubCategory"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan"
    )
    venues: Mapped[list["Venue"]] = relationship(
        "Venue",
        back_populates="category",
        cascade="all, delete-orphan"
    )


# ----------------------------------------------------------------------------
# 2. SubCategory Model
# ----------------------------------------------------------------------------
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from app.models.base import BaseModel
from typing import Optional

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.venues import Venue

class SubCategory(BaseModel):
    __tablename__ = "subcategories"

    name_en: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    name_ar: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    name_fr: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    # Foreign Keys
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relationships
    category: Mapped["Category"] = relationship(back_populates="subcategories")
    venues: Mapped[list["Venue"]] = relationship("Venue", back_populates="subcategory")


# ----------------------------------------------------------------------------
# 3. Venue Model (Relevant sections only)
# ----------------------------------------------------------------------------
from sqlalchemy import String, Float, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.subcategory import SubCategory
    from app.models.resource import Resource
    from app.models.perk import Perk
    from app.models.pricing import Pricing
    from app.models.user import User
    from app.models.venue_operating_hour import VenueOperatingHour
    from app.models.venue_featured_placement import VenueFeaturedPlacement
    from app.models.venue_payment_method import VenuePaymentMethod
    from app.models.venue_staff_pin import VenueStaffPin

class Venue(BaseModel):
    __tablename__ = "venues"

    # ... (other fields omitted for brevity) ...

    # -------------------------
    # Category & Subcategory
    # -------------------------
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship("Category", back_populates="venues")
    
    subcategory_id: Mapped[UUID] = mapped_column(
        ForeignKey("subcategories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    subcategory: Mapped["SubCategory"] = relationship("SubCategory", back_populates="venues")

    # ... (other fields and relationships) ...


# ============================================================================
# SECTION B — EXPLANATION OF NoForeignKeysError
# ============================================================================

"""
CAUSE:
SubCategory model defined `venues` relationship with back_populates="subcategory",
but Venue model was missing both:
1. subcategory_id column with ForeignKey("subcategories.id")
2. subcategory relationship with back_populates="venues"

SQLAlchemy couldn't establish the join condition because no FK existed in Venue
pointing to SubCategory, even though the database column existed.
"""


# ============================================================================
# SECTION C — VERIFICATION
# ============================================================================

# ----------------------------------------------------------------------------
# Verification Step 1: Confirm Mapper Configuration
# ----------------------------------------------------------------------------
from sqlalchemy.orm import configure_mappers
from app.models.category import Category
from app.models.subcategory import SubCategory
from app.models.venues import Venue

# This will raise an error if relationships are misconfigured
try:
    configure_mappers()
    print("✅ All mappers configured successfully")
except Exception as e:
    print(f"❌ Mapper configuration error: {e}")


# ----------------------------------------------------------------------------
# Verification Step 2: Test Query with selectinload
# ----------------------------------------------------------------------------
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def test_relationships(session):
    """Test bidirectional relationships"""
    
    # Query category with eager-loaded subcategories and venues
    stmt = (
        select(Category)
        .options(
            selectinload(Category.subcategories).selectinload(SubCategory.venues)
        )
        .limit(1)
    )
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    
    if category:
        print(f"Category: {category.name_en}")
        print(f"Subcategories: {len(category.subcategories)}")
        for subcat in category.subcategories:
            print(f"  - {subcat.name_en}: {len(subcat.venues)} venues")
            for venue in subcat.venues:
                # Test reverse relationship
                assert venue.subcategory.id == subcat.id
                assert venue.category.id == category.id
                print(f"    * {venue.name_en}")
        print("✅ All relationships working correctly")
    
    return category


# ----------------------------------------------------------------------------
# Verification Step 3: Test Reverse Navigation
# ----------------------------------------------------------------------------
async def test_reverse_navigation(session):
    """Test navigating from Venue up to Category"""
    
    stmt = (
        select(Venue)
        .options(
            selectinload(Venue.subcategory).selectinload(SubCategory.category)
        )
        .limit(1)
    )
    result = await session.execute(stmt)
    venue = result.scalar_one_or_none()
    
    if venue:
        print(f"Venue: {venue.name_en}")
        print(f"Subcategory: {venue.subcategory.name_en}")
        print(f"Category: {venue.subcategory.category.name_en}")
        print("✅ Reverse navigation working")
    
    return venue
