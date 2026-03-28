# Cashier Guidance - Karyana POS

This document explains exactly how a cashier should use the POS system during daily operations.

Scope of this guide:
- Sales counter operations only
- Customer, sale, payment, invoice, cancellation, and shift close only
- Excludes supplier, purchase, and rider/provider workflows

Standard POS mode note:
- Supplier/provider and rider flows are disabled from cashier-facing API routes.
- Cashiers should only use customers, sales, payments, cancellations, and invoices.
- Rider-based `/api/v1/items` flow is disabled in POS mode because it depends on rider_id.

## 1. Purpose

Use this guide for:
- Opening counter
- Creating walk-in and regular customer sales
- Taking full and partial payments
- Printing or downloading invoices
- Handling mistakes safely
- Closing shift with reconciliation

## 2. Before You Start

Make sure:
1. Your account is active and you can log in.
2. Counter internet and printer are working.
3. Products are visible in POS with prices.
4. A walk-in customer exists (or initialize one).

## 3. Shift Start SOP

### Step 1: Login
- Login with your cashier credentials.
- Confirm your name and role after login.

### Step 2: Initialize Walk-in Customer (once per branch setup)
- Action: Initialize default walk-in customer.
- API used by system: POST /api/v1/sales/customers/walk-in/init
- Expected result: success true and customer_type walk_in.

### Step 3: Quick Health Check
- Open customer list and sales list screens.
- Confirm they load successfully.
- If not loading, report to manager before billing starts.

## 4. Create Sale SOP (Most Common Flow)

### Step 1: Select Customer
- Walk-in buyer: choose Walk-in Customer.
- Regular buyer: search and select existing customer.
- New regular buyer: create customer first, then continue sale.

### Step 2: Add Items
- Scan barcode or search product.
- Enter quantity correctly.
- Verify unit price shown on screen.
- Apply discount only if policy allows.

### Step 3: Confirm Bill
- Confirm line totals.
- Confirm subtotal, discount, tax, and grand total.
- Ask customer to verify total before payment.

### Step 4: Take Payment
- Full payment: paid amount equals grand total.
- Partial payment: paid amount less than grand total.
- Choose correct payment method: cash, bank_transfer, easypaisa, jazzcash, card, credit.

### Step 5: Submit Sale
- System creates sale and deducts stock automatically.
- FIFO is handled by backend, cashier does not choose batches.

### Step 6: Provide Invoice
- Printable data endpoint: GET /api/v1/sales/sales/{sale_id}/invoice
- PDF endpoint: GET /api/v1/sales/sales/{sale_id}/invoice/pdf

## 5. Add Payment to Existing Sale SOP

Use this when customer pays later for an unpaid or partially paid invoice.

### Steps
1. Open sale details.
2. Click Add Payment.
3. Enter payment date, amount, method, and reference.
4. Save.
5. Confirm remaining amount updated.

API used by system:
- POST /api/v1/sales/sales/{sale_id}/payments

## 6. Create Customer SOP

Create customer when buyer wants credit history or future follow-up.

### Steps
1. Open customer create form.
2. Enter name and phone (phone should be unique).
3. Set customer_type:
   - walk_in
  - regular
4. Set opening balance if provided by manager/accounts.
5. Save and verify customer appears in list.

API used by system:
- POST /api/v1/sales/customers

## 7. Cancel Wrong Sale SOP

Do this if wrong item/quantity/price was billed.

### Rules
- Never edit database directly.
- Never ignore wrong sale.
- Always cancel wrong sale in system, then create correct sale.

### Steps
1. Open wrong sale.
2. Click Cancel Sale.
3. Confirm cancellation.
4. Recreate correct sale.

API used by system:
- POST /api/v1/sales/sales/{sale_id}/cancel

## 8. How to Read Payment Status

- unpaid: customer paid 0
- partially_paid: customer paid some amount, remaining > 0
- paid: total paid covers grand total

Tip:
- If remaining is negative, customer has extra credit.

## 9. Cashier Do and Do Not

### Do
- Verify customer before saving sale.
- Verify quantity before payment.
- Use Add Payment for later collections.
- Use Cancel Sale for mistakes.
- Keep payment references for non-cash methods.

### Do Not
- Do not manually adjust stock for a sale mistake.
- Do not share cashier credentials.
- Do not delete records outside system process.
- Do not mark cash as card or card as cash.

## 10. Common Error Handling

### Duplicate phone while creating customer
- Meaning: phone already exists.
- Action: search existing customer and use that profile.

### Insufficient stock
- Meaning: requested quantity not available.
- Action: reduce quantity or remove item and inform customer.

### Sale not found while adding payment/cancel
- Meaning: invalid or old sale reference.
- Action: refresh list and search by sale number.

### Invoice PDF does not open
- Retry invoice endpoint.
- If still failing, use printable invoice data view and inform support.

## 11. End of Shift SOP

### Reconciliation Checklist
1. Count total invoices created in your shift.
2. Reconcile cash collected with cash sales.
3. Reconcile digital collections with references.
4. List unpaid and partially paid invoices.
5. Submit shift handover to manager.

### Must Report to Manager
- Any duplicate payment incident
- Any repeated cancellation pattern
- Any network outage with manual billing

## 12. Quick API Map (Reference)

### Customers
- POST /api/v1/sales/customers
- GET /api/v1/sales/customers
- GET /api/v1/sales/customers/{customer_id}
- PUT /api/v1/sales/customers/{customer_id}
- POST /api/v1/sales/customers/walk-in/init

### Sales
- POST /api/v1/sales/sales
- GET /api/v1/sales/sales
- GET /api/v1/sales/sales/{sale_id}
- POST /api/v1/sales/sales/{sale_id}/payments
- POST /api/v1/sales/sales/{sale_id}/cancel
- GET /api/v1/sales/sales/{sale_id}/invoice
- GET /api/v1/sales/sales/{sale_id}/invoice/pdf

## 13. Standard Response Format

All successful endpoints follow this structure:

{
  "success": true,
  "message": "Human-readable message",
  "data": { ... }
}

If operation fails, success is false and error detail is provided by backend.

## 14. Fast Daily Checklist for Cashier

### Opening
- Login successful
- Walk-in customer ready
- Product list visible
- Printer test done

### During shift
- Correct customer selected
- Correct quantity entered
- Payment method recorded correctly
- Invoice shared after every sale

### Closing
- Cash and digital totals reconciled
- Pending dues list noted
- Incidents reported

---

Owner: POS Operations
Last Updated: 2026-03-28
