from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import List
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

# Enums
class ProductCategory(str, Enum):
    ELECTRONICS = "Electronics"
    BOOKS = "Books"
    CLOTHING = "Clothing"

class LoyaltyLevel(str, Enum):
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    NONE = "None"

# Pydantic Models
class ProductItem(BaseModel):
    id: int
    name: str
    category: ProductCategory
    price: Decimal = Field(..., gt=0, description="Price must be greater than 0")
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")

    @validator('price', pre=True)
    def validate_price(cls, v):
        return Decimal(str(v)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class Customer(BaseModel):
    loyalty_level: LoyaltyLevel = LoyaltyLevel.NONE

class CartRequest(BaseModel):
    items: List[ProductItem]
    customer: Customer

class AddItemRequest(BaseModel):
    item: ProductItem

class UpdateQuantityRequest(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0)

class CartItemBreakdown(BaseModel):
    id: int
    name: str
    category: str
    base_price: Decimal
    quantity: int
    subtotal_before_tax: Decimal
    tax_amount: Decimal
    subtotal_after_tax: Decimal
    item_discount: Decimal
    final_item_total: Decimal

class CartSummary(BaseModel):
    items: List[CartItemBreakdown]
    subtotal: Decimal
    total_tax: Decimal
    item_discounts: Decimal
    bulk_discount: Decimal
    loyalty_discount: Decimal
    final_total: Decimal
    customer_loyalty_level: str

class CartResponse(BaseModel):
    cart_id: str
    summary: CartSummary
    timestamp: 'datetime'
