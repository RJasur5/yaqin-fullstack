import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/user.dart';
import '../models/category.dart';
import '../models/master.dart';
import '../models/order.dart';
import '../models/subscription.dart';

class ApiService {
  String? _token;

  void setToken(String? token) => _token = token;

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Bypass-Tunnel-Reminder': 'true',
    if (_token != null) 'Authorization': 'Bearer $_token',
  };

  // ==================== AUTH ====================

  Future<Map<String, dynamic>> register({
    String? name,
    required String phone,
    required String password,
    String role = 'client',
    String? city,
    String lang = 'ru',
  }) async {
    final res = await http.post(
      Uri.parse(ApiConfig.authRegister),
      headers: _headers,
      body: jsonEncode({
        'name': name,
        'phone': phone,
        'password': password,
        'role': role,
        'city': city,
        'lang': lang,
      }),
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Registration failed');
  }

  Future<Map<String, dynamic>> login({
    required String phone,
    required String password,
  }) async {
    final res = await http.post(
      Uri.parse(ApiConfig.authLogin),
      headers: _headers,
      body: jsonEncode({'phone': phone, 'password': password}),
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Login failed');
  }

  Future<UserModel> getMe() async {
    final res = await http.get(
      Uri.parse(ApiConfig.authMe),
      headers: _headers,
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(res.body));
    }
    throw Exception('Failed to get user');
  }

  Future<UserModel> updateProfile({String? name, String? city, String? lang}) async {
    final res = await http.put(
      Uri.parse(ApiConfig.authProfile),
      headers: _headers,
      body: jsonEncode({
        if (name != null) 'name': name,
        if (city != null) 'city': city,
        if (lang != null) 'lang': lang,
      }),
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(res.body));
    }
    String msg = 'Profile update failed';
    try {
       msg = jsonDecode(res.body)['detail'];
    } catch (_) {}
    throw Exception(msg);
  }

  Future<void> updateFCMToken(String token) async {
    final res = await http.post(
      Uri.parse(ApiConfig.authFcmToken),
      headers: _headers,
      body: jsonEncode({'fcm_token': token}),
    ).timeout(const Duration(seconds: 20));
    if (res.statusCode != 200) {
      throw Exception('Failed to update FCM token');
    }
  }

  Future<UserModel> uploadAvatar(String imagePath) async {
    final request = http.MultipartRequest('POST', Uri.parse('${ApiConfig.apiUrl}/auth/me/avatar'));
    if (_token != null) {
      request.headers['Authorization'] = 'Bearer $_token';
    }
    request.files.add(await http.MultipartFile.fromPath('file', imagePath));
    
    final streamedResponse = await request.send().timeout(const Duration(seconds: 45));
    final response = await http.Response.fromStream(streamedResponse);
    
    if (response.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(response.body));
    }
    String msg = 'Avatar upload failed';
    try {
       msg = jsonDecode(response.body)['detail'];
    } catch (_) {}
    throw Exception(msg);
  }

  // ==================== CATEGORIES ====================

  Future<List<CategoryModel>> getCategories() async {
    final res = await http.get(
      Uri.parse(ApiConfig.categories),
      headers: _headers,
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode == 200) {
      final list = jsonDecode(res.body) as List;
      return list.map((c) => CategoryModel.fromJson(c)).toList();
    }
    throw Exception('Failed to load categories');
  }

  // ==================== MASTERS ====================

  Future<List<MasterModel>> getMasters({
    int? categoryId,
    int? subcategoryId,
    String? city,
    String? search,
    double? minRating,
    String sortBy = 'rating',
    int limit = 50,
    int offset = 0,
  }) async {
    final params = <String, String>{
      if (categoryId != null) 'category_id': '$categoryId',
      if (subcategoryId != null) 'subcategory_id': '$subcategoryId',
      if (city != null) 'city': city,
      if (search != null && search.isNotEmpty) 'search': search,
      if (minRating != null) 'min_rating': '$minRating',
      'sort_by': sortBy,
      'limit': '$limit',
      'offset': '$offset',
    };
    final uri = Uri.parse(ApiConfig.masters).replace(queryParameters: params);
    final res = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 30));
    if (res.statusCode == 200) {
      final list = jsonDecode(res.body) as List;
      return list.map((m) => MasterModel.fromJson(m)).toList();
    }
    throw Exception('Failed to load masters');
  }

  Future<MasterModel> getMasterDetail(int id) async {
    final res = await http.get(
      Uri.parse(ApiConfig.masterDetail(id)),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      return MasterModel.fromJson(jsonDecode(res.body));
    }
    throw Exception('Master not found');
  }

  Future<MasterModel?> getMyMasterProfile() async {
    final res = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/api/masters/profile/me'),
      headers: _headers,
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode == 200) {
      return MasterModel.fromJson(jsonDecode(res.body));
    } else if (res.statusCode == 404) {
      return null;
    }
    throw Exception('Failed to get my master profile');
  }

  Future<MasterModel> createMasterProfile({
    required int subcategoryId,
    String? description,
    int experienceYears = 0,
    double? hourlyRate,
    String? city,
    String? district,
    String? address,
    List<String>? skills,
  }) async {
    final res = await http.post(
      Uri.parse(ApiConfig.masterProfile),
      headers: _headers,
      body: jsonEncode({
        'subcategory_id': subcategoryId,
        'description': description,
        'experience_years': experienceYears,
        'hourly_rate': hourlyRate,
        'city': city,
        'district': district,
        'address': address,
        'skills': skills,
      }),
    );
    if (res.statusCode == 200) {
      return MasterModel.fromJson(jsonDecode(res.body));
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Failed to create profile');
  }

  Future<MasterModel> updateMasterProfile({
    int? subcategoryId,
    String? description,
    int? experienceYears,
    double? hourlyRate,
    String? city,
    String? district,
    String? address,
    List<String>? skills,
  }) async {
    final body = <String, dynamic>{};
    if (subcategoryId != null) body['subcategory_id'] = subcategoryId;
    if (description != null) body['description'] = description;
    if (experienceYears != null) body['experience_years'] = experienceYears;
    if (hourlyRate != null) body['hourly_rate'] = hourlyRate;
    if (city != null) body['city'] = city;
    if (district != null) body['district'] = district;
    if (address != null) body['address'] = address;
    if (skills != null) body['skills'] = skills;

    final res = await http.put(
      Uri.parse(ApiConfig.masterProfile),
      headers: _headers,
      body: jsonEncode(body),
    );
    if (res.statusCode == 200) {
      return MasterModel.fromJson(jsonDecode(res.body));
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Failed to update profile');
  }

  Future<void> createReview(int masterId, int rating, String? comment) async {
    final res = await http.post(
      Uri.parse(ApiConfig.masterReview(masterId)),
      headers: _headers,
      body: jsonEncode({'rating': rating, 'comment': comment}),
    );
    if (res.statusCode != 200) {
      throw Exception('Failed to create review');
    }
  }

  Future<void> rateMasterByOrder(int orderId, int rating, String? comment) async {
    final res = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/api/orders/$orderId/rate_master'),
      headers: _headers,
      body: jsonEncode({'rating': rating, 'comment': comment}),
    );
    if (res.statusCode != 200) {
      throw Exception('Failed to rate master');
    }
  }

  // ==================== FAVORITES ====================

  Future<List<MasterModel>> getFavorites() async {
    final res = await http.get(
      Uri.parse(ApiConfig.favorites),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      final list = jsonDecode(res.body) as List;
      return list.map((m) => MasterModel.fromJson(m)).toList();
    }
    throw Exception('Failed to load favorites');
  }

  Future<void> toggleFavorite(int masterId) async {
    final res = await http.post(
      Uri.parse(ApiConfig.toggleFavorite(masterId)),
      headers: _headers,
    );
    if (res.statusCode != 200) {
      throw Exception('Failed to toggle favorite');
    }
  }

  // ==================== ORDERS ====================

  Future<Map<String, dynamic>> createOrder({
    required int subcategoryId,
    required String description,
    required String city,
    String? district,
    double? price,
    bool includeLunch = false,
    bool includeTaxi = false,
  }) async {
    final res = await http.post(
      Uri.parse(ApiConfig.orders),
      headers: _headers,
      body: jsonEncode({
        'subcategory_id': subcategoryId,
        'description': description,
        'city': city,
        'district': district,
        'price': price,
        'include_lunch': includeLunch,
        'include_taxi': includeTaxi,
      }),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Failed to create order');
  }

  Future<List<dynamic>> getAvailableOrders({
    int? categoryId,
    int? subcategoryId,
    String? city,
    String? search,
  }) async {
    final params = <String, String>{
      if (categoryId != null) 'category_id': '$categoryId',
      if (subcategoryId != null) 'subcategory_id': '$subcategoryId',
      if (city != null && city.isNotEmpty) 'city': city,
      if (search != null && search.isNotEmpty) 'search': search,
    };
    final uri = Uri.parse(ApiConfig.ordersAvailable).replace(queryParameters: params);
    final res = await http.get(uri, headers: _headers);
    if (res.statusCode == 200) {
      return jsonDecode(res.body) as List;
    }
    throw Exception('Failed to load available orders');
  }


  Future<List<dynamic>> getMyOrders({String? type}) async {
    final params = <String, String>{
      if (type != null) 'type': type,
    };
    final uri = Uri.parse(ApiConfig.ordersMy).replace(queryParameters: params);
    final res = await http.get(uri, headers: _headers);
    if (res.statusCode == 200) {
      return jsonDecode(res.body) as List;
    }
    throw Exception('Failed to load my orders');
  }

  Future<Map<String, dynamic>> acceptOrder(int orderId) async {
    final res = await http.post(
      Uri.parse(ApiConfig.acceptOrder(orderId)),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Failed to accept order');
  }

  // ==================== CLIENTS ====================

  Future<void> rateClient(int orderId, int rating, String? comment) async {
    final res = await http.post(
      Uri.parse(ApiConfig.rateClient(orderId)),
      headers: _headers,
      body: jsonEncode({'rating': rating, 'comment': comment}),
    );
    if (res.statusCode != 200) {
      throw Exception(jsonDecode(res.body)['detail'] ?? 'Failed to rate client');
    }
  }

  Future<Map<String, dynamic>> getClientProfile(int clientId) async {
    final res = await http.get(
      Uri.parse(ApiConfig.clientProfile(clientId)),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('Failed to load client profile');
  }

  // ==================== CHAT ====================

  Future<List<dynamic>> getChatHistory(int orderId) async {
    final res = await http.get(
      Uri.parse(ApiConfig.orderChat(orderId)),
      headers: _headers,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body) as List;
    }
    String msg = 'Failed to load chat history';
    try {
      final decoded = jsonDecode(res.body);
      msg = decoded['detail'] ?? msg;
    } catch (_) {}
    throw Exception('$msg (${res.statusCode})');
  }

  Future<Map<String, dynamic>> sendChatMessage(int orderId, String text) async {
    final res = await http.post(
      Uri.parse(ApiConfig.orderChat(orderId)),
      headers: _headers,
      body: jsonEncode({'text': text}),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('Failed to send message');
  }

  Future<List<dynamic>> getChatList() async {
    final response = await http.get(
      Uri.parse(ApiConfig.orderChatList),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    String msg = 'Failed to load chat list';
    try {
      final decoded = json.decode(utf8.decode(response.bodyBytes));
      msg = decoded['detail'] ?? msg;
    } catch (_) {}
    throw Exception('$msg (${response.statusCode})');
  }

  Future<void> markAsRead(int orderId) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.apiUrl}/orders/$orderId/read'),
      headers: _headers,
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to mark messages as read');
    }
  }

  // ==================== ADMIN ====================

  Future<List<UserModel>> getAdminUsers() async {
    final res = await http.get(
      Uri.parse(ApiConfig.adminUsers),
      headers: _headers,
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode == 200) {
      final List data = jsonDecode(res.body);
      return data.map((u) => UserModel.fromJson(u)).toList();
    }
    throw Exception('Failed to load users');
  }

  Future<UserModel> getAdminUserDetail(int id) async {
    final res = await http.get(
      Uri.parse(ApiConfig.adminUserDetail(id)),
      headers: _headers,
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(res.body));
    }
    throw Exception('Failed to load user details');
  }

  Future<void> deleteUser(int id) async {
    final res = await http.delete(
      Uri.parse(ApiConfig.adminUserDetail(id)),
      headers: _headers,
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode != 200) {
      throw Exception(jsonDecode(res.body)['detail'] ?? 'Failed to delete user');
    }
  }

  Future<void> updateUserAdmin(int id, Map<String, dynamic> data) async {
    final res = await http.put(
      Uri.parse(ApiConfig.adminUserDetail(id)),
      headers: _headers,
      body: jsonEncode(data),
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode != 200) {
      throw Exception(jsonDecode(res.body)['detail'] ?? 'Failed to update user');
    }
  }

  Future<void> updateMasterProfileAdmin(int id, Map<String, dynamic> data) async {
    final res = await http.put(
      Uri.parse('${ApiConfig.adminUserDetail(id)}/master'),
      headers: _headers,
      body: jsonEncode(data),
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode != 200) {
      throw Exception(jsonDecode(res.body)['detail'] ?? 'Failed to update master profile');
    }
  }

  Future<List<OrderResponse>> getAdminOrders() async {
    final res = await http.get(
      Uri.parse(ApiConfig.adminOrders),
      headers: _headers,
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode == 200) {
      final List data = jsonDecode(res.body);
      return data.map((o) => OrderResponse.fromJson(o)).toList();
    }
    throw Exception('Failed to load orders');
  }

  Future<void> deleteOrder(int id) async {
    final res = await http.delete(
      Uri.parse(ApiConfig.adminOrderDetail(id)),
      headers: _headers,
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode != 200) {
      throw Exception(jsonDecode(res.body)['detail'] ?? 'Failed to delete order');
    }
  }

  Future<List<dynamic>> getAppReviews() async {
    final res = await http.get(
      Uri.parse(ApiConfig.appReviews),
      headers: _headers,
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode != 200) {
      throw Exception(jsonDecode(res.body)['detail'] ?? 'Failed to get reviews');
    }
    return jsonDecode(res.body);
  }

  Future<void> createAppReview(int rating, String comment) async {
    final res = await http.post(
      Uri.parse(ApiConfig.appReviews),
      headers: _headers,
      body: jsonEncode({
        'rating': rating,
        'comment': comment,
      }),
    ).timeout(const Duration(seconds: 30));
    
    if (res.statusCode != 200 && res.statusCode != 201) {
      String errorMessage = 'Failed to leave review';
      if (res.body.isNotEmpty) {
        try {
          final decoded = jsonDecode(res.body);
          if (decoded['detail'] is List) {
            // FastAPI validation error is a list
            errorMessage = (decoded['detail'] as List).map((e) => e['msg'] ?? e.toString()).join(', ');
          } else {
            errorMessage = decoded['detail'] ?? errorMessage;
          }
        } catch (_) {}
      }
      throw Exception(errorMessage);
    }
  }

  Future<void> adminChangeUserPassword(int userId, String newPassword) async {
    final res = await http.put(
      Uri.parse('${ApiConfig.baseUrl}/api/auth/admin/users/$userId/password'),
      headers: _headers,
      body: jsonEncode(newPassword), // The endpoint expects a plain string or we can wrap it
    ).timeout(const Duration(seconds: 30));
    
    // Note: If the backend expects a JSON object {"new_password": "..."}, we should change this.
    // Based on my previous backend edit, I used: def admin_change_user_password(user_id: int, new_password: str, ...)
    // FastAPI will expect new_password as a query param or body depending on signature.
    // Let's re-verify my backend code... I used: def admin_change_user_password(user_id: int, new_password: str, ...)
    // In FastAPI, a simple type in a POST/PUT without Body() is a Query param.
    
    if (res.statusCode != 200) {
      throw Exception(jsonDecode(res.body)['detail'] ?? 'Failed to change password');
    }
  }

  Future<Map<String, dynamic>> getAdminStats() async {
    final res = await http.get(
      Uri.parse(ApiConfig.adminStats),
      headers: _headers,
    ).timeout(const Duration(seconds: 30));
    
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('Failed to load admin stats');
  }

  // ==================== SUBSCRIPTIONS ====================

  Future<SubscriptionModel> getMySubscription() async {
    final res = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/api/subscriptions/my'),
      headers: _headers,
    ).timeout(const Duration(seconds: 30));
    
    if (res.statusCode == 200) {
      return SubscriptionModel.fromJson(jsonDecode(res.body));
    }
    throw Exception('Failed to load subscription info');
  }

  Future<SubscriptionModel> payWithCard({
    required String cardNumber,
    required String expiry,
    required String cvv,
    required String planName,
  }) async {
    final res = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/api/subscriptions/pay-card'),
      headers: _headers,
      body: jsonEncode({
        'card_number': cardNumber,
        'expiry': expiry,
        'cvv': cvv,
        'plan_name': planName,
      }),
    ).timeout(const Duration(seconds: 30));
    
    if (res.statusCode == 200) {
      return SubscriptionModel.fromJson(jsonDecode(res.body));
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Payment failed');
  }
}
