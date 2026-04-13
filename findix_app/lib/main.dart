import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'dart:io' show Platform;
import 'package:shared_preferences/shared_preferences.dart';
import 'config/theme.dart';
import 'services/api_service.dart';
import 'services/auth_service.dart';
import 'screens/splash_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/register_screen.dart';
import 'screens/home_screen.dart';
import 'screens/orders/create_order_screen.dart';
import 'screens/orders/available_orders_screen.dart';
import 'screens/orders/my_orders_screen.dart';
import 'screens/orders/accepted_orders_screen.dart';
import 'screens/onboarding_screen.dart';
import 'screens/language_select_screen.dart';
import 'screens/app_reviews_screen.dart';
import 'services/socket_service.dart';
import 'services/notification_service.dart';
import 'services/theme_service.dart';
import 'dart:async';

import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:flutter_background_service_android/flutter_background_service_android.dart';
import 'package:intl/date_symbol_data_local.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize services
  final apiService = ApiService();
  final authService = AuthService(apiService);
  
  // Load saved token to ApiService on startup
  final prefs = await SharedPreferences.getInstance();
  final token = prefs.getString('auth_token');
  if (token != null) {
    apiService.setToken(token);
  }
  
  // Initialize notification service for UI alerts
  await NotificationService.instance.init();
  
  // Initialize Theme Service
  final themeService = ThemeService();
  await themeService.init();
  
  // Initialize Background Service
  await initializeService();

  // Initialize Date Formatting
  await initializeDateFormatting('ru', null);
  await initializeDateFormatting('uz', null);

  runApp(YaqinApp(apiService: apiService, authService: authService, themeService: themeService));
}

Future<void> initializeService() async {
  final service = FlutterBackgroundService();

  await service.configure(
    androidConfiguration: AndroidConfiguration(
      onStart: onStart,
      autoStart: true,
      isForegroundMode: true,
      notificationChannelId: 'yaqin_foreground',
      initialNotificationTitle: 'Yaqin',
      initialNotificationContent: 'Qidiruv yangi buyurtmalar...',
      foregroundServiceNotificationId: 888,
    ),
    iosConfiguration: IosConfiguration(
      autoStart: true,
      onForeground: onStart,
      onBackground: onIosBackground,
    ),
  );
}

@pragma('vm:entry-point')
Future<bool> onIosBackground(ServiceInstance service) async {
  return true;
}

@pragma('vm:entry-point')
void onStart(ServiceInstance service) async {
  if (service is AndroidServiceInstance) {
    service.on('setAsForeground').listen((event) {
      service.setAsForegroundService();
    });
    service.on('setAsBackground').listen((event) {
      service.setAsBackgroundService();
    });
    
    // IMMEDIATELY update UI so we know we are alive
    service.setForegroundNotificationInfo(
      title: "Yaqin",
      content: "Сервис запущен. Ждем данные...",
    );
  }

  service.on('stopService').listen((event) {
    service.stopSelf();
  });

  try {
    await NotificationService().init(requestPermission: false);
    
    final apiService = ApiService();
    final authService = AuthService(apiService);
    
    service.on('updateConfig').listen((event) async {
       final userId = event?['userId'];
       if (userId != null && userId is int) {
          SocketService().connect(userId);
       }
    });

    service.on('connect').listen((event) async {
       final userId = event?['user_id'];
       if (userId != null && userId is int) {
          SocketService().connect(userId);
       }
    });

    service.on('disconnect').listen((event) {
       SocketService().disconnect();
    });

    // Check saved user on start
    final userId = await authService.savedUserId;
    if (userId != null) {
       SocketService().connect(userId);
    } else {
       SocketService().disconnect();
    }

    Timer.periodic(const Duration(seconds: 30), (timer) async {
      if (service is AndroidServiceInstance) {
        if (await service.isForegroundService()) {
          service.setForegroundNotificationInfo(
            title: "Yaqin",
            content: "Поиск новых заказов...",
          );
        }
      }
    });
  } catch (e) {
    if (service is AndroidServiceInstance) {
      service.setForegroundNotificationInfo(
        title: "Yaqin: Ошибка запуска",
        content: e.toString(),
      );
    }
  }
}

class YaqinApp extends StatelessWidget {
  final ApiService apiService;
  final AuthService authService;
  final ThemeService themeService;

  static final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();
  
  const YaqinApp({super.key, required this.apiService, required this.authService, required this.themeService});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<AppThemeMode>(
      valueListenable: themeService.themeNotifier,
      builder: (context, mode, child) {
        return MaterialApp(
          navigatorKey: YaqinApp.navigatorKey,
          debugShowCheckedModeBanner: false,
          title: 'Yaqin',
          theme: AppTheme.getTheme(mode),
          themeMode: ThemeMode.light, // Force the specific selected mode
          initialRoute: '/',
          routes: {
            '/': (context) => SplashScreen(authService: authService),
            '/login': (context) => LoginScreen(authService: authService),
            '/register': (context) => RegisterScreen(authService: authService),
            '/home': (context) => HomeScreen(apiService: apiService, authService: authService),
            '/create-order': (context) => CreateOrderScreen(apiService: apiService, authService: authService),
            '/available-orders': (context) => AvailableOrdersScreen(apiService: apiService),
            '/my-orders': (context) => MyOrdersScreen(apiService: apiService, authService: authService),
            '/accepted-orders': (context) => AcceptedOrdersScreen(apiService: apiService, authService: authService),
            '/onboarding': (context) => const OnboardingScreen(),
            '/language-select': (context) => LanguageSelectScreen(authService: authService),
            '/app-reviews': (context) => AppReviewsScreen(apiService: apiService),
          },
        );
      },
    );
  }
}
