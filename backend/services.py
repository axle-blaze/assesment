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

# Business Logic Classes
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
        """Apply item-specific discounts (Electronics 15% off if quantity > 2)"""
        if item.category == ProductCategory.ELECTRONICS and item.quantity > 2:
            return (subtotal_after_tax * Decimal('0.15')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0.00')
    
    @classmethod
    def calculate_bulk_discount(cls, cart_total: Decimal) -> Decimal:
        """Apply bulk discount (10% off if total > $200)"""
        if cart_total > Decimal('200.00'):
            return (cart_total * Decimal('0.10')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0.00')
    
    @classmethod
    def calculate_loyalty_discount(cls, amount: Decimal, loyalty_level: LoyaltyLevel) -> Decimal:
        """Apply loyalty discount on final amount"""
        discount_rate = cls.LOYALTY_DISCOUNTS.get(loyalty_level, Decimal('0.00'))
        return (amount * discount_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class ShoppingCartService:
    """Main service class for shopping cart operations"""
    
    def __init__(self):
        self.carts: Dict[str, Dict[str, Any]] = {}
    
    def create_cart(self, cart_request: CartRequest) -> CartResponse:
        """Create a new shopping cart with items"""
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
        """Add or update an item in the cart"""
        if cart_id not in self.carts:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        try:
            cart = self.carts[cart_id]
            items = cart['items']
            
            if add_request.item.id in items:
                # Update existing item quantity
                existing_item = items[add_request.item.id]
                existing_item.quantity += add_request.item.quantity
            else:
                # Add new item
                items[add_request.item.id] = add_request.item
            
            # Recalculate summary
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
        """Remove an item from the cart"""
        if cart_id not in self.carts:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        try:
            cart = self.carts[cart_id]
            items = cart['items']
            
            if item_id not in items:
                raise HTTPException(status_code=404, detail="Item not found in cart")
            
            del items[item_id]
            
            # Recalculate summary
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
        """Update item quantity in the cart"""
        if cart_id not in self.carts:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        try:
            cart = self.carts[cart_id]
            items = cart['items']
            
            if update_request.item_id not in items:
                raise HTTPException(status_code=404, detail="Item not found in cart")
            
            items[update_request.item_id].quantity = update_request.quantity
            
            # Recalculate summary
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
        """Get cart details"""
        if cart_id not in self.carts:
            return None
        
        cart = self.carts[cart_id]
        return CartResponse(
            cart_id=cart_id,
            summary=cart['summary'],
            timestamp=datetime.now()
        )
    
    def get_all_carts(self) -> List[str]:
        """Get list of all cart IDs"""
        return list(self.carts.keys())
    
    def clear_cart(self, cart_id: str) -> bool:
        """Clear all items from a cart"""
        if cart_id not in self.carts:
            return False
        
        cart = self.carts[cart_id]
        cart['items'] = {}
        
        # Recalculate summary with empty items
        summary = self._calculate_cart_summary([], cart['customer'])
        cart['summary'] = summary
        
        logger.info(f"Cleared all items from cart {cart_id}")
        return True
    
    def delete_cart(self, cart_id: str) -> bool:
        """Delete a cart completely"""
        if cart_id not in self.carts:
            return False
        
        del self.carts[cart_id]
        logger.info(f"Deleted cart {cart_id}")
        return True
    
    def _calculate_cart_summary(self, items: List[ProductItem], customer: Customer) -> CartSummary:
        """Calculate comprehensive cart summary with all discounts applied in correct order"""
        item_breakdowns = []
        cart_subtotal = Decimal('0.00')
        total_tax = Decimal('0.00')
        total_item_discounts = Decimal('0.00')
        
        # Step 1: Process each item and calculate item-specific discounts
        for item in items:
            # Calculate base amounts
            subtotal_before_tax = item.price * item.quantity
            tax_amount = TaxCalculator.calculate_tax(subtotal_before_tax, item.category)
            subtotal_after_tax = subtotal_before_tax + tax_amount
            
            # Calculate item-specific discount (Electronics 15% off if quantity > 2)
            item_discount = DiscountCalculator.calculate_item_discount(item, subtotal_after_tax)
            final_item_total = subtotal_after_tax - item_discount
            
            # Create breakdown
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
            cart_subtotal += subtotal_after_tax  # Cart total before any discounts
            total_tax += tax_amount
            total_item_discounts += item_discount
        
        # Step 2: Calculate cart total after item discounts
        cart_total_after_item_discounts = cart_subtotal - total_item_discounts
        
        # Step 3: Apply bulk discount (10% off if cart value > $200) - applied to total after item discounts
        bulk_discount = DiscountCalculator.calculate_bulk_discount(cart_total_after_item_discounts)
        
        # Step 4: Calculate amount after bulk discount
        amount_after_bulk_discount = cart_total_after_item_discounts - bulk_discount
        
        # Step 5: Apply loyalty discount to final amount
        loyalty_discount = DiscountCalculator.calculate_loyalty_discount(
            amount_after_bulk_discount, customer.loyalty_level
        )
        
        # Final total
        final_total = amount_after_bulk_discount - loyalty_discount
        
        return CartSummary(
            items=item_breakdowns,
            subtotal=cart_subtotal,  # Total before any discounts
            total_tax=total_tax,
            item_discounts=total_item_discounts,
            bulk_discount=bulk_discount,
            loyalty_discount=loyalty_discount,
            final_total=final_total,
            customer_loyalty_level=customer.loyalty_level.value
        )
