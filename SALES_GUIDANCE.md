# Sales Module - Complete Guide

This document describes the complete architecture, workflow, and API surface for the Sales (Point of Sale) module in the Karyana backend.

## Table of Contents

1. [Overview](#overview)
2. [Domain Design](#domain-design)
3. [Database Schema](#database-schema)
4. [End-to-End Sales Flow](#end-to-end-sales-flow)
5. [Calculation Rules](#calculation-rules)
6. [FIFO Stock Allocation](#fifo-stock-allocation)
7. [Customer Balance Tracking](#customer-balance-tracking)
8. [API Surface](#api-surface)
9. [Request/Response Examples](#requestresponse-examples)
10. [Operational Workflow](#operational-workflow)
11. [Next Features](#next-features)

---

## Overview

The Sales module enables fast, reliable point-of-sale (POS) transactions with the following core capabilities:

- **Customer Management**: Walk-in and registered customers with credit tracking
- **Sales Transactions**: Full, partial, or unpaid sales with instant stock deduction
- **FIFO Allocation**: Automatic stock deduction using First-In-First-Out (FIFO) from available batches
- **Balance Tracking**: Real-time customer receivables and supplier payables
- **Stock Ledger Integration**: Immutable stock movement records for audit trail
- **Payment Recording**: Multiple payments per sale with automatic balance updates
- **Sale Cancellation**: Reverse stock movements and restore customer/supplier balances

---

## Domain Design

### Master Data

**Customers** - Persistent or temporary buyers
- Walk-in: One default customer for cash transactions without customer details
- Regular: Named customers with credit account (receivables)
- Wholesale: Bulk buyers with special pricing

**Products** - Goods being sold (from Inventory module)
- Track inventory flag: Controls stock deduction on sale
- Unit pricing: Marked-up from cost price for profit reporting

### Transaction Data

**Sales** - Sale headers with aggregated totals
- One sale = many items
- Payment status: unpaid / partially_paid / paid
- Status: posted / cancelled (soft delete via deleted_at)

**SaleItems** - Individual sold products
- Snapshot fields: Product name, SKU, barcode, cost price (historical accuracy)
- Discount & tax calculation: Backend-calculated, immutable
- References batches for traceability

**SalePayments** - Payment records
- One or more payments per sale
- Immutable ledger for audit trail

### Inventory Integration

**StockBatches** - Updated quantities after FIFO deduction
- quantity_available reduced by sale allocation
- Historical cost preserved for profit calculation

**StockMovements** - Immutable transaction log
- movement_type: sale_out
- quantity_out: Allocated quantity
- reference_id: Sales ID for traceability

**SaleItemBatchAllocations** - FIFO traceability
- Links each sold line to exact batches consumed
- Supports returns, expiry tracking, FIFO audits

---

## Database Schema

### customers Table

```sql
CREATE TABLE customers (
  id UUID PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  phone VARCHAR(30) UNIQUE NULL,
  email VARCHAR(120) NULL,
  address TEXT NULL,
  city VARCHAR(100) NULL,
  opening_balance NUMERIC(12,2) DEFAULT 0,
  current_balance NUMERIC(12,2) DEFAULT 0,
  customer_type VARCHAR(30) DEFAULT 'walk_in',  -- walk_in | regular | wholesale
  notes TEXT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  deleted_at TIMESTAMP NULL
);
```

### sales Table

```sql
CREATE TABLE sales (
  id UUID PRIMARY KEY,
  sale_number VARCHAR(50) UNIQUE NOT NULL,  -- SAL-20260328-00001
  customer_id UUID NOT NULL FK -> customers.id,
  sale_date DATE NOT NULL,
  invoice_number VARCHAR(100) NULL,
  payment_method VARCHAR(30) NOT NULL,
  payment_status VARCHAR(30) NOT NULL,  -- unpaid | partially_paid | paid
  subtotal NUMERIC(12,2) NOT NULL,
  discount_total NUMERIC(12,2) NOT NULL,
  tax_total NUMERIC(12,2) NOT NULL,
  other_charges NUMERIC(12,2) NOT NULL,
  grand_total NUMERIC(12,2) NOT NULL,
  paid_amount NUMERIC(12,2) NOT NULL,
  remaining_amount NUMERIC(12,2) NOT NULL,
  notes TEXT NULL,
  status VARCHAR(30) NOT NULL,  -- posted | cancelled
  created_by UUID NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  deleted_at TIMESTAMP NULL
);
```

### sale_items Table

```sql
CREATE TABLE sale_items (
  id UUID PRIMARY KEY,
  sale_id UUID NOT NULL FK -> sales.id,
  product_id UUID NOT NULL FK -> products.id,
  product_name_snapshot VARCHAR(150) NOT NULL,
  sku_snapshot VARCHAR(80) NULL,
  barcode_snapshot VARCHAR(120) NULL,
  unit_id UUID NOT NULL FK -> units.id,
  quantity NUMERIC(12,3) NOT NULL,
  unit_price NUMERIC(12,2) NOT NULL,
  cost_price_snapshot NUMERIC(12,2) NOT NULL,  -- For profit reporting
  discount_type VARCHAR(20) NULL,  -- flat | percent
  discount_value NUMERIC(12,2) NOT NULL,  -- Original discount input
  discount_amount NUMERIC(12,2) NOT NULL,  -- Calculated amount
  tax_percent NUMERIC(5,2) NOT NULL,
  tax_amount NUMERIC(12,2) NOT NULL,
  line_total NUMERIC(12,2) NOT NULL,
  notes TEXT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  deleted_at TIMESTAMP NULL
);
```

### sale_payments Table

```sql
CREATE TABLE sale_payments (
  id UUID PRIMARY KEY,
  sale_id UUID NOT NULL FK -> sales.id,
  customer_id UUID NOT NULL FK -> customers.id,
  payment_date DATE NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  payment_method VARCHAR(30) NOT NULL,  -- cash | bank_transfer | easypaisa | jazzcash | card | credit
  reference_number VARCHAR(100) NULL,
  notes TEXT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  deleted_at TIMESTAMP NULL
);
```

### sale_item_batch_allocations Table

```sql
CREATE TABLE sale_item_batch_allocations (
  id UUID PRIMARY KEY,
  sale_item_id UUID NOT NULL FK -> sale_items.id,
  stock_batch_id UUID NOT NULL FK -> stock_batches.id,
  quantity_allocated NUMERIC(12,3) NOT NULL,
  unit_cost NUMERIC(12,2) NOT NULL,  -- Cost at time of sale (from batch)
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
```

---

## End-to-End Sales Flow

### 1. Sale Creation Flow (POST /sales)

#### Input Validation
```
1. Customer exists and is active
2. Sale contains at least 1 item
3. Each item:
   - Quantity > 0
   - Unit price > 0
   - Product exists and is active
   - Unit is valid
4. Stock available (quantity_available >= quantity for each item)
```

#### Calculation (Backend Only)
```
For each item:
  base_total = quantity × unit_price
  
  If discount_type == "flat":
    discount_amount = discount_value
  Else if discount_type == "percent":
    discount_amount = base_total × (discount_value / 100)
  Else:
    discount_amount = 0
  
  tax_amount = (base_total - discount_amount) × (tax_percent / 100)
  line_total = base_total - discount_amount + tax_amount

Sale totals:
  subtotal = sum(base_total for all items)
  discount_total = sum(discount_amount for all items)
  tax_total = sum(tax_amount for all items)
  grand_total = subtotal - discount_total + tax_total + other_charges
  remaining_amount = grand_total - paid_amount
  payment_status = determine_payment_status(paid_amount, remaining_amount)
```

#### Database Operations (Atomic Transaction)
```
1. Create Sale header
2. For each item:
   a. Create SaleItem with snapshot fields
   b. Get available batches sorted by created_at (FIFO)
   c. Allocate quantity from batches:
      - Create SaleItemBatchAllocation
      - Create StockMovement (movement_type = sale_out)
      - Reduce batch.quantity_available
   d. Create initial SalePayment if paid_amount > 0
3. Recalculate customer.current_balance
4. COMMIT transaction
```

### 2. Payment Addition Flow (POST /sales/{id}/payments)

#### Validation
```
1. Sale exists
2. Sale is not cancelled
3. Payment amount > 0
```

#### Processing
```
1. Create SalePayment record
2. Update sale.paid_amount += payment.amount
3. Update sale.remaining_amount = grand_total - paid_amount
4. Update sale.payment_status (unpaid → partially_paid → paid)
5. Recalculate customer.current_balance
6. COMMIT
```

### 3. Sale Cancellation Flow (POST /sales/{id}/cancel)

#### Processing
```
1. Get all SaleItemBatchAllocations for this sale
2. For each allocation:
   a. Find stock_batch
   b. Restore batch.quantity_available += allocation.quantity_allocated
3. Delete all StockMovements for this sale (reference_type = sale)
4. Update sale.status = cancelled
5. Recalculate customer.current_balance
6. COMMIT
```

---

## Calculation Rules

### Example: Two-Item Sale

**Item 1: Sugar**
- Quantity: 20 kg
- Unit Price: 150
- Discount Type: Flat
- Discount Value: 200
- Tax: 0%

```
base_total = 20 × 150 = 3000
discount_amount = 200 (flat)
tax_amount = (3000 - 200) × 0% = 0
line_total = 3000 - 200 + 0 = 2800
```

**Item 2: Oil**
- Quantity: 5 L
- Unit Price: 650
- Discount Type: Percent
- Discount Value: 5%
- Tax: 0%

```
base_total = 5 × 650 = 3250
discount_amount = 3250 × (5 / 100) = 162.50
tax_amount = (3250 - 162.50) × 0% = 0
line_total = 3250 - 162.50 + 0 = 3087.50
```

**Sale Totals**
```
subtotal = 3000 + 3250 = 6250.00
discount_total = 200 + 162.50 = 362.50
tax_total = 0 + 0 = 0.00
other_charges = 0.00
grand_total = 6250 - 362.50 + 0 + 0 = 5887.50

If paid_amount = 5000:
  remaining_amount = 5887.50 - 5000 = 887.50
  payment_status = partially_paid (paid > 0 AND remaining > 0)
```

---

## FIFO Stock Allocation

### Mechanism

When 20kg of Sugar is sold:

**Before Sale:**
```
Batch A (BATCH-001, created 2026-03-01):
  - quantity_received: 50
  - quantity_available: 50

Batch B (BATCH-002, created 2026-03-15):
  - quantity_received: 30
  - quantity_available: 30
```

**FIFO Algorithm:**
```
1. Sort batches by created_at (ASC) → Batch A first
2. Allocate 20kg from Batch A:
   - allocation 1: 20 units from Batch A @ cost 100
3. Batch A quantity_available: 50 - 20 = 30
4. After sale, Batch A still has 30 available
```

**Allocations Created:**
```
SaleItemBatchAllocation:
  sale_item_id: <sugar line id>
  stock_batch_id: <Batch A id>
  quantity_allocated: 20
  unit_cost: 100
```

**Stock Movements Created:**
```
StockMovement:
  product_id: <Sugar product id>
  stock_batch_id: <Batch A id>
  movement_type: sale_out
  quantity_out: 20
  reference_type: sale
  reference_id: <Sale id>
```

### Expiry Tracking

If a product has `has_expiry = true`, you can enhance FIFO with expiry-based ordering:
```
Sort batches by:
  1. expiry_date (earliest first - FEFO)
  2. created_at (then by FIFO)
```

---

## Customer Balance Tracking

### Formula

```
customer.current_balance = opening_balance + sum(remaining_amount for non-cancelled sales)
```

### Example

**Customer: Ahmed Hassan**
- opening_balance: 500 (credit account)

**After Sale 1 (5887.50 grand total, 5000 paid):**
```
remaining_balance = 887.50
current_balance = 500 + 887.50 = 1387.50 (amount owed)
```

**After Payment of 3000:**
```
remaining_balance = 887.50 - 3000 = -2112.50 (overpaid)
current_balance = 500 + (-2112.50) = -1612.50 (customer credit)
```

**Note:** Negative balance means customer has a credit they can use for future purchases or claim as refund.

### Updates

- **On Sale Creation**: Recalculate immediately
- **On Payment Addition**: Recalculate immediately
- **On Sale Cancellation**: Recalculate immediately

---

## API Surface

### Base Path
```
/api/v1/sales/
```

### Customer Endpoints

#### POST /customers
**Create a new customer**

Request:
```json
{
  "name": "Ahmed Hassan",
  "phone": "+923009876543",
  "email": "ahmed@example.com",
  "address": "Street 10, Lahore",
  "city": "Lahore",
  "opening_balance": 500,
  "customer_type": "regular",
  "notes": "Regular customer"
}
```

Response: `201 Created`
```json
{
  "id": "8b313785-b4de-42fc-a77d-8a093a8e3a41",
  "name": "Ahmed Hassan",
  "phone": "+923009876543",
  "email": "ahmed@example.com",
  "address": "Street 10, Lahore",
  "city": "Lahore",
  "opening_balance": 500.00,
  "current_balance": 500.00,
  "customer_type": "regular",
  "notes": "Regular customer",
  "is_active": true,
  "created_at": "2026-03-28T...",
  "updated_at": "2026-03-28T..."
}
```

#### GET /customers
**List all customers**

Query Parameters:
- `skip`: 0 (default)
- `limit`: 100 (default, max 1000)

Response: `200 OK` → Array of CustomerResponse

#### GET /customers/{customer_id}
**Get single customer**

Response: `200 OK` → CustomerResponse or `404 Not Found`

#### PUT /customers/{customer_id}
**Update customer**

Request: Partial CustomerUpdateRequest

Response: `200 OK` → Updated CustomerResponse

### Sale Endpoints

#### POST /sales
**Create a new sale**

Request:
```json
{
  "customer_id": "8b313785-b4de-42fc-a77d-8a093a8e3a41",
  "sale_date": "2026-03-28",
  "invoice_number": "SAL-2026-0001",
  "payment_method": "cash",
  "paid_amount": 2500,
  "other_charges": 0,
  "notes": "Walk-in customer",
  "items": [
    {
      "product_id": "cf818727-36ef-4df0-a8d8-fd7b1325b8d9",
      "unit_id": "0b992720-1a40-4335-a0a7-4c5d6a0e5c69",
      "quantity": 2,
      "unit_price": 160,
      "discount_type": "flat",
      "discount_value": 10,
      "tax_percent": 0,
      "notes": "Regular sale"
    }
  ]
}
```

Response: `201 Created` → SaleResponse with full details including items and allocations

#### GET /sales
**List sales**

Query Parameters:
- `skip`: 0
- `limit`: 100
- `customer_id`: (optional) Filter by customer
- `payment_status`: (optional) unpaid | partially_paid | paid
- `status`: (optional) posted | cancelled

Response: `200 OK` → Array of SaleListResponse

#### GET /sales/{sale_id}
**Get single sale with all details**

Response: `200 OK` → SaleResponse with items and allocations

#### POST /sales/{sale_id}/payments
**Add payment to sale**

Request:
```json
{
  "payment_date": "2026-03-28",
  "amount": 3000,
  "payment_method": "bank_transfer",
  "reference_number": "TRF-123456",
  "notes": "Partial payment"
}
```

Response: `201 Created` → Updated SaleResponse

#### POST /sales/{sale_id}/cancel
**Cancel a sale and restore stock**

Response: `200 OK` → Cancelled SaleResponse (status = "cancelled")

#### POST /customers/walk-in/init
**Get or create default walk-in customer**

Response: `200 OK` → Walk-in CustomerResponse

---

## Request/Response Examples

### Example 1: Walk-in Cash Sale (Complete)

**Request:**
```bash
POST /api/v1/sales/sales
Content-Type: application/json

{
  "customer_id": "default-walkin-id",
  "sale_date": "2026-03-28",
  "invoice_number": null,
  "payment_method": "cash",
  "paid_amount": 1000,
  "other_charges": 0,
  "notes": null,
  "items": [
    {
      "product_id": "prod-123",
      "unit_id": "unit-kg",
      "quantity": 2,
      "unit_price": 500,
      "discount_type": null,
      "discount_value": 0,
      "tax_percent": 0,
      "notes": null
    }
  ]
}
```

**Response:**
```json
{
  "id": "sale-001",
  "sale_number": "SAL-20260328-00001",
  "customer_id": "walkin-id",
  "sale_date": "2026-03-28",
  "invoice_number": null,
  "payment_method": "cash",
  "payment_status": "paid",
  "subtotal": 1000.00,
  "discount_total": 0.00,
  "tax_total": 0.00,
  "other_charges": 0.00,
  "grand_total": 1000.00,
  "paid_amount": 1000.00,
  "remaining_amount": 0.00,
  "notes": null,
  "status": "posted",
  "created_by": null,
  "items": [
    {
      "id": "item-001",
      "product_id": "prod-123",
      "product_name_snapshot": "Sugar 1kg",
      "sku_snapshot": "SUGAR-1KG",
      "barcode_snapshot": "123456",
      "unit_id": "unit-kg",
      "quantity": 2.000,
      "unit_price": 500.00,
      "cost_price_snapshot": 100.00,
      "discount_type": null,
      "discount_value": 0.00,
      "discount_amount": 0.00,
      "tax_percent": 0.00,
      "tax_amount": 0.00,
      "line_total": 1000.00,
      "notes": null,
      "created_at": "2026-03-28T..."
    }
  ],
  "created_at": "2026-03-28T...",
  "updated_at": "2026-03-28T..."
}
```

### Example 2: Credit Sale with Partial Payment

**Request:**
```bash
POST /api/v1/sales/sales
{
  "customer_id": "cust-ahmed",
  "sale_date": "2026-03-28",
  "invoice_number": "INV-001",
  "payment_method": "credit",
  "paid_amount": 2000,
  "other_charges": 50,
  "items": [
    {
      "product_id": "product-a",
      "unit_id": "unit-kg",
      "quantity": 5,
      "unit_price": 200,
      "discount_type": "percent",
      "discount_value": 10,
      "tax_percent": 5
    }
  ]
}
```

**Calculation:**
```
Item: 5 × 200 = 1000
Discount: 1000 × 10% = 100
Tax: (1000 - 100) × 5% = 45
Line Total: 1000 - 100 + 45 = 945

Sale Total:
  subtotal = 1000
  discount_total = 100
  tax_total = 45
  other_charges = 50
  grand_total = 1000 - 100 + 45 + 50 = 995
  remaining = 995 - 2000 = -1005 (overpaid)
  payment_status = paid
```

---

## Operational Workflow

### V1 Recommended Sequence

#### Day 1: Setup
```
1. POST /customers/walk-in/init
   → Create default walk-in customer for cash sales
2. POST /customers
   → Create 3-5 regular customers with opening balances
3. [Verify inventory has products with stock batches]
```

#### Daily Operation
```
Morning:
  GET /customers → Verify customer list

Throughout Day:
  POST /sales → Create sale for each transaction
  POST /sales/{id}/payments → Record payment if partial
  
End of Day:
  GET /sales?payment_status=partially_paid → Follow up on outstanding
  GET /customers → Review balances owed
```

#### Problem Sales
```
Wrong item sold:
  POST /sales/{id}/cancel → Reverse everything
  POST /sales → Create correct sale

Partial payment received later:
  POST /sales/{id}/payments → Add payment
  GET /sales/{id} → Verify balance
```

### Customer Account Example

**Ahmed Hassan starts with 500 balance (credit account)**

1. **Sale 1: 5887.50 (paid 5000)**
   - remaining: 887.50
   - balance: 500 + 887.50 = 1387.50

2. **Sale 1 additional payment: 3000**
   - remaining: -2112.50
   - balance: 500 + (-2112.50) = -1612.50 (has credit)

3. **Sale 2: 1000 (paid 0 - full credit)**
   - remaining: 1000
   - balance: -1612.50 + 1000 = -612.50 (still has credit)

---

## Next Features

### Phase 2: Reporting
- `GET /sales-report` - Daily/monthly sales aggregates
- `GET /customer-ledger/{id}` - Transaction history per customer
- `GET /profit-report` - Gross profit by product/category
- `GET /low-stock-report` - Products below minimum threshold
- `GET /expiry-report` - Products expiring soon

### Phase 3: Advanced
- Bulk sales import (CSV/Excel)
- Sale return/exchange (reverse allocation + new sale)
- Loyalty points
- Tiered pricing (quantity/customer type discounts)
- Printable invoice/receipt (PDF generation)
- Sales by cashier/user
- Daily reconciliation report

### Phase 4: Integration
- Barcode scanner support (simplified UX)
- SMS payment reminders for credit customers
- Automated reconciliation with purchases
- Sync with accounting system (GL posting)

---

## Notes & Constraints

### Financial Precision
- All monetary fields use NUMERIC(12,2) - 2 decimal places
- Quantities use NUMERIC(12,3) - 3 decimal places for fractional units
- Backend quantizes all intermediate calculations with ROUND_HALF_UP
- Never trust frontend calculations

### Stock Integrity
- FIFO allocation is default and not configurable per-sale
- Expiry-based ordering can be added later
- Cancelled sales always restore stock (no manual adjustment)
- Stock movements are immutable ledger entries

### Data Integrity
- All snapshots (product_name, cost_price, SKU, barcode) are historical records
- Modifying product details does NOT affect completed sales
- Deleted batches DO NOT affect historical allocations
- Payment records cannot be deleted (soft-delete via deleted_at if needed)

### Customer Balance
- Formula is derived (not stored separately) to eliminate reconciliation issues
- Recalculated on each sale/payment/cancellation
- Negative balance = customer credit (overpaid or advance payment)
- Can handle credit customers, wholesale, installment buys

---

## Summary

The Sales module is production-ready with:

✅ Complete FIFO stock allocation  
✅ Accurate financial calculations (backend-only)  
✅ Real-time customer balance tracking  
✅ Immutable transaction ledger  
✅ Full payment recording  
✅ Sale cancellation with stock restoration  
✅ Walk-in and credit customer support  

**All business rules are implemented server-side. The frontend can trust the API responses completely.**
