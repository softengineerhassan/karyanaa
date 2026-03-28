#!/usr/bin/env python3
"""Test Sales API via HTTP endpoints"""
import requests
import json
from decimal import Decimal
from datetime import date

BASE_URL = "http://127.0.0.1:8009/api/v1/sales"

def test_api():
    print("\n=== TESTING SALES API VIA HTTP ===\n")
    
    # Test 1: Get existing customers
    print("Test 1: GET /customers")
    response = requests.get(f"{BASE_URL}/customers")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        customers = response.json()
        print(f"✓ Retrieved {len(customers)} customers")
        if customers:
            print(f"  First customer: {customers[0].get('name')}")
    else:
        print(f"✗ Error: {response.text}")
    
    # Test 2: Create a new customer
    print("\nTest 2: POST /customers")
    customer_data = {
        "name": "API Test Customer",
        "phone": "+923334445666",
        "email": "test@example.com",
        "address": "Test Street",
        "city": "Karachi",
        "opening_balance": "1000.00",
        "customer_type": "regular",
        "notes": "Created via API test"
    }
    response = requests.post(f"{BASE_URL}/customers", json=customer_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200 or response.status_code == 201:
        customer = response.json()
        print(f"✓ Created customer: {customer.get('name')}")
        customer_id = customer.get('id')
    else:
        print(f"✗ Error: {response.text}")
        return
    
    # Test 3: Get customer details
    print(f"\nTest 3: GET /customers/{customer_id}")
    response = requests.get(f"{BASE_URL}/customers/{customer_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        customer = response.json()
        print(f"✓ Retrieved customer: {customer.get('name')}")
        print(f"  Balance: {customer.get('current_balance')}")
    else:
        print(f"✗ Error: {response.text}")
    
    # Test 4: Get sales list
    print("\nTest 4: GET /sales")
    response = requests.get(f"{BASE_URL}/sales")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        sales = response.json()
        print(f"✓ Retrieved {len(sales)} sales")
        if sales:
            print(f"  First sale: {sales[0].get('sale_number')}")
            sale_id = sales[0].get('id')
            
            # Test 5: Get sale details
            print(f"\nTest 5: GET /sales/{sale_id}")
            response = requests.get(f"{BASE_URL}/sales/{sale_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                sale = response.json()
                print(f"✓ Retrieved sale: {sale.get('sale_number')}")
                print(f"  Total: {sale.get('grand_total')}")
                print(f"  Status: {sale.get('payment_status')}")
            else:
                print(f"✗ Error: {response.text}")
    else:
        print(f"✗ Error: {response.text}")
    
    # Test 6: Get documentation
    print("\nTest 6: GET /docs (API Documentation)")
    response = requests.get("http://127.0.0.1:8009/docs")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ SwaggerUI documentation available at http://127.0.0.1:8009/docs")
    else:
        print(f"✗ Could not access documentation")
    
    print("\n=== API TESTS COMPLETED ===\n")

if __name__ == "__main__":
    test_api()
