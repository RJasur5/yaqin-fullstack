import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_core/firebase_core.dart';
import 'auth_service.dart';
import 'package:flutter/foundation.dart';
import 'dart:io' show Platform;
import '../main.dart';
import 'dart:convert';

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  // Handle background message
}


class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();

  static final NotificationService instance = NotificationService._internal();
  
  dynamic _pendingPayload;
  bool _isNavigationInProgress = false;

  // Track the current chat to suppress notifications while reading
  static int? activeChatOrderId;

  Future<void> init({bool requestPermission = true, AuthService? authService}) async {
    if (kIsWeb) return; 

    // Initialize Firebase if not already initialized
    await Firebase.initializeApp();

    // Set background handler
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

    // Listen for token refresh and update backend
    FirebaseMessaging.instance.onTokenRefresh.listen((newToken) {
      if (authService != null) {
        authService.updateFCMToken(newToken);
      }
    });

    // Request permissions for iOS
    if (Platform.isIOS) {
       await FirebaseMessaging.instance.requestPermission(
          alert: true,
          badge: true,
          sound: true,
       );
    }

    // Retrieve and register FCM Token
    String? token = await FirebaseMessaging.instance.getToken();
    if (token != null && authService != null) {
       print("FCM Token: $token");
       await authService.updateFCMToken(token);
    }

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      // System notification suppressed in foreground as requested.
      // Internal overlays are handled by SocketService.
      debugPrint('NOTIFICATION_SERVICE: Foreground message received (system UI suppressed)');
    });


    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const DarwinInitializationSettings initializationSettingsDarwin =
        DarwinInitializationSettings();

    const InitializationSettings initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsDarwin,
    );

    await flutterLocalNotificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: (NotificationResponse response) {
        handlePayload(response.payload);
      },
    );

    // 1. CAPTURE TERMINATED STATE MESSAGE IMMEDIATELY
    RemoteMessage? initialMessage = await FirebaseMessaging.instance.getInitialMessage();
    if (initialMessage != null && initialMessage.data.isNotEmpty) {
      debugPrint('NOTIFICATION_SERVICE: Captured initial message on init');
      _pendingPayload = initialMessage.data;
    } else {
      // 2. CHECK LOCAL NOTIFICATIONS AS FALLBACK
      final NotificationAppLaunchDetails? details = 
          await flutterLocalNotificationsPlugin.getNotificationAppLaunchDetails();
      if (details != null && details.didNotificationLaunchApp) {
        debugPrint('NOTIFICATION_SERVICE: Captured local notification launch');
        _pendingPayload = details.notificationResponse?.payload;
      }
    }

    // Handle clicks when app is in background
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
       handlePayload(message.data);
    });

    if (Platform.isAndroid) {
      final androidPlugin = flutterLocalNotificationsPlugin
          .resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();
      
      // Create the channel for the foreground service
      const AndroidNotificationChannel channel = AndroidNotificationChannel(
        'yaqin_foreground', // same as in main.dart
        'Yaqin Background Service',
        description: 'This channel is used for the foreground service.',
        importance: Importance.low, 
      );

      // Create the channel for actual ORDER notifications (CRITICAL FIX)
      const AndroidNotificationChannel ordersChannel = AndroidNotificationChannel(
        'yaqin_orders_channel',
        'Yaqin Order Notifications',
        description: 'Notifications for new orders matching your specialty',
        importance: Importance.max,
        playSound: true,
        enableVibration: true,
      );

      await androidPlugin?.createNotificationChannel(channel);
      await androidPlugin?.createNotificationChannel(ordersChannel);
      
      // ONLY request permission if we are in the main UI thread
      if (requestPermission) {
        await androidPlugin?.requestNotificationsPermission();
      }
    }
  }

  Future<void> handlePayload(dynamic data) async {
    if (data == null) return;
    
    // Convert string to map if needed
    Map<String, dynamic> finalData = {};
    if (data is String) {
      if (data.isEmpty) return;
      try {
        final parsed = json.decode(data);
        if (parsed is Map) {
          finalData = Map<String, dynamic>.from(parsed);
        } else {
          finalData['type'] = data;
        }
      } catch (_) {
        finalData['type'] = data;
      }
    } else if (data is Map) {
      finalData = Map<String, dynamic>.from(data);
    }

    final type = finalData['type']?.toString();
    if (type == null) return;

    var nav = YaqinApp.navigatorKey.currentState;
    
    // If navigator is not ready, store as pending and we will process it later
    if (nav == null) {
      debugPrint('NOTIFICATION_SERVICE: Navigator not ready, storing as pending: $type');
      _pendingPayload = finalData;
      return;
    }

    if (_isNavigationInProgress) {
      debugPrint('NOTIFICATION_SERVICE: Navigation already in progress, queuing payload');
      _pendingPayload = finalData;
      return;
    }
    
    _isNavigationInProgress = true;

    try {
      debugPrint('NOTIFICATION_SERVICE: Executing navigation for type: $type');
      
      // Delay slightly to ensure any current transitions are finished
      await Future.delayed(const Duration(milliseconds: 300));
      
      // Support both old string format and new backend format
      if (type == 'new_order' || type == 'available_orders' || finalData['payload'] == 'available_orders') {
        await nav.pushNamed('/available-orders');
      } else if (type == 'chat_message' || type.startsWith('chat_')) {
        // If we have order data, we could potentially go to the specific chat, 
        // but for now, we go to the chat list to be safe.
        await nav.pushNamed('/chats');
      } else if (type == 'my_orders' || type == 'order_accepted' || type == 'order_completed') {
        await nav.pushNamed('/my-orders');
      } else {
        debugPrint('NOTIFICATION_SERVICE: No specific navigation for type: $type');
      }
    } finally {
      // Small cooldown to prevent double transitions
      await Future.delayed(const Duration(milliseconds: 500));
      _isNavigationInProgress = false;
      _pendingPayload = null; // Clear queue after success
    }
  }

  /// Called when the Navigator is definitely ready (e.g. from HomeScreen or the main builder)
  Future<void> processPendingNavigation({int retryCount = 0}) async {
    if (_pendingPayload != null) {
      debugPrint('NOTIFICATION_SERVICE: Processing pending navigation (Attempt ${retryCount + 1})...');
      
      if (YaqinApp.navigatorKey.currentState == null) {
        if (retryCount < 5) {
          debugPrint('NOTIFICATION_SERVICE: Navigator still not ready, retrying in 500ms...');
          await Future.delayed(const Duration(milliseconds: 500));
          return processPendingNavigation(retryCount: retryCount + 1);
        } else {
          debugPrint('NOTIFICATION_SERVICE: Navigator failed to initialize after 5 retries.');
          return;
        }
      }
      
      await handlePayload(_pendingPayload);
    }
  }

  Future<void> showNotification({
    required int id,
    required String title,
    required String body,
    Map<String, dynamic>? data,
  }) async {
    if (kIsWeb) return; // Skip on Web

    final String? payload = data != null ? json.encode(data) : null;
    final AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'yaqin_orders_channel',
      'Yaqin Order Notifications',
      channelDescription: 'Notifications for new orders matching your specialty',
      importance: Importance.max,
      priority: Priority.high,
      showWhen: true,
      playSound: true,
      enableVibration: true,
      visibility: NotificationVisibility.public,
    );

    const DarwinNotificationDetails darwinPlatformChannelSpecifics =
        DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    final NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
      iOS: darwinPlatformChannelSpecifics,
    );

    await flutterLocalNotificationsPlugin.show(
      id,
      title,
      body,
      platformChannelSpecifics,
      payload: payload,
    );
  }
}
