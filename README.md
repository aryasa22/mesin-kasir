# Web-Based POS (Point of Sale) System

Production-oriented POS web app for cashier and admin roles using FastAPI, PostgreSQL, SQLAlchemy, and vanilla frontend.

## 1) System Architecture (Text Diagram)

```text
[ Browser UI ]
  |  Login / Cashier / Inventory / Reports pages
  |  (HTML + CSS + Vanilla JS)
  v
[ FastAPI Application Layer ]
  |- Auth API (JWT)
  |- Product API (Inventory CRUD + barcode lookup)
  |- Transaction API (cart checkout + stock deduction + receipt payload)
  |- Report API (daily/monthly sales and profit)
  v
[ Service Layer ]
  |- Transaction Service (validation, stock checks, invoice creation)
  |- Reporting Service (optimized SQL aggregates)
  v
[ Data Access Layer ]
  |- SQLAlchemy ORM models
  |- PostgreSQL engine/session
  v
[ PostgreSQL ]
  |- users
  |- products
  |- transactions
  |- transaction_items
```

## 2) Project Folder Structure

```text
mesin-kasir/
├── app/
│   ├── api/                # REST endpoints and auth dependencies
│   ├── core/               # app settings and security helpers
│   ├── db/                 # database engine/session/base
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic request/response models
│   ├── services/           # transaction and reporting business logic
│   ├── static/             # css/js assets
│   ├── templates/          # login, cashier, inventory, report pages
│   └── main.py             # app entrypoint
├── scripts/seed_data.py    # sample user/product data
├── requirements.txt
└── README.md
```

## 3) PostgreSQL Database Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    cost_price NUMERIC(12,2) NOT NULL,
    selling_price NUMERIC(12,2) NOT NULL,
    stock_qty INT NOT NULL CHECK (stock_qty >= 0),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_name ON products(name);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(30) UNIQUE NOT NULL,
    cashier_id INT NOT NULL REFERENCES users(id),
    total_amount NUMERIC(12,2) NOT NULL,
    payment_amount NUMERIC(12,2) NOT NULL,
    change_amount NUMERIC(12,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_transactions_date ON transactions(created_at);

CREATE TABLE transaction_items (
    id SERIAL PRIMARY KEY,
    transaction_id INT NOT NULL REFERENCES transactions(id),
    product_id INT NOT NULL REFERENCES products(id),
    product_name VARCHAR(150) NOT NULL,
    qty INT NOT NULL,
    cost_price NUMERIC(12,2) NOT NULL,
    selling_price NUMERIC(12,2) NOT NULL,
    subtotal NUMERIC(12,2) NOT NULL
);
```

## 4) Main REST API Endpoints

### Auth
- `POST /api/auth/login`

### Products / Inventory
- `GET /api/products?search=...`
- `GET /api/products/barcode/{barcode}`
- `GET /api/products/{product_id}`
- `POST /api/products` (admin)
- `PUT /api/products/{product_id}` (admin)
- `DELETE /api/products/{product_id}` (admin)

### Transactions
- `POST /api/transactions`
- `GET /api/transactions/{transaction_id}`

### Reports
- `GET /api/reports/summary?period=daily|monthly` (admin)
- `GET /api/reports/breakdown?period=daily|monthly` (admin)

## 5) Sample Code Snippets

### A. Creating a transaction
```python
transaction = create_transaction(db, payload, current_user)
```
The function validates stock, calculates subtotals/total/change, stores transaction + items, and updates stock atomically.

### B. Updating stock
```python
if "stock_qty" in updates and updates["stock_qty"] < 0:
    raise HTTPException(status_code=400, detail="Stock cannot be negative")
product.stock_qty = updates["stock_qty"]
```

### C. Printing receipt
```javascript
document.getElementById("print-receipt").addEventListener("click", () => window.print());
```
Receipt body is rendered in `<pre id="receipt">` after successful checkout.

### D. Generating profit/loss report
```sql
SELECT COUNT(DISTINCT t.id) AS total_transactions,
       COALESCE(SUM(t.total_amount), 0) AS total_revenue,
       COALESCE(SUM(ti.cost_price * ti.qty), 0) AS total_cost,
       COALESCE(SUM(t.total_amount) - SUM(ti.cost_price * ti.qty), 0) AS gross_profit
FROM transactions t
LEFT JOIN transaction_items ti ON ti.transaction_id = t.id
WHERE DATE(t.created_at) = CURRENT_DATE;
```

## 6) Run Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL 13+

### Setup
1. Create database:
   ```sql
   CREATE DATABASE mesin_kasir;
   ```
2. Configure `.env`:
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/mesin_kasir
   SECRET_KEY=replace-with-random-secret
   STORE_NAME=My POS Store
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start app:
   ```bash
   uvicorn app.main:app --reload
   ```
5. (Optional) seed demo data:
   ```bash
   python scripts/seed_data.py
   ```

### Default demo users
- `admin / admin123`
- `cashier / cashier123`

## Notes for scalability
- Modular service layer supports future branch/multi-tenant extension.
- JWT auth allows future role granularity.
- Transaction design supports audit logs and additional payment methods.
- Reporting SQL can be moved to materialized views for high-volume stores.
