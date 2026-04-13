class ApiConfig {
  static const bool isProduction = false; // Toggle this for server deployment
  
  static const String devUrl = 'http://192.168.88.111:8010';
  static const String prodUrl = 'https://api.yaqin.uz';
  
  static String get baseUrl => isProduction ? prodUrl : devUrl;
  static String get wsBaseUrl => baseUrl.replaceFirst('http', 'ws');
  
  static String wsNotifications(int id) => '$wsBaseUrl/ws/notifications/$id';

  static const String apiUrl = '$baseUrl/api';

  static String get authRegister => '$apiUrl/auth/register';
  static String get authLogin => '$apiUrl/auth/login';
  static String get authMe => '$apiUrl/auth/me';
  static String get authProfile => '$apiUrl/auth/profile';
  static String get masters => '$apiUrl/masters';
  static String get masterProfile => '$apiUrl/masters/profile';
  static String get categories => '$apiUrl/categories';
  static String get favorites => '$apiUrl/favorites';
  static String get orders => '$apiUrl/orders';
  static String get ordersAvailable => '$apiUrl/orders/available';
  static String get ordersMy => '$apiUrl/orders/my';

  static String masterDetail(int id) => '$apiUrl/masters/$id';
  static String masterReview(int id) => '$apiUrl/masters/$id/review';
  static String toggleFavorite(int id) => '$apiUrl/favorites/$id';
  static String acceptOrder(int id) => '$apiUrl/orders/$id/accept';
  static String rateClient(int id) => '$apiUrl/orders/$id/rate_client';
  static String clientProfile(int id) => '$apiUrl/clients/$id';
  static String orderChat(int id) => '$apiUrl/orders/$id/chat';
  static String get orderChatList => '$apiUrl/orders/chats';
  
  // Admin
  static String get adminUsers => '$apiUrl/admin/users';
  static String adminUserDetail(int id) => '$apiUrl/admin/users/$id';
  static String get adminOrders => '$apiUrl/admin/orders';
  static String adminOrderDetail(int id) => '$apiUrl/admin/orders/$id';
  
  static String get appReviews => '$apiUrl/app-reviews/';
}


