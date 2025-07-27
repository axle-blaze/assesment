from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException
from models import ProductCategory, LoyaltyLevel, ProductItem, Customer, CartRequest, AddItemRequest, UpdateQuantityRequest, CartItemBreakdown, CartSummary, CartResponse
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaxCalculator:
    """Handles tax calculations for different product categories"""
    TAX_RATES = {
        ProductCategory.ELECTRONICS: Decimal('0.10'),
        ProductCategory.BOOKS: Decimal('0.00'),
        ProductCategory.CLOTHING: Decimal('0.05')
    }
    @classmethod
    def calculate_tax(cls, price: Decimal, category: ProductCategory) -> Decimal:
        tax_rate = cls.TAX_RATES.get(category, Decimal('0.00'))
        return (price * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class DiscountCalculator:
    """Handles all discount calculations"""
    LOYALTY_DISCOUNTS = {
        LoyaltyLevel.BRONZE: Decimal('0.05'),
        LoyaltyLevel.SILVER: Decimal('0.10'),
        LoyaltyLevel.GOLD: Decimal('0.15'),
        LoyaltyLevel.NONE: Decimal('0.00')
    }
    @classmethod
    def calculate_item_discount(cls, item: ProductItem, subtotal_after_tax: Decimal) -> Decimal:
        if item.category == ProductCategory.ELECTRONICS and item.quantity > 2:
            return (subtotal_after_tax * Decimal('0.15')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0.00')
    @classmethod
    def calculate_bulk_discount(cls, cart_total: Decimal) -> Decimal:
        if cart_total > Decimal('200.00'):
            return (cart_total * Decimal('0.10')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0.00')
    @classmethod
    def calculate_loyalty_discount(cls, amount: Decimal, loyalty_level: LoyaltyLevel) -> Decimal:
        discount_rate = cls.LOYALTY_DISCOUNTS.get(loyalty_level, Decimal('0.00'))
        return (amount * discount_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class ShoppingCartService:
    """Main service class for shopping cart operations"""
    def __init__(self):
        self.carts: Dict[str, Dict[str, Any]] = {}


    def create_cart(self, cart_request: CartRequest) -> CartResponse:
        cart_id = str(uuid.uuid4())
        try:
            summary = self._calculate_cart_summary(cart_request.items, cart_request.customer)
            cart_data = {
                'items': {item.id: item for item in cart_request.items},
                'customer': cart_request.customer,
                'summary': summary
            }
            self.carts[cart_id] = cart_data
            logger.info(f"Created cart {cart_id} with {len(cart_request.items)} items")
            return CartResponse(
                cart_id=cart_id,
                summary=summary,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error creating cart: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
        

    def add_item(self, cart_id: str, add_request: AddItemRequest) -> CartResponse:
        if cart_id not in self.carts:
            raise HTTPException(status_code=404, detail="Cart not found")
        try:
            cart = self.carts[cart_id]
            items = cart['items']
            if add_request.item.id in items:
                existing_item = items[add_request.item.id]
                existing_item.quantity += add_request.item.quantity
            else:
                items[add_request.item.id] = add_request.item
            summary = self._calculate_cart_summary(list(items.values()), cart['customer'])
            cart['summary'] = summary
            logger.info(f"Added item {add_request.item.id} to cart {cart_id}")
            return CartResponse(
                cart_id=cart_id,
                summary=summary,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error adding item to cart {cart_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
        

    def remove_item(self, cart_id: str, item_id: int) -> CartResponse:
        if cart_id not in self.carts:
            raise HTTPException(status_code=404, detail="Cart not found")
        try:
            cart = self.carts[cart_id]
            items = cart['items']
            if item_id not in items:
                raise HTTPException(status_code=404, detail="Item not found in cart")
            del items[item_id]
            summary = self._calculate_cart_summary(list(items.values()), cart['customer'])
            cart['summary'] = summary
            logger.info(f"Removed item {item_id} from cart {cart_id}")
            return CartResponse(
                cart_id=cart_id,
                summary=summary,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error removing item from cart {cart_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
        
        
    def update_quantity(self, cart_id: str, update_request: UpdateQuantityRequest) -> CartResponse:
        if cart_id not in self.carts:
            raise HTTPException(status_code=404, detail="Cart not found")
        try:
            cart = self.carts[cart_id]
            items = cart['items']
            if update_request.item_id not in items:
                raise HTTPException(status_code=404, detail="Item not found in cart")
            items[update_request.item_id].quantity = update_request.quantity
            summary = self._calculate_cart_summary(list(items.values()), cart['customer'])
            cart['summary'] = summary
            logger.info(f"Updated item {update_request.item_id} quantity to {update_request.quantity} in cart {cart_id}")
            return CartResponse(
                cart_id=cart_id,
                summary=summary,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error updating item quantity in cart {cart_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
        

    def get_cart(self, cart_id: str) -> Optional[CartResponse]:
        if cart_id not in self.carts:
            return None
        cart = self.carts[cart_id]
        return CartResponse(
            cart_id=cart_id,
            summary=cart['summary'],
            timestamp=datetime.now()
        )
    
    
    def _calculate_cart_summary(self, items: List[ProductItem], customer: Customer) -> CartSummary:
        item_breakdowns = []
        total_before_discounts = Decimal('0.00')
        total_tax = Decimal('0.00')
        total_item_discounts = Decimal('0.00')
        for item in items:
            subtotal_before_tax = item.price * item.quantity
            tax_amount = TaxCalculator.calculate_tax(subtotal_before_tax, item.category)
            subtotal_after_tax = subtotal_before_tax + tax_amount
            item_discount = DiscountCalculator.calculate_item_discount(item, subtotal_after_tax)
            final_item_total = subtotal_after_tax - item_discount
            breakdown = CartItemBreakdown(
                id=item.id,
                name=item.name,
                category=item.category.value,
                base_price=item.price,
                quantity=item.quantity,
                subtotal_before_tax=subtotal_before_tax,
                tax_amount=tax_amount,
                subtotal_after_tax=subtotal_after_tax,
                item_discount=item_discount,
                final_item_total=final_item_total
            )
            item_breakdowns.append(breakdown)
            total_before_discounts += subtotal_after_tax
            total_tax += tax_amount
            total_item_discounts += item_discount
        cart_total_after_item_discounts = total_before_discounts - total_item_discounts
        bulk_discount = DiscountCalculator.calculate_bulk_discount(cart_total_after_item_discounts)
        amount_after_bulk_discount = cart_total_after_item_discounts - bulk_discount
        loyalty_discount = DiscountCalculator.calculate_loyalty_discount(
            amount_after_bulk_discount, customer.loyalty_level
        )
        final_total = amount_after_bulk_discount - loyalty_discount
        return CartSummary(
            items=item_breakdowns,
            subtotal=total_before_discounts,
            total_tax=total_tax,
            item_discounts=total_item_discounts,
            bulk_discount=bulk_discount,
            loyalty_discount=loyalty_discount,
            final_total=final_total,
            customer_loyalty_level=customer.loyalty_level.value
        )
