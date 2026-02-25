from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionRead
from app.schemas.transaction import TransactionCreate
from app.services.print_service import print_transaction_receipt
from app.services.transaction_service import create_transaction

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def _to_read_schema(transaction: Transaction) -> TransactionRead:
    return TransactionRead(
        id=transaction.id,
        invoice_no=transaction.invoice_no,
        total_amount=float(transaction.total_amount),
        payment_amount=float(transaction.payment_amount),
        change_amount=float(transaction.change_amount),
        created_at=transaction.created_at,
        items=[
            {
                "name": item.product_name,
                "qty": item.qty,
                "price": float(item.selling_price),
                "subtotal": float(item.subtotal),
            }
            for item in transaction.items
        ],
    )


@router.post("", response_model=TransactionRead)
def create_pos_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = create_transaction(db, payload, current_user)
    return _to_read_schema(transaction)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return _to_read_schema(transaction)


@router.post("/{transaction_id}/print")
def print_receipt(transaction_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    try:
        print_transaction_receipt(transaction)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Printer error: {exc}") from exc

    return {"message": "Receipt sent to thermal printer"}
