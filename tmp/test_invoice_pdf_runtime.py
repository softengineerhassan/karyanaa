from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.sales import Sale
from app.services.sales_service import SalesService


def main() -> None:
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        sale = session.execute(
            select(Sale).where(Sale.deleted_at.is_(None)).order_by(Sale.created_at.desc())
        ).scalars().first()
        print("SALE_ID", sale.id if sale else None)
        if not sale:
            print("NO_SALE_FOUND")
            return

        service = SalesService(session)
        pdf_bytes = service.generate_invoice_pdf(sale.id)
        print("PDF_BYTES", len(pdf_bytes))
        print("PDF_HEADER", pdf_bytes[:5])
    finally:
        session.close()


if __name__ == "__main__":
    main()
