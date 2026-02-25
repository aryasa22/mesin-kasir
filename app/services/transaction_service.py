from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.transaction import Transaction, TransactionItem
from app.models.user import User
from app.schemas.transaction import TransactionCreate


def _generate_invoice_no() -> str:
    return datetime.now().strftime("INV%Y%m%d%H%M%S%f")[:-3]


def create_transaction(db: Session, payload: TransactionCreate, cashier: User) -> Transaction:
    product_ids = [item.product_id for item in payload.items]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    product_map = {product.id: product for product in products}

    tx_items: list[TransactionItem] = []
    total_amount = 0.0

    for item in payload.items:
        product = product_map.get(item.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item.product_id} not found")
        if product.stock_qty < item.qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}",
            )

        subtotal = float(product.selling_price) * item.qty
        total_amount += subtotal

        tx_items.append(
            TransactionItem(
                product_id=product.id,
                product_name=product.name,
                qty=item.qty,
                cost_price=product.cost_price,
                selling_price=product.selling_price,
                subtotal=subtotal,
            )
        )

    if payload.payment_amount < total_amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment amount is less than total")

    transaction = Transaction(
        invoice_no=_generate_invoice_no(),
        cashier_id=cashier.id,
        total_amount=total_amount,
        payment_amount=payload.payment_amount,
        change_amount=payload.payment_amount - total_amount,
        items=tx_items,
    )

    for item in payload.items:
        product_map[item.product_id].stock_qty -= item.qty

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
