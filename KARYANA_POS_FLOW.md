# Karyana System Flow (POS Guide)

## 1) What Are Units?

In your system, **Unit** means the measurement used for a product quantity.

Examples:
- `kg` (kilogram)
- `g` (gram)
- `ltr` (liter)
- `ml` (milliliter)
- `pcs` (pieces)
- `pack`

Why Units are important:
- Keep stock quantities consistent.
- Make pricing clear (`price per kg`, `price per piece`, etc.).
- Prevent confusion in sales and inventory reports.
- Allow products to have base/sales/purchase unit mappings in product setup.

Simple example:
- Product: Sugar
- Unit: `kg`
- If cashier sells `2`, system understands it as `2 kg`.

---

## 2) Basic Flow of Your Current Karyana System

Your current backend flow is now **POS-focused**.

### A. Master Setup (one-time / occasional)
1. Create Categories (e.g., Grocery, Beverages)
2. Create Units (kg, pcs, ltr, etc.)
3. Create Products (assign category + unit + prices)

### B. Counter Sale Flow (daily operations)
1. Select customer
   - Walk-in customer or regular customer
2. Add sale items
   - Product, quantity, unit price, discount (if any)
3. System calculates totals
   - Subtotal, discount, tax, grand total
4. Take payment
   - Full or partial
5. Save sale
   - Stock is deducted (FIFO logic)
6. Generate invoice
   - Printable JSON and PDF endpoints available

### C. After Sale
1. Add additional payment later if customer has due
2. Update payment status (`unpaid`, `partially_paid`, `paid`)
3. If wrong sale happened, cancel the sale using sale cancel endpoint

---

## 3) Is It Complete POS?

## Short answer
**Yes, for core retail POS operations it is complete and usable.**

What is already covered:
- Customer management
- Walk-in customer support
- Sales creation
- Payment posting (full/partial)
- Invoice generation (JSON + PDF)
- Sale cancellation flow
- Stock deduction with FIFO behavior
- POS-oriented inventory setup (categories, units, products)

What is intentionally removed or not in cashier flow:
- Rider flow
- Provider/supplier purchase flow from active POS API surface

---

## 4) Practical POS Sequence for Your Team

Use this daily sequence:
1. Open shift and verify product list is visible
2. Create/select customer
3. Create sale and collect payment
4. Print/download invoice
5. Handle remaining dues via add payment
6. Cancel wrong sales only through system action
7. Close shift with cash/digital reconciliation

---

## 5) Current Scope Statement

Your system is now running as a **Standard POS-first backend**.

- Primary active business flow: **Inventory Masters -> Sales -> Payments -> Invoices**
- Non-POS rider/provider workflows have been removed from active route surface and related POS layers.

If you want, I can also create a second markdown file with a visual API map (endpoint-by-endpoint) for your cashier and frontend developer.