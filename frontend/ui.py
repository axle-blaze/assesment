# shopping_cart_frontend.py
import streamlit as st
import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

st.title("🛒 Shopping Cart System")

# Initialize session state
if 'cart_data' not in st.session_state:
    st.session_state.cart_data = None

def make_api_request(method, endpoint, data=None):
    """Make API request and handle errors"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# Main sections
tab1, tab2 = st.tabs(["Create Cart", "Manage Cart"])

with tab1:
    st.header("Create New Cart")
    
    # Customer section
    st.subheader("Customer Information")
    loyalty_level = st.selectbox("Loyalty Level", ["None", "Bronze", "Silver", "Gold"])
    
    # Items section
    st.subheader("Add Items")
    
    # Initialize items in session state
    if 'cart_items' not in st.session_state:
        st.session_state.cart_items = []
    
    # Form to add items
    with st.form("add_item_form"):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            item_id = st.number_input("ID", min_value=1, value=1)
        with col2:
            item_name = st.text_input("Name", value="Item")
        with col3:
            category = st.selectbox("Category", ["Electronics", "Books", "Clothing"])
        with col4:
            price = st.number_input("Price", min_value=0.01, value=10.0)
        with col5:
            quantity = st.number_input("Quantity", min_value=1, value=1)
        
        if st.form_submit_button("Add Item"):
            new_item = {
                "id": item_id,
                "name": item_name,
                "category": category,
                "price": price,
                "quantity": quantity
            }
            st.session_state.cart_items.append(new_item)
            st.success(f"Added {item_name} to items list")
    
    # Quick add buttons
    st.write("**Quick Add Sample Items:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Add Laptop"):
            st.session_state.cart_items.append({
                "id": 1, "name": "Laptop", "category": "Electronics", "price": 1000, "quantity": 1
            })
    
    with col2:
        if st.button("Add Book"):
            st.session_state.cart_items.append({
                "id": 2, "name": "Book", "category": "Books", "price": 20, "quantity": 3
            })
    
    with col3:
        if st.button("Add T-shirt"):
            st.session_state.cart_items.append({
                "id": 3, "name": "T-shirt", "category": "Clothing", "price": 25, "quantity": 2
            })
    
    # Display current items
    if st.session_state.cart_items:
        st.write("**Current Items:**")
        for i, item in enumerate(st.session_state.cart_items):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{item['name']} - {item['category']} - ${item['price']} x {item['quantity']}")
            with col2:
                if st.button("Remove", key=f"remove_{i}"):
                    st.session_state.cart_items.pop(i)
                    st.rerun()
        
        if st.button("Clear All Items"):
            st.session_state.cart_items = []
            st.rerun()
    
    # Show request body
    if st.session_state.cart_items:
        st.subheader("Request Body Preview")
        request_body = {
            "items": st.session_state.cart_items,
            "customer": {"loyalty_level": loyalty_level}
        }
        st.code(json.dumps(request_body, indent=2), language="json")
        
        # Create cart button
        if st.button("Create Cart", type="primary"):
            result = make_api_request("POST", "/cart", request_body)
            if result:
                st.session_state.cart_data = result
                st.success(f"Cart created! Cart ID: {result['cart_id']}")
                st.session_state.cart_items = []  # Clear items after successful creation

with tab2:
    st.header("Manage Existing Cart")
    
    # Load cart by ID
    cart_id = st.text_input("Cart ID")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Load Cart"):
            if cart_id:
                result = make_api_request("GET", f"/cart/{cart_id}")
                if result:
                    st.session_state.cart_data = result
                    st.success("Cart loaded!")
    
    with col2:
        if st.button("Refresh Current Cart"):
            if st.session_state.cart_data:
                current_cart_id = st.session_state.cart_data['cart_id']
                result = make_api_request("GET", f"/cart/{current_cart_id}")
                if result:
                    st.session_state.cart_data = result
                    st.success("Cart refreshed!")

# Display cart data if available
if st.session_state.cart_data:
    st.header("Cart Details")
    
    cart_data = st.session_state.cart_data
    summary = cart_data['summary']
    
    st.write(f"**Cart ID:** {cart_data['cart_id']}")
    st.write(f"**Customer Loyalty:** {summary['customer_loyalty_level']}")
    st.write(f"**Timestamp:** {cart_data['timestamp']}")
    
    # Items table
    st.subheader("Items in Cart")
    if summary['items']:
        for idx, item in enumerate(summary['items']):
            with st.expander(f"{item['name']} - ${float(item['final_item_total']):.2f}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Category:** {item['category']}")
                    st.write(f"**Base Price:** ${float(item['base_price']):.2f}")
                    st.write(f"**Quantity:** {item['quantity']}")
                    st.write(f"**Subtotal Before Tax:** ${float(item['subtotal_before_tax']):.2f}")
                
                with col2:
                    st.write(f"**Tax Amount:** ${float(item['tax_amount']):.2f}")
                    st.write(f"**Subtotal After Tax:** ${float(item['subtotal_after_tax']):.2f}")
                    st.write(f"**Item Discount:** ${float(item['item_discount']):.2f}")
                    st.write(f"**Final Item Total:** ${float(item['final_item_total']):.2f}")
                
                # Item management buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_qty = st.number_input(f"New Quantity", min_value=1, value=item['quantity'], key=f"qty_{cart_data['cart_id']}_{item['id']}_{idx}")
                    if st.button(f"Update Qty", key=f"update_{cart_data['cart_id']}_{item['id']}_{idx}"):
                        update_data = {"item_id": item['id'], "quantity": new_qty}
                        result = make_api_request("PUT", f"/cart/{cart_data['cart_id']}/items/quantity", update_data)
                        if result:
                            st.session_state.cart_data = result
                            st.success("Quantity updated!")
                            st.rerun()
                
                with col2:
                    if st.button(f"Remove Item", key=f"remove_{cart_data['cart_id']}_{item['id']}_{idx}"):
                        result = make_api_request("DELETE", f"/cart/{cart_data['cart_id']}/items/{item['id']}")
                        if result:
                            st.session_state.cart_data = result
                            st.success("Item removed!")
                            st.rerun()
    
    # Add new item to existing cart
    if st.session_state.cart_data:
        st.subheader("Add New Item to Cart")
        with st.form("add_to_existing_cart"):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                new_id = st.number_input("Item ID", min_value=1, value=100, key="new_id")
            with col2:
                new_name = st.text_input("Name", value="New Item", key="new_name")
            with col3:
                new_category = st.selectbox("Category", ["Electronics", "Books", "Clothing"], key="new_category")
            with col4:
                new_price = st.number_input("Price", min_value=0.01, value=10.0, key="new_price")
            with col5:
                new_quantity = st.number_input("Quantity", min_value=1, value=1, key="new_quantity")
            
            if st.form_submit_button("Add to Cart"):
                new_item_data = {
                    "item": {
                        "id": new_id,
                        "name": new_name,
                        "category": new_category,
                        "price": new_price,
                        "quantity": new_quantity
                    }
                }
                result = make_api_request("POST", f"/cart/{cart_data['cart_id']}/items", new_item_data)
                if result:
                    st.session_state.cart_data = result
                    st.success("Item added to cart!")
                    st.rerun()
    
    # Price breakdown
    st.subheader("Price Breakdown")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Subtotal:** ${float(summary['subtotal']):.2f}")
        st.write(f"**Total Tax:** ${float(summary['total_tax']):.2f}")
        st.write(f"**Item Discounts:** -${float(summary['item_discounts']):.2f}")
    
    with col2:
        st.write(f"**Bulk Discount:** -${float(summary['bulk_discount']):.2f}")
        st.write(f"**Loyalty Discount:** -${float(summary['loyalty_discount']):.2f}")
        st.write(f"**FINAL TOTAL:** ${float(summary['final_total']):.2f}")
    
    # Raw JSON response
    with st.expander("View Raw API Response"):
        st.json(cart_data)

# API Health Check
with st.sidebar:
    st.subheader("API Status")
    if st.button("Check API Health"):
        try:
            response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=5)
            if response.status_code == 200:
                st.success("API is healthy!")
            else:
                st.error("API is not responding properly")
        except:
            st.error("Cannot connect to API")
    
    st.subheader("Instructions")
    st.write("""
    1. **Create Cart**: Add items and customer info, then create cart
    2. **Manage Cart**: Load existing cart by ID to modify items
    3. **Discounts Applied**:
       - Electronics: 15% off if qty > 2
       - Bulk: 10% off if total > $200
       - Loyalty: Bronze(5%), Silver(10%), Gold(15%)
    """)
    
    st.subheader("API Endpoints")
    st.code("""
POST /api/v1/cart
GET /api/v1/cart/{cart_id}
POST /api/v1/cart/{cart_id}/items
DELETE /api/v1/cart/{cart_id}/items/{item_id}
PUT /api/v1/cart/{cart_id}/items/quantity
    """)