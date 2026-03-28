#!/usr/bin/env python3
"""Test all API endpoints for StandardResponse compliance"""
import requests
import json

BASE_URL = "http://127.0.0.1:8009/api/v1"

def test_endpoint(method, path, expected_status=200):
    """Test an endpoint and verify StandardResponse format"""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=5)
        else:
            return None
            
        if response.status_code == expected_status:
            data = response.json()
            # Check if response has StandardResponse structure
            has_success = 'success' in data
            has_message = 'message' in data
            has_data = 'data' in data
            
            if has_success and has_message and has_data is not None:
                return "✅"
            else:
                return f"⚠️  Missing field: success={has_success}, message={has_message}, data={has_data}"
        else:
            return f"⚠️  Status: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)[:50]}"

def main():
    print("\n" + "="*80)
    print("TESTING ALL API ENDPOINTS FOR STANDARDRESPONSE COMPLIANCE")
    print("="*80 + "\n")
    
    endpoints = {
        "Auth": [
            ("POST", "/auth/login"),
            ("POST", "/auth/register"),
            ("GET", "/auth/me"),
        ],
        "Users": [
            ("GET", "/users"),
            ("POST", "/users"),
            ("GET", "/users"),
        ],
        "Inventory - Categories": [
            ("GET", "/inventory/categories"),
            ("POST", "/inventory/categories"),
        ],
        "Inventory - Products": [
            ("GET", "/inventory/products"),
            ("POST", "/inventory/products"),
        ],
        "Inventory - Suppliers": [
            ("GET", "/inventory/suppliers"),
            ("POST", "/inventory/suppliers"),
        ],
        "Inventory - Units": [
            ("GET", "/inventory/units"),
            ("POST", "/inventory/units"),
        ],
        "Inventory - Purchases": [
            ("GET", "/inventory/purchases"),
            ("POST", "/inventory/purchases"),
        ],
        "Inventory - Stock Movements": [
            ("GET", "/inventory/stock-movements"),
        ],
        "Riders": [
            ("GET", "/riders"),
            ("POST", "/riders"),
        ],
        "Items": [
            ("GET", "/items"),
            ("POST", "/items"),
        ],
        "Sales - Customers": [
            ("GET", "/sales/customers"),
            ("POST", "/sales/customers"),
        ],
        "Sales - Sales": [
            ("GET", "/sales/sales"),
            ("POST", "/sales/sales"),
        ],
    }
    
    total = 0
    passed = 0
    
    for category, endpoint_list in endpoints.items():
        print(f"\n📦 {category}")
        print("-" * 80)
        
        for method, path in endpoint_list:
            result = test_endpoint(method, path)
            if result:
                total += 1
                if result == "✅":
                    passed += 1
                    status = "✅ PASS"
                else:
                    status = f"⚠️  {result}"
                print(f"  {method:6} {path:45} {status}")
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed}/{total} endpoints using StandardResponse")
    print("="*80 + "\n")
    
    if passed == total:
        print("✅ ALL ENDPOINTS COMPLIANT WITH STANDARDRESPONSE FORMAT!")
    else:
        print(f"⚠️  {total - passed} endpoint(s) need StandardResponse wrapper")

if __name__ == "__main__":
    main()
