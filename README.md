# 🛒 Shopping Cart System

A production-grade shopping cart system built with a **FastAPI** backend and an interactive **Streamlit** frontend. Easily manage carts, apply discounts, and explore RESTful APIs—all in a clean, deployable setup.

---

## 🌐 Live Demo

- 🔹 **Frontend (UI):** [cart-discount.streamlit.app](https://cart-discount.streamlit.app/)
- 🔹 **Backend (API):** [assesments-nsjj.onrender.com](https://assesments-nsjj.onrender.com/)
- 🔹 **API Docs (Swagger):** [assesments-nsjj.onrender.com/docs](https://assesments-nsjj.onrender.com/docs)

---

## 🚀 Features

- **🛍️ Create Cart:** Add items, choose loyalty levels, and initialize a cart.
- **🧾 Manage Cart:** View, update, or delete cart items using cart ID.
- **🏷️ Smart Discounts:**
  - **Electronics Discount:** 15% off if quantity > 2
  - **Bulk Discount:** 10% off if total > $200
  - **Loyalty Discount:** 
    - Bronze – 5%
    - Silver – 10%
    - Gold – 15%
- **📡 RESTful API:** FastAPI-based backend with clean endpoints.
- **💻 Interactive UI:** Built with Streamlit for easy, visual cart management.
- **⚡ In-Memory Storage:** No external database required—great for prototyping.

---

## 🗂️ Project Structure

```
assesment/
│
├── backend/
│   ├── __init__.py
│   ├── api.py             # API routes
│   ├── main.py            # App entry point
│   ├── models.py          # Data models
│   ├── services.py        # Business logic and discount rules
│   └── shopping_cart.py   # Cart operations and storage
│
├── frontend/
│   └── ui.py              # Streamlit app
│
└── requirement.txt        # Project dependencies
```

---

## 🛠️ Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/axle-blaze/assesment.git
cd assesment
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
```

- **On Windows:**
  ```bash
  .\venv\Scripts\activate
  ```

- **On Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirement.txt
```

### 4. Run the Backend

```bash
python backend/main.py
```

- Local API: [http://localhost:8000](http://localhost:8000)  
- Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Run the Frontend

```bash
streamlit run frontend/ui.py
```

- Local UI: [http://localhost:8501](http://localhost:8501)

---

## 📬 API Endpoints

| Method | Endpoint                                 | Description                   |
|--------|------------------------------------------|-------------------------------|
| POST   | `/api/v1/cart`                           | Create a new cart             |
| GET    | `/api/v1/cart/{cart_id}`                 | Get cart details              |
| POST   | `/api/v1/cart/{cart_id}/items`           | Add item to existing cart     |
| DELETE | `/api/v1/cart/{cart_id}/items/{item_id}` | Remove item from cart         |
| PUT    | `/api/v1/cart/{cart_id}/items/quantity`  | Update quantity of an item    |

---

## 🧪 Usage Guide

### ✅ Create Cart
- Add items with name, category, price, and quantity.
- Choose the customer’s loyalty tier.
- Click **Create Cart** to generate a new cart ID.

### 🛠 Manage Existing Cart
- Input an existing **Cart ID**.
- Add, remove, or update items directly in the UI.
- View automatically updated prices and discounts.

### 🔍 Check API Health
- Use the “Check API” button in the sidebar to verify connectivity.

---

## 📌 Notes

- The backend must be running before launching the frontend.
- All data is stored in memory—no persistence after restart.
- Ideal for demos, PoCs, or learning API + UI integration.

---

## 📣 Contribution

Feel free to fork the repo, suggest improvements, or create issues. PRs are welcome!
