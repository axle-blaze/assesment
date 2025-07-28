# 🛒 Shopping Cart System

A production-grade shopping cart system with a FastAPI backend and a Streamlit frontend UI.

---

## Features

- **Create Cart:** Add items and customer info, then create a new cart.
- **Manage Cart:** Load an existing cart by ID to view, update, or remove items.
- **Discounts Applied:**
  - **Electronics:** 15% off if quantity > 2
  - **Bulk:** 10% off if total > $200
  - **Loyalty:** Bronze (5%), Silver (10%), Gold (15%)
- **API Endpoints:** RESTful endpoints for cart operations.
- **Interactive UI:** Built with Streamlit for easy cart management.

---

## Project Structure

```
assesment/
│
├── backend/
│   ├── __init__.py
│   ├── api.py
│   ├── main.py
│   ├── models.py
│   ├── services.py
│   └── shopping_cart.py
│
├── frontend/
│   └── ui.py
│
└── requirement.txt
```

---

## Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/axle-blaze/assesment.git
cd assesment
```

### 2. Create and Activate a Virtual Environment

```sh
python -m venv venv
.\venv\Scripts\activate   # On Windows

source venv/bin/activate  # On Mac/Linux

```

### 3. Install Dependencies

```sh
pip install -r requirement.txt
```

### 4. Run the Backend (FastAPI)

```sh
python backend/main.py
```
- The API will be available at [http://localhost:8000](http://localhost:8000)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Run the Frontend (Streamlit UI)

```sh
streamlit run frontend/ui.py
```
- The UI will open at [http://localhost:8501](http://localhost:8501)

---

## API Endpoints

```
POST   /api/v1/cart
GET    /api/v1/cart/{cart_id}
POST   /api/v1/cart/{cart_id}/items
DELETE /api/v1/cart/{cart_id}/items/{item_id}
PUT    /api/v1/cart/{cart_id}/items/quantity
```

---

## Usage

1. **Create Cart:**  
   - Add items and select customer loyalty level.
   - Click "Create Cart" to generate a new cart.

2. **Manage Cart:**  
   - Enter an existing Cart ID to load and manage the cart.
   - Update quantities, remove items, or add new items.

3. **Check API Health:**  
   - Use the sidebar button to check if the backend API is running.

---

## Notes

- Ensure the backend server is running before starting the frontend UI.
- All data is stored in memory (no database).

---
