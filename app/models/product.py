from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    barcode: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    cost_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    selling_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    stock_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
