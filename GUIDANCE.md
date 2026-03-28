# Karyana Inventory + Purchase System Guidance

## 1. Purpose
This document explains the complete flow of the current inventory and purchase system implementation in this service.

It covers:
- Domain boundaries
- Data lifecycle
- API flow
- Calculation rules
- Stock and supplier balance behavior
- Recommended operational sequence

## 2. Domain Design

### Master Data
- categories
- brands (available in model, optional in V1 usage)
- units
- suppliers
- riders
- products

### Transaction Data
- purchases
- purchase_items
- purchase_payments

### Inventory Data
- stock_batches
- stock_movements

## 3. End-to-End Business Flow

### Step A: Setup master records
Create records in this order:
1. categories
2. units
3. suppliers
4. riders
5. products

Why this order:
- products require category_id and unit_id
- riders may reference supplier_id

### Step B: Post purchase
When purchase is created:
1. Validate supplier and optional rider
2. Validate each item product and unit
3. Enforce product rules:
   - if product.has_expiry is true, expiry_date is required
   - if product.has_batch is true, batch_number is required
4. Calculate all totals server-side
5. Insert purchase header
6. Insert purchase items (with snapshot fields)
7. Create one stock_batch per item
8. Create one stock_movement per item with movement_type = purchase_in
9. If paid_amount > 0, create initial purchase_payment
10. Recalculate supplier current_balance

### Step C: Add further payments
When payment is added to a purchase:
1. Ensure purchase exists and is not cancelled
2. Create purchase_payment
3. Recompute purchase paid_amount and remaining_amount
4. Recompute payment_status
5. Recompute supplier current_balance

## 4. Calculation Rules (Source of Truth)

### Per line item
base_total = quantity * unit_cost

If discount_type is flat:
discount_amount = discount_value

If discount_type is percent:
discount_amount = base_total * (discount_value / 100)

tax_amount = (base_total - discount_amount) * tax_percent / 100
line_total = base_total - discount_amount + tax_amount

### Purchase totals
subtotal = sum(base_total)
discount_total = sum(discount_amount)
tax_total = sum(tax_amount)
grand_total = subtotal - discount_total + tax_total + other_charges
remaining_amount = grand_total - paid_amount

### Payment status
- paid: remaining_amount <= 0
- partially_paid: paid_amount > 0 and remaining_amount > 0
- unpaid: paid_amount == 0

### Supplier balance behavior
Current implementation recalculates as:
current_balance = opening_balance + sum(remaining_amount for non-cancelled purchases)

## 5. Inventory Ledger Behavior

### stock_batches
Tracks batch-level quantity and expiry scope.
- quantity_received
- quantity_available

### stock_movements
Tracks immutable movement events.
For purchase posting:
- movement_type: purchase_in
- quantity_in: quantity + bonus_quantity
- quantity_out: 0

This enables later FIFO, low stock, expiry, and audit reporting.

## 6. API Surface (Current)
All routes are under:
/api/v1/inventory

### Master CRUD
- POST /categories
- GET /categories
- GET /categories/{category_id}
- PUT /categories/{category_id}
- DELETE /categories/{category_id}

- POST /units
- GET /units
- GET /units/{unit_id}
- PUT /units/{unit_id}
- DELETE /units/{unit_id}

- POST /suppliers
- GET /suppliers
- GET /suppliers/{supplier_id}
- PUT /suppliers/{supplier_id}
- DELETE /suppliers/{supplier_id}

- POST /riders
- GET /riders
- GET /riders/{rider_id}
- PUT /riders/{rider_id}
- DELETE /riders/{rider_id}

- POST /products
- GET /products
- GET /products/{product_id}
- PUT /products/{product_id}
- DELETE /products/{product_id}

### Purchase + Inventory operations
- POST /purchases
- GET /purchases
- GET /purchases/{purchase_id}
- POST /purchases/{purchase_id}/payments
- GET /stock-movements

## 7. Request Flow Example

### Create purchase request shape
Use PurchaseCreateRequest with:
- supplier_id
- rider_id (optional)
- invoice details
- payment_method
- paid_amount
- other_charges
- items[]

Each item contains:
- product_id
- unit_id
- quantity
- bonus_quantity
- unit_cost
- discount_type and discount_value
- tax_percent
- batch_number and expiry/manufacturing dates as needed

### Expected side effects after successful request
- 1 purchase row
- N purchase_items rows
- N stock_batches rows
- N stock_movements rows
- 0 or 1 initial purchase_payment row (if paid_amount > 0)
- updated supplier current_balance

## 8. Data Integrity Notes
- Purchase item snapshots preserve history if product fields change later.
- Product slug uniqueness is generated/maintained in service.
- Soft delete is used via deleted_at where repository methods support it.

## 9. Operational Runbook

### Local startup sequence
1. Ensure virtual environment and dependencies are installed
2. Ensure database is reachable
3. Apply schema changes
4. Seed baseline master data
5. Run service and test endpoints

### Current migration caveat in this repo
This repository contains legacy Alembic branches that may fail in some environments due to unrelated historical dependencies (for example, missing venues table in old chain). If full upgrade to all heads fails:
- keep inventory module tables in sync via targeted migration path
- or create required legacy dependencies before full historical replay

## 10. Recommended V1 Operating Sequence for Teams
1. Master data admin sets categories, units, suppliers, riders, products.
2. Store operator posts purchases daily.
3. Finance/operator records subsequent supplier payments.
4. Inventory checks stock movements and batch availability.
5. Reporting layer reads purchases, stock movements, and supplier balances.

## 11. Suggested V1 Next Additions
- Stock summary endpoint
- Low stock report endpoint
- Expiry report endpoint
- Batch-wise stock report endpoint
- Supplier ledger endpoint
- Purchase cancel flow with reverse stock movement
