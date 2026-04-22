import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import '../models/user.dart';
import 'api_service.dart';

class AuthService {
  static const _tokenKey = 'yaqin_token';
  static const _userIdKey = 'yaqin_user_id';
  static const _userNameKey = 'yaqin_user_name';
  static const _userRoleKey = 'yaqin_user_role';
  static const _langKey = 'yaqin_lang';

  final ApiService api;
  UserModel? currentUser;
  String? token;

  AuthService(this.api);

  int? get userId => currentUser?.id;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    token = prefs.getString(_tokenKey);
    if (token != null) {
      api.setToken(token);
      try {
        currentUser = await api.getMe();
      } catch (_) {
        await logout();
      }
    }
  }

  Future<bool> get isLoggedIn async => token != null;

  Future<int?> get savedUserId async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_userIdKey);
  }

  Future<String> get savedLang async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_langKey) ?? 'ru';
  }

  Future<void> _saveToken(String t, UserModel user) async {
    token = t;
    currentUser = user;
    api.setToken(t);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, t);
    await prefs.setInt(_userIdKey, user.id);
    await prefs.setString(_userNameKey, user.name);
    await prefs.setString(_userRoleKey, user.role);
    
    // Notify Background Service immediately
    try {
      FlutterBackgroundService().invoke('updateConfig', {'userId': user.id});
    } catch (e) {
      debugPrint('AuthService: Failed to notify background service: $e');
    }
  }

  Future<void> saveLang(String lang) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_langKey, lang);
  }

  Future<UserModel> uploadAvatar(String imagePath) async {
    final user = await api.uploadAvatar(imagePath);
    currentUser = user;
    return user;
  }

  Future<UserModel> login(String phone, String password) async {
    final data = await api.login(phone: phone, password: password);
    final user = UserModel.fromJson(data['user']);
    await _saveToken(data['access_token'], user);
    return user;
  }

  Future<UserModel> register({
    String? name,
    required String phone,
    required String password,
    String role = 'client',
    String? city,
    String lang = 'ru',
  }) async {
    final data = await api.register(
      name: name,
      phone: phone,
      password: password,
      role: role,
      city: city,
      lang: lang,
    );
    final user = UserModel.fromJson(data['user']);
    await _saveToken(data['access_token'], user);
    return user;
  }

  Future<UserModel?> refreshUser() async {
    if (token == null) return null;
    try {
      final user = await api.getMe();
      currentUser = user;
      
      // Update role in storage too
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userRoleKey, user.role);
      
      return user;
    } catch (e) {
      debugPrint('Error refreshing user: $e');
      return currentUser;
    }
  }

  Future<void> updateFCMToken(String fcmToken) async {
    if (token == null) return;
    try {
      await api.updateFCMToken(fcmToken);
      debugPrint('AuthService: FCM Token updated successfully');
    } catch (e) {
      debugPrint('AuthService: Failed to update FCM token on backend: $e');
    }
  }

  Future<void> logout() async {
    token = null;
    currentUser = null;
    api.setToken(null);
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userIdKey);
    await prefs.remove(_userNameKey);
    await prefs.remove(_userRoleKey);
  }
}
