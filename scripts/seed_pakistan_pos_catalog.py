from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import sys

# Ensure project root is importable when running this script directly.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.inventory import Category, Product, Unit


def to_slug(value: str) -> str:
    return "-".join(value.strip().lower().split())


def ensure_unit(session, name: str, symbol: str, description: str = "") -> Unit:
    unit = session.execute(
        select(Unit).where(Unit.symbol == symbol, Unit.deleted_at.is_(None))
    ).scalar_one_or_none()
    if unit:
        return unit

    unit = Unit(name=name, symbol=symbol, description=description, is_active=True)
    session.add(unit)
    session.flush()
    return unit


def ensure_category(session, name: str, description: str = "") -> Category:
    slug = to_slug(name)
    category = session.execute(
        select(Category).where(Category.slug == slug, Category.deleted_at.is_(None))
    ).scalar_one_or_none()
    if category:
        return category

    category = Category(
        name=name,
        slug=slug,
        description=description or f"{name} products",
        is_active=True,
    )
    session.add(category)
    session.flush()
    return category


def ensure_product(session, payload: dict, category_map: dict[str, Category], unit_map: dict[str, Unit]) -> bool:
    sku = payload["sku"]
    existing = session.execute(
        select(Product).where(Product.sku == sku, Product.deleted_at.is_(None))
    ).scalar_one_or_none()
    if existing:
        return False

    category = category_map[payload["category"]]
    unit = unit_map[payload["unit"]]

    product = Product(
        name=payload["name"],
        slug=to_slug(payload["name"]),
        sku=sku,
        barcode=payload.get("barcode"),
        category_id=category.id,
        unit_id=unit.id,
        purchase_unit_id=unit.id,
        sales_unit_id=unit.id,
        product_type="stockable",
        track_inventory=True,
        has_expiry=payload.get("has_expiry", False),
        has_batch=payload.get("has_batch", False),
        minimum_stock_alert=Decimal(str(payload.get("minimum_stock_alert", "5"))),
        default_purchase_price=Decimal(str(payload["purchase_price"])),
        default_selling_price=Decimal(str(payload["selling_price"])),
        tax_percent=Decimal(str(payload.get("tax_percent", "0"))),
        description=payload.get("description", ""),
        image_url=None,
        is_active=True,
    )
    session.add(product)
    session.flush()
    return True


