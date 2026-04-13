import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io' show Platform;
import '../main.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();

  static final NotificationService instance = NotificationService._internal();

  Future<void> init({bool requestPermission = true}) async {
    if (kIsWeb) return; // Skip initialization on Web

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
        final payload = response.payload;
        if (payload != null && payload.isNotEmpty) {
           final nav = YaqinApp.navigatorKey.currentState;
           if (nav != null) {
              if (payload.startsWith('chat_')) {
                 final orderId = int.tryParse(payload.split('_')[1]);
                 if (orderId != null) {
                    nav.pushNamed('/chat', arguments: orderId);
                 }
              } else if (payload == 'available_orders') {
                 nav.pushNamed('/available-orders');
              } else if (payload == 'my_orders') {
                 nav.pushNamed('/my-orders');
              }
           }
        }
      },
    );

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

  Future<void> showNotification({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    if (kIsWeb) return; // Skip on Web

    const AndroidNotificationDetails androidPlatformChannelSpecifics =
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

    const NotificationDetails platformChannelSpecifics = NotificationDetails(
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
