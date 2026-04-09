# Flutter Guide: Search and Date Filters for Riders (Providers) and Purchase Items

This guide is for Flutter developers integrating rider provider search and rider purchase item date filters.

## Base URL and Auth

- Base path: `/api/v1`
- Auth: Send bearer token in `Authorization` header.

```http
Authorization: Bearer <access_token>
```

## 1) Rider Provider Search API

Use this endpoint to search rider providers (rider profiles).

### Endpoint

```http
GET /api/v1/riders
```

### Query Params

- `search` (optional, string): partial text match on rider full name.

### Example

```http
GET /api/v1/riders?search=ali
```

### Success Response Shape

```json
{
  "success": true,
  "message": "Rider profiles fetched successfully",
  "data": [
    {
      "id": "uuid",
      "owner_user_id": "uuid",
      "full_name": "Ali Raza",
      "phone_number": "03001234567",
      "email": "ali@example.com",
      "profile_image": null,
      "created_at": "2026-04-09T09:10:00",
      "updated_at": "2026-04-09T09:10:00"
    }
  ]
}
```

## 2) Rider Purchase Items Search + Date Filters API

Use this endpoint to fetch purchase items with optional search and date range.

### Endpoint

```http
GET /api/v1/rider-purchase-items
```

### Query Params

- `search` (optional, string): matches rider full name OR item name.
- `rider_profile_id` (optional, UUID): filter items for one rider provider.
- `start_date` (optional, `YYYY-MM-DD`): includes records with `purchase_date >= start_date`.
- `end_date` (optional, `YYYY-MM-DD`): includes records with `purchase_date <= end_date`.

Date filters are inclusive on both sides.

### Example

```http
GET /api/v1/rider-purchase-items?search=bag&rider_profile_id=8a05f046-8d9b-4500-ae50-4fc29b7ddf88&start_date=2026-04-01&end_date=2026-04-09
```

### Success Response Shape

```json
{
  "success": true,
  "message": "Rider purchase items fetched successfully",
  "data": [
    {
      "id": "uuid",
      "owner_user_id": "uuid",
      "rider_profile_id": "uuid",
      "item_name": "Delivery Bag",
      "item_code": "DB-001",
      "barcode": null,
      "category": "Accessories",
      "brand": "Local",
      "quantity": 2.0,
      "unit": "pcs",
      "unit_size": null,
      "unit_price": 1500.0,
      "cost_price": 1200.0,
      "total_amount": 3000.0,
      "total_price": 3000.0,
      "purchase_date": "2026-04-06",
      "expiry_date": null,
      "batch_number": null,
      "supplier_name": "ABC Traders",
      "supplier_contact": "03001112222",
      "status": "delivered",
      "payment_status": "paid",
      "notes": null,
      "created_by": "uuid",
      "created_at": "2026-04-06T10:30:00",
      "updated_at": "2026-04-06T10:30:00"
    }
  ]
}
```

## Flutter Integration (Provider package)

## Filter model

```dart
class RiderPurchaseItemFilter {
  final String? search;
  final String? riderProfileId;
  final DateTime? startDate;
  final DateTime? endDate;

  const RiderPurchaseItemFilter({
    this.search,
    this.riderProfileId,
    this.startDate,
    this.endDate,
  });
}
```

## API service

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';

class RiderApiService {
  RiderApiService({required this.baseUrl, required this.token});

  final String baseUrl;
  final String token;
  final _dateFmt = DateFormat('yyyy-MM-dd');

  Map<String, String> get _headers => {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      };

  Future<List<dynamic>> fetchRiders({String? search}) async {
    final query = <String, String>{};
    if (search != null && search.trim().isNotEmpty) {
      query['search'] = search.trim();
    }

    final uri = Uri.parse('$baseUrl/api/v1/riders').replace(queryParameters: query);
    final res = await http.get(uri, headers: _headers);

    if (res.statusCode >= 200 && res.statusCode < 300) {
      final body = jsonDecode(res.body) as Map<String, dynamic>;
      return (body['data'] as List<dynamic>? ?? []);
    }
    throw Exception('Failed to fetch riders: ${res.body}');
  }

  Future<List<dynamic>> fetchRiderPurchaseItems(RiderPurchaseItemFilter filter) async {
    final query = <String, String>{};

    if (filter.search != null && filter.search!.trim().isNotEmpty) {
      query['search'] = filter.search!.trim();
    }
    if (filter.riderProfileId != null && filter.riderProfileId!.isNotEmpty) {
      query['rider_profile_id'] = filter.riderProfileId!;
    }
    if (filter.startDate != null) {
      query['start_date'] = _dateFmt.format(filter.startDate!);
    }
    if (filter.endDate != null) {
      query['end_date'] = _dateFmt.format(filter.endDate!);
    }

    final uri = Uri.parse('$baseUrl/api/v1/rider-purchase-items').replace(queryParameters: query);
    final res = await http.get(uri, headers: _headers);

    if (res.statusCode >= 200 && res.statusCode < 300) {
      final body = jsonDecode(res.body) as Map<String, dynamic>;
      return (body['data'] as List<dynamic>? ?? []);
    }
    throw Exception('Failed to fetch purchase items: ${res.body}');
  }
}
```

## ChangeNotifier provider

```dart
import 'package:flutter/foundation.dart';

class RiderPurchaseItemProvider extends ChangeNotifier {
  RiderPurchaseItemProvider(this.api);

  final RiderApiService api;

  bool loadingRiders = false;
  bool loadingItems = false;
  String? error;

  List<dynamic> riders = [];
  List<dynamic> items = [];

  String? selectedRiderId;
  String search = '';
  DateTime? startDate;
  DateTime? endDate;

  Future<void> loadRiders({String? q}) async {
    loadingRiders = true;
    error = null;
    notifyListeners();
    try {
      riders = await api.fetchRiders(search: q ?? search);
    } catch (e) {
      error = e.toString();
    } finally {
      loadingRiders = false;
      notifyListeners();
    }
  }

  Future<void> loadItems() async {
    loadingItems = true;
    error = null;
    notifyListeners();
    try {
      items = await api.fetchRiderPurchaseItems(
        RiderPurchaseItemFilter(
          search: search,
          riderProfileId: selectedRiderId,
          startDate: startDate,
          endDate: endDate,
        ),
      );
    } catch (e) {
      error = e.toString();
    } finally {
      loadingItems = false;
      notifyListeners();
    }
  }

  Future<void> applyFilters({
    String? newSearch,
    String? newRiderId,
    DateTime? newStartDate,
    DateTime? newEndDate,
  }) async {
    search = newSearch ?? search;
    selectedRiderId = newRiderId ?? selectedRiderId;
    startDate = newStartDate ?? startDate;
    endDate = newEndDate ?? endDate;
    await loadItems();
  }

  Future<void> clearFilters() async {
    search = '';
    selectedRiderId = null;
    startDate = null;
    endDate = null;
    await loadItems();
  }
}
```

## Quick Notes for Flutter Team

- Use `yyyy-MM-dd` format only for `start_date` and `end_date`.
- If you send invalid UUID in `rider_profile_id`, API returns `422` validation error.
- If rider does not belong to logged-in owner, API returns `400` with message like `Rider profile not found`.
- Apply local debounce for search input (for example 300 to 500 ms) before calling API.
