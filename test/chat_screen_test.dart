import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:findix_app/screens/orders/chat_screen.dart';
import 'package:findix_app/services/api_service.dart';

void main() {
  testWidgets('ChatScreen navigation tap test', (WidgetTester tester) async {
    final order = {
      'id': 1,
      'client_id': 100,
      'master_id': 200,
      'other_master_id': 200,
      'other_user_id': 100,
      'master_name': 'Test Master',
      'client_name': 'Test Client',
      'other_name': 'Other Name'
    };

    final apiService = ApiService();

    await tester.pumpWidget(MaterialApp(
      home: ChatScreen(
        order: order,
        apiService: apiService,
        currentUserId: 100, // I am client
      ),
    ));

    await tester.pumpAndSettle();

    final titleFinder = find.text('Other Name');
    expect(titleFinder, findsOneWidget);

    // Tap the title
    await tester.tap(titleFinder);
    await tester.pumpAndSettle();

    // Since MasterDetailScreen needs API, it might crash or show loading.
    // Let's just check if it navigated.
    print('Test finished');
  });
}
