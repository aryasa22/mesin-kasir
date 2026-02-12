from datetime import datetime

from pydantic import BaseModel, Field


class TransactionItemCreate(BaseModel):
    product_id: int
    qty: int = Field(gt=0)


class TransactionCreate(BaseModel):
    items: list[TransactionItemCreate] = Field(min_length=1)
    payment_amount: float = Field(gt=0)


class ReceiptItem(BaseModel):
    name: str
    qty: int
    price: float
    subtotal: float


class TransactionRead(BaseModel):
    id: int
    invoice_no: str
    total_amount: float
    payment_amount: float
    change_amount: float
    created_at: datetime
    items: list[ReceiptItem]


class ReportSummary(BaseModel):
    period: str
    total_transactions: int
    total_revenue: float
    total_cost: float
    gross_profit: float