def main() -> None:
    categories_data = [
        ("Atta & Flour", "Wheat flour, maida and baking flour"),
        ("Rice & Pulses", "Basmati rice, lentils and beans"),
        ("Spices & Masala", "Everyday Pakistani spice essentials"),
        ("Cooking Oil & Ghee", "Oils and desi ghee"),
        ("Tea & Beverages", "Tea, sharbat and drinks"),
        ("Dairy & Breakfast", "Milk, butter, eggs and breakfast items"),
        ("Snacks & Biscuits", "Chips, nimko and biscuits"),
        ("Sugar & Sweeteners", "Sugar and sweetener products"),
        ("Personal Care", "Soap, shampoo and hygiene"),
        ("Home Care", "Detergents and cleaning supplies"),
    ]

    units_data = [
        ("Piece", "pc", "Single sale unit"),
        ("Kilogram", "kg", "Weight in kilograms"),
        ("Gram", "g", "Weight in grams"),
        ("Litre", "l", "Volume in litres"),
        ("Millilitre", "ml", "Volume in millilitres"),
        ("Pack", "pack", "Packaged quantity"),
        ("Dozen", "dozen", "Dozen quantity"),
    ]

    products_data = [
        {"name": "Atta Chakki 10kg", "sku": "PK-ATTA-10KG", "barcode": "8961001000010", "category": "Atta & Flour", "unit": "kg", "purchase_price": "1250", "selling_price": "1390", "minimum_stock_alert": "8"},
        {"name": "Maida Fine 1kg", "sku": "PK-MAIDA-1KG", "barcode": "8961001000011", "category": "Atta & Flour", "unit": "kg", "purchase_price": "155", "selling_price": "180", "minimum_stock_alert": "12"},
        {"name": "Basmati Rice Super 5kg", "sku": "PK-RICE-5KG", "barcode": "8961001000012", "category": "Rice & Pulses", "unit": "kg", "purchase_price": "1280", "selling_price": "1490", "minimum_stock_alert": "6"},
        {"name": "Daal Chana 1kg", "sku": "PK-DAAL-CHANA-1KG", "barcode": "8961001000013", "category": "Rice & Pulses", "unit": "kg", "purchase_price": "305", "selling_price": "355", "minimum_stock_alert": "10"},
        {"name": "Red Chilli Powder 200g", "sku": "PK-MASALA-RC-200G", "barcode": "8961001000014", "category": "Spices & Masala", "unit": "g", "purchase_price": "115", "selling_price": "145", "minimum_stock_alert": "15"},
        {"name": "Turmeric Powder 200g", "sku": "PK-MASALA-HALDI-200G", "barcode": "8961001000015", "category": "Spices & Masala", "unit": "g", "purchase_price": "95", "selling_price": "125", "minimum_stock_alert": "15"},
        {"name": "Cooking Oil Canola 5L", "sku": "PK-OIL-CANOLA-5L", "barcode": "8961001000016", "category": "Cooking Oil & Ghee", "unit": "l", "purchase_price": "2290", "selling_price": "2590", "minimum_stock_alert": "5"},
        {"name": "Desi Ghee 1kg", "sku": "PK-GHEE-1KG", "barcode": "8961001000017", "category": "Cooking Oil & Ghee", "unit": "kg", "purchase_price": "710", "selling_price": "840", "minimum_stock_alert": "8"},
        {"name": "Black Tea Danedar 900g", "sku": "PK-TEA-900G", "barcode": "8961001000018", "category": "Tea & Beverages", "unit": "g", "purchase_price": "1140", "selling_price": "1290", "minimum_stock_alert": "7"},
        {"name": "Rooh Afza 800ml", "sku": "PK-SHARBAT-800ML", "barcode": "8961001000019", "category": "Tea & Beverages", "unit": "ml", "purchase_price": "300", "selling_price": "360", "minimum_stock_alert": "10"},
        {"name": "UHT Milk 1L", "sku": "PK-MILK-1L", "barcode": "8961001000020", "category": "Dairy & Breakfast", "unit": "l", "purchase_price": "248", "selling_price": "295", "minimum_stock_alert": "18", "has_expiry": True},
        {"name": "Eggs Farm Dozen", "sku": "PK-EGGS-DOZEN", "barcode": "8961001000021", "category": "Dairy & Breakfast", "unit": "dozen", "purchase_price": "320", "selling_price": "380", "minimum_stock_alert": "10", "has_expiry": True},
        {"name": "Biscuits Gluco Pack", "sku": "PK-BISCUIT-GLUCO", "barcode": "8961001000022", "category": "Snacks & Biscuits", "unit": "pack", "purchase_price": "24", "selling_price": "30", "minimum_stock_alert": "40"},
        {"name": "Potato Chips Masala 65g", "sku": "PK-CHIPS-MASALA-65G", "barcode": "8961001000023", "category": "Snacks & Biscuits", "unit": "pack", "purchase_price": "42", "selling_price": "55", "minimum_stock_alert": "30"},
        {"name": "Sugar Premium 1kg", "sku": "PK-SUGAR-1KG", "barcode": "8961001000024", "category": "Sugar & Sweeteners", "unit": "kg", "purchase_price": "155", "selling_price": "180", "minimum_stock_alert": "20"},
        {"name": "Shampoo Anti Dandruff 360ml", "sku": "PK-SHAMPOO-360ML", "barcode": "8961001000025", "category": "Personal Care", "unit": "ml", "purchase_price": "460", "selling_price": "550", "minimum_stock_alert": "8"},
        {"name": "Bath Soap Lime 130g", "sku": "PK-SOAP-LIME-130G", "barcode": "8961001000026", "category": "Personal Care", "unit": "pc", "purchase_price": "75", "selling_price": "95", "minimum_stock_alert": "35"},
        {"name": "Washing Powder 1kg", "sku": "PK-DETERGENT-1KG", "barcode": "8961001000027", "category": "Home Care", "unit": "kg", "purchase_price": "380", "selling_price": "460", "minimum_stock_alert": "12"},
        {"name": "Dishwash Liquid 500ml", "sku": "PK-DISHWASH-500ML", "barcode": "8961001000028", "category": "Home Care", "unit": "ml", "purchase_price": "165", "selling_price": "210", "minimum_stock_alert": "15"},
    ]

    session = SessionLocal()
    try:
        unit_map = {}
        for name, symbol, description in units_data:
            unit_map[symbol] = ensure_unit(session, name=name, symbol=symbol, description=description)

        category_map = {}
        for category_name, description in categories_data:
            category_map[category_name] = ensure_category(session, name=category_name, description=description)

        created_products = 0
        for product in products_data:
            if ensure_product(session, product, category_map, unit_map):
                created_products += 1

        session.commit()

        print("Pakistan POS catalog seeding completed successfully.")
        print(f"Categories available: {len(category_map)}")
        print(f"Units available: {len(unit_map)}")
        print(f"New products inserted: {created_products}")
        print(f"Products processed: {len(products_data)}")
    except Exception as exc:
        session.rollback()
        print(f"Seeding failed: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
