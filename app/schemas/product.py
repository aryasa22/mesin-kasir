from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    barcode: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=2, max_length=150)
    cost_price: float = Field(gt=0)
    selling_price: float = Field(gt=0)
    stock_qty: int = Field(ge=0)

    @field_validator("selling_price")
    @classmethod
    def validate_sell_price(cls, value: float, info):
        cost_price = info.data.get("cost_price")
        if cost_price is not None and value < cost_price:
            raise ValueError("Selling price cannot be lower than cost price")
        return value


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    barcode: str | None = Field(default=None, min_length=3, max_length=50)
    name: str | None = Field(default=None, min_length=2, max_length=150)
    cost_price: float | None = Field(default=None, gt=0)
    selling_price: float | None = Field(default=None, gt=0)
    stock_qty: int | None = Field(default=None, ge=0)


class ProductRead(ProductBase):
    id: int
    updated_at: datetime | None

    model_config = {"from_attributes": True}
