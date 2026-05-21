import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'auth_service.dart';
import 'package:flutter/foundation.dart';
import 'dart:io' show Platform;
import '../main.dart';
import 'dart:convert';
import '../screens/home_screen.dart';

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  // Handle background message
}


class NotificationService {
  // FIX: Single instance only
  static final NotificationService instance = NotificationService._internal();
  factory NotificationService() => instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();
  
  dynamic _pendingPayload;
  bool _isNavigationInProgress = false;
  static bool isReadyForNavigation = false;
  static bool _initialMessageProcessed = false;

  // Track the current chat to suppress notifications while reading
  static int? activeChatOrderId;

  /// Called from main() to set notification payload read from native iOS UserDefaults
  void setNativePendingPayload(String jsonPayload) {
    try {
      final parsed = json.decode(jsonPayload);
      if (parsed is Map && parsed.isNotEmpty) {
        _pendingPayload = Map<String, dynamic>.from(parsed);
        debugPrint('NOTIFICATION_SERVICE: Native payload set from main(): $_pendingPayload');
      }
    } catch (e) {
      debugPrint('NOTIFICATION_SERVICE: Error parsing native payload in setNativePendingPayload: $e');
    }
  }

  Future<void> init({bool requestPermission = true, AuthService? authService, bool isBackgroundService = false}) async {
    if (kIsWeb) return; 

    // Initialize Firebase if not already initialized
    try {
      await Firebase.initializeApp();
    } catch (e) {
      debugPrint('Firebase already initialized or error: $e');
    }

    // Set background handler
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

    // Listen for token refresh and update backend
    if (!isBackgroundService) {
      FirebaseMessaging.instance.onTokenRefresh.listen((newToken) {
        if (authService != null) {
          authService.updateFCMToken(newToken);
        }
      });
    }

    // Request permissions for iOS
    if (Platform.isIOS && !isBackgroundService) {
       await FirebaseMessaging.instance.requestPermission(
          alert: true,
          badge: true,
          sound: true,
       );
       await FirebaseMessaging.instance.setForegroundNotificationPresentationOptions(
          alert: true,
          badge: true,
          sound: true,
       );
    }

    // Fetch FCM Token asynchronously to not block app launch
    if (!isBackgroundService) {
      () async {
        try {
          if (Platform.isIOS) {
            String? apnsToken;
            // Wait up to 30 seconds for APNS token asynchronously without blocking app launch
            for (int i = 0; i < 30; i++) {
              await Future.delayed(const Duration(seconds: 1));
              apnsToken = await FirebaseMessaging.instance.getAPNSToken();
              if (apnsToken != null) break;
            }
            if (apnsToken == null) {
              print("APNS token is still null after 30s. Push notifications won't work.");
              return;
            }
            print("APNS Token acquired: $apnsToken");
          }
          String? token = await FirebaseMessaging.instance.getToken();
          if (token != null && authService != null) {
             print("FCM Token: $token");
             await authService.updateFCMToken(token);
          }
        } catch (e) {
          print("Error getting FCM token: $e");
        }
      }();
    }

    // Handle foreground messages
    if (!isBackgroundService) {
      FirebaseMessaging.onMessage.listen((RemoteMessage message) {
        debugPrint('NOTIFICATION_SERVICE: Foreground message received: ${message.data}');
        
        final data = message.data;
        // If it's a chat message and we're currently in that chat, suppress it
        if (data['type'] == 'chat_message' || data['type'] == 'chat_new_order') {
          final orderIdStr = data['order_id']?.toString();
          if (orderIdStr != null && int.tryParse(orderIdStr) == activeChatOrderId) {
             debugPrint('NOTIFICATION_SERVICE: Suppressing foreground notification for active chat $activeChatOrderId');
             return;
          }
        }

        // Prevent duplicate notifications in the foreground:
        // SocketService already shows a global overlay for 'new_order' and a dialog for 'hr_expiry_warning'.
        if (data['type'] == 'new_order' || data['type'] == 'hr_expiry_warning') {
           debugPrint('NOTIFICATION_SERVICE: Suppressing system foreground notification for ${data['type']} because SocketService handles it via UI');
           return;
        }

        // Show system notification
        instance.showNotification(
          id: DateTime.now().millisecondsSinceEpoch.remainder(100000),
          title: message.notification?.title ?? data['title'] ?? 'Новое уведомление',
          body: message.notification?.body ?? data['body'] ?? '',
          data: data,
        );
      });
    }

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

    // 1. CAPTURE TERMINATED STATE MESSAGE - try Firebase first
    RemoteMessage? initialMessage = await FirebaseMessaging.instance.getInitialMessage();
    if (initialMessage != null && initialMessage.data.isNotEmpty) {
      debugPrint('NOTIFICATION_SERVICE: Captured initial message via Firebase');
      _pendingPayload = initialMessage.data;
    } else {
      // 2. CHECK NATIVE iOS UserDefaults (our AppDelegate stores notification taps here)
      await _checkNativeNotificationPayload();
    }
    
    if (_pendingPayload == null) {
      // 3. CHECK LOCAL NOTIFICATIONS AS FALLBACK
      final NotificationAppLaunchDetails? details = 
          await flutterLocalNotificationsPlugin.getNotificationAppLaunchDetails();
      if (details != null && details.didNotificationLaunchApp) {
        debugPrint('NOTIFICATION_SERVICE: Captured local notification launch');
        _pendingPayload = details.notificationResponse?.payload;
      }
    }

    // Handle clicks when app is in background
    if (!isBackgroundService) {
      FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
         handlePayload(message.data);
      });
    }

    if (Platform.isAndroid) {
      final androidPlugin = flutterLocalNotificationsPlugin
          .resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();
      
      // Create the channel for the foreground service
      const AndroidNotificationChannel channel = AndroidNotificationChannel(
        'yaqin_foreground', // same as in main.dart
        'Yaqin Go Background Service',
        description: 'This channel is used for the foreground service.',
        importance: Importance.low, 
      );

      // Create a hidden channel to silently absorb unlocalized Russian FCM pushes
      const AndroidNotificationChannel hiddenChannel = AndroidNotificationChannel(
        'yaqin_fcm_hidden',
        'Hidden FCM Notifications',
        description: 'Silently consumes backend FCM to avoid duplicates',
        importance: Importance.none, // NOTHING IS SHOWN
        playSound: false,
        enableVibration: false,
      );

      // Create the channel for actual ORDER notifications (CRITICAL FIX)
      const AndroidNotificationChannel ordersChannel = AndroidNotificationChannel(
        'yaqin_orders_channel',
        'Yaqin Go Order Notifications',
        description: 'Notifications for new orders matching your specialty',
        importance: Importance.max,
        playSound: true,
        enableVibration: true,
      );

      await androidPlugin?.createNotificationChannel(channel);
      await androidPlugin?.createNotificationChannel(hiddenChannel);
      await androidPlugin?.createNotificationChannel(ordersChannel);
      
      // ONLY request permission if we are in the main UI thread
      if (requestPermission) {
        await androidPlugin?.requestNotificationsPermission();
      }
    }
  }

  /// Read notification payload saved by native iOS AppDelegate
  Future<void> _checkNativeNotificationPayload() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final nativePayload = prefs.getString('pending_notification_payload');
      if (nativePayload != null && nativePayload.isNotEmpty) {
        debugPrint('NOTIFICATION_SERVICE: Found native iOS notification payload: $nativePayload');
        // Clear it immediately so it's not processed again
        await prefs.remove('pending_notification_payload');
        
        try {
          final parsed = json.decode(nativePayload);
          if (parsed is Map) {
            _pendingPayload = Map<String, dynamic>.from(parsed);
            debugPrint('NOTIFICATION_SERVICE: Parsed native payload: $_pendingPayload');
          }
        } catch (e) {
          debugPrint('NOTIFICATION_SERVICE: Error parsing native payload: $e');
        }
      }
    } catch (e) {
      debugPrint('NOTIFICATION_SERVICE: Error reading native notification payload: $e');
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

    if (finalData.containsKey('payload') && finalData['payload'] is String) {
      try {
        final decoded = json.decode(finalData['payload']);
        if (decoded is Map) {
          finalData.addAll(Map<String, dynamic>.from(decoded));
        }
      } catch (e) {
        debugPrint('NOTIFICATION_SERVICE: Could not decode payload: $e');
      }
    }

    final type = finalData['type']?.toString();
    if (type == null) return;

    var nav = YaqinApp.navigatorKey.currentState;
    
    // If navigator is not ready or we are still on Splash Screen, store as pending
    if (nav == null || !isReadyForNavigation) {
      debugPrint('NOTIFICATION_SERVICE: App not ready for navigation, storing as pending: $type');
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
      
      // Helper: Navigate to HomeScreen on a specific tab (preserves BottomNavigationBar)
      void goToHomeTab(int tabIndex) {
        bool hasHome = false;
        nav.popUntil((route) {
          if (route.settings.name == '/home') hasHome = true;
          return true;
        });

        if (hasHome) {
          nav.popUntil((route) => route.settings.name == '/home');
          HomeScreen.switchToTab?.call(tabIndex);
        } else {
          nav.pushNamedAndRemoveUntil('/home', (route) => false);
          Future.delayed(const Duration(milliseconds: 200), () {
            HomeScreen.switchToTab?.call(tabIndex);
          });
        }
      }
      
      // Support both old string format and new backend format
      if (type == 'new_order' || type == 'available_orders' || finalData['payload'] == 'available_orders') {
        // Tab 3 = Available Orders
        goToHomeTab(3);
      } else if (type == 'chat_message' || type.startsWith('chat_')) {
        // Tab 2 = Chats
        goToHomeTab(2);
      } else if (type == 'job_applications' || type == 'job_application') {
        await nav.pushNamed('/job-applications');
      } else if (type == 'job_application_status' || type == 'my_orders') {
        // Go to My Orders Screen
        await nav.pushNamed('/my-orders');
      } else if (type == 'order_accepted') {
        // If it's an HR announcement response, go to My Orders. Else go to Profile.
        if (finalData['is_company'] == 'True' || finalData['is_company'] == true) {
          await nav.pushNamed('/my-orders');
        } else {
          goToHomeTab(4); // Profile Tab
        }
      } else if (type == 'order_completed' || type == 'hr_accepted' || type == 'order_rejected' || type == 'profile' || type == 'vacancy_closed') {
        goToHomeTab(4); // Profile Tab
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
    // If pending payload is null, try ALL sources one more time
    if (_pendingPayload == null && !_initialMessageProcessed) {
      _initialMessageProcessed = true;

      // 1. Try Firebase getInitialMessage
      try {
        final initialMessage = await FirebaseMessaging.instance.getInitialMessage();
        if (initialMessage != null && initialMessage.data.isNotEmpty) {
          debugPrint('NOTIFICATION_SERVICE: Late capture via Firebase getInitialMessage');
          _pendingPayload = initialMessage.data;
        }
      } catch (e) {
        debugPrint('NOTIFICATION_SERVICE: Error in late getInitialMessage: $e');
      }
      
      // 2. Try native iOS UserDefaults (AppDelegate saved it there)
      if (_pendingPayload == null) {
        await _checkNativeNotificationPayload();
      }
      
      // 3. Try flutter_local_notifications launch details
      if (_pendingPayload == null) {
        try {
          final details = await flutterLocalNotificationsPlugin.getNotificationAppLaunchDetails();
          if (details != null && details.didNotificationLaunchApp && details.notificationResponse?.payload != null) {
            debugPrint('NOTIFICATION_SERVICE: Late capture via local notification launch details');
            _pendingPayload = details.notificationResponse!.payload;
          }
        } catch (e) {
          debugPrint('NOTIFICATION_SERVICE: Error in late launch details: $e');
        }
      }
    }

    if (_pendingPayload != null) {
      debugPrint('NOTIFICATION_SERVICE: Processing pending navigation (Attempt ${retryCount + 1}), payload: $_pendingPayload');
      
      if (YaqinApp.navigatorKey.currentState == null || !isReadyForNavigation) {
        if (retryCount < 10) {
          debugPrint('NOTIFICATION_SERVICE: App still not ready, retrying in 500ms...');
          await Future.delayed(const Duration(milliseconds: 500));
          return processPendingNavigation(retryCount: retryCount + 1);
        } else {
          debugPrint('NOTIFICATION_SERVICE: App failed to be ready after 10 retries.');
          return;
        }
      }
      
      await handlePayload(_pendingPayload);
    } else {
      debugPrint('NOTIFICATION_SERVICE: No pending payload found from any source.');
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
      'Yaqin Go Order Notifications',
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
