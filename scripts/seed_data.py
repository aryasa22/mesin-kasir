from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.product import Product
from app.models.user import User


def seed():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", full_name="Administrator", role="admin", hashed_password=hash_password("admin123")))
        if not db.query(User).filter(User.username == "cashier").first():
            db.add(User(username="cashier", full_name="Main Cashier", role="cashier", hashed_password=hash_password("cashier123")))

        if db.query(Product).count() == 0:
            db.add_all([
                Product(barcode="899100001", name="Bottled Water", cost_price=2.00, selling_price=3.00, stock_qty=120),
                Product(barcode="899100002", name="Chocolate Bar", cost_price=1.50, selling_price=2.50, stock_qty=90),
                Product(barcode="899100003", name="Instant Noodles", cost_price=0.70, selling_price=1.20, stock_qty=200),
            ])
        db.commit()
        print("Seed complete")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
