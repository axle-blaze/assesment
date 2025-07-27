from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from models import CartRequest, AddItemRequest, UpdateQuantityRequest, CartResponse
from services import ShoppingCartService

app = FastAPI(
    title="Shopping Cart API",
    description="Production-grade shopping cart system with discount calculations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cart_service = ShoppingCartService()

def get_cart_service() -> ShoppingCartService:
    return cart_service

@app.post("/api/v1/cart", response_model=CartResponse)
async def create_cart(
    cart_request: CartRequest,
    service: ShoppingCartService = Depends(get_cart_service)
):
    return service.create_cart(cart_request)

@app.get("/api/v1/cart/{cart_id}", response_model=CartResponse)
async def get_cart(
    cart_id: str,
    service: ShoppingCartService = Depends(get_cart_service)
):
    cart = service.get_cart(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@app.post("/api/v1/cart/{cart_id}/items", response_model=CartResponse)
async def add_item_to_cart(
    cart_id: str,
    add_request: AddItemRequest,
    service: ShoppingCartService = Depends(get_cart_service)
):
    return service.add_item(cart_id, add_request)

@app.delete("/api/v1/cart/{cart_id}/items/{item_id}", response_model=CartResponse)
async def remove_item_from_cart(
    cart_id: str,
    item_id: int,
    service: ShoppingCartService = Depends(get_cart_service)
):
    return service.remove_item(cart_id, item_id)

@app.put("/api/v1/cart/{cart_id}/items/quantity", response_model=CartResponse)
async def update_item_quantity(
    cart_id: str,
    update_request: UpdateQuantityRequest,
    service: ShoppingCartService = Depends(get_cart_service)
):
    return service.update_quantity(cart_id, update_request)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
