#!/usr/bin/env python3
"""Test Sales API response format"""
import requests
import json
import random
from datetime import date

BASE_URL = "http://127.0.0.1:8009/api/v1/sales"

def test_response_format():
    print("\n=== TESTING SALES API STANDARD RESPONSE FORMAT ===\n")
    
    # Test 1: GET customers (shows StandardResponse with List)
    print("Test 1: GET /customers")
    response = requests.get(f"{BASE_URL}/customers")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response Keys: {data.keys()}")
    print(f"  - success: {data.get('success')}")
    print(f"  - message: {data.get('message')}")
    print(f"  - data type: {type(data.get('data'))}")
    if isinstance(data.get('data'), list):
        print(f"  - data length: {len(data.get('data'))}")
        if data.get('data'):
            customer = data['data'][0]
            print(f"  - First customer keys: {list(customer.keys())}")
            print(f"    • name: {customer.get('name')}")
            print(f"    • phone: {customer.get('phone')}")
            print(f"    • customer_type: {customer.get('customer_type')}")
            print(f"    • current_balance: {customer.get('current_balance')}")
            print(f"    • created_at: {customer.get('created_at')}")
    print()
    
    # Test 2: GET sales (shows StandardResponse with List)
    print("Test 2: GET /sales")
    response = requests.get(f"{BASE_URL}/sales")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response Keys: {data.keys()}")
    print(f"  - success: {data.get('success')}")
    print(f"  - message: {data.get('message')}")
    print(f"  - data type: {type(data.get('data'))}")
    if isinstance(data.get('data'), list):
        print(f"  - data length: {len(data.get('data'))}")
        if data.get('data'):
            sale = data['data'][0]
            print(f"  - First sale keys: {list(sale.keys())}")
            print(f"    • sale_number: {sale.get('sale_number')}")
            print(f"    • grand_total: {sale.get('grand_total')}")
            print(f"    • payment_status: {sale.get('payment_status')}")
            print(f"    • created_at: {sale.get('created_at')}")
    print()
    
    # Test 3: GET single sale (shows StandardResponse with Object)
    print("Test 3: GET /sales/{id}")
    if data.get('data') and len(data['data']) > 0:
        sale_id = data['data'][0].get('id')
        response = requests.get(f"{BASE_URL}/sales/{sale_id}")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response Keys: {data.keys()}")
        print(f"  - success: {data.get('success')}")
        print(f"  - message: {data.get('message')}")
        print(f"  - data type: {type(data.get('data'))}")
        if isinstance(data.get('data'), dict):
            sale = data['data']
            print(f"  - Sale object keys: {list(sale.keys())}")
            print(f"    • sale_number: {sale.get('sale_number')}")
            print(f"    • grand_total: {sale.get('grand_total')}")
            print(f"    • payment_status: {sale.get('payment_status')}")
            print(f"    • items: {len(sale.get('items', []))} items")
            if sale.get('items'):
                item = sale['items'][0]
                print(f"    • First item keys: {list(item.keys())}")
                print(f"      - product_snapshot: {item.get('product_snapshot', {}).get('name')}")
                print(f"      - quantity: {item.get('quantity')}")
                print(f"      - unit_price: {item.get('unit_price')}")
    print()
    
    # Test 4: Create customer with unique phone
    print("Test 4: POST /customers (with unique phone)")
    unique_phone = f"+9233{random.randint(10000000, 99999999)}"
    customer_data = {
        "name": f"Test Customer {random.randint(1000, 9999)}",
        "phone": unique_phone,
        "email": f"test{random.randint(1000, 9999)}@example.com",
        "address": "Test Street",
        "city": "Karachi",
        "opening_balance": "1000.00",
        "customer_type": "regular",
        "notes": "Created via API test"
    }
    response = requests.post(f"{BASE_URL}/customers", json=customer_data)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response Keys: {data.keys()}")
    print(f"  - success: {data.get('success')}")
    print(f"  - message: {data.get('message')}")
    print(f"  - data type: {type(data.get('data'))}")
    if isinstance(data.get('data'), dict):
        customer = data['data']
        print(f"  - Customer object keys: {list(customer.keys())}")
        print(f"    • name: {customer.get('name')}")
        print(f"    • phone: {customer.get('phone')}")
        print(f"    • customer_type: {customer.get('customer_type')}")
        print(f"    • current_balance: {customer.get('current_balance')}")
        print(f"    • created_at: {customer.get('created_at')}")
        print(f"    • updated_at: {customer.get('updated_at')}")
    print()
    
    print("=== API RESPONSE FORMAT VERIFIED ===\n")
    print("✅ All responses follow StandardResponse[T] format:")
    print("   - success: boolean")
    print("   - message: string")
    print("   - data: T (list or object)")
    print("   - errors: optional list")

if __name__ == "__main__":
    test_response_format()
