import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../config/localization.dart';
import '../../services/api_service.dart';
import '../../services/theme_service.dart';
import 'admin_users_screen.dart';
import 'admin_orders_screen.dart';

class AdminPanelScreen extends StatelessWidget {
  final ApiService apiService;
  const AdminPanelScreen({super.key, required this.apiService});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<AppThemeMode>(
      valueListenable: ThemeService().themeNotifier,
      builder: (context, mode, child) {
        final palette = AppTheme.getPalette(mode);

        return Container(
          decoration: BoxDecoration(gradient: palette.bgGradient),
          child: DefaultTabController(
            length: 2,
            child: Scaffold(
              backgroundColor: Colors.transparent,
              appBar: AppBar(
                backgroundColor: Colors.transparent,
                elevation: 0,
                centerTitle: true,
                leading: IconButton(
                  icon: Icon(Icons.arrow_back_rounded, color: palette.textPrimary),
                  onPressed: () => Navigator.pop(context),
                ),
                title: Text(
                  AppStrings.isRu ? 'Админ-панель' : 'Admin paneli',
                  style: TextStyle(
                    fontWeight: FontWeight.w800, 
                    color: palette.textPrimary,
                    fontSize: 20
                  ),
                ),
                bottom: TabBar(
                  tabs: [
                    Tab(text: AppStrings.isRu ? 'Пользователи' : 'Foydalanuvchilar'),
                    Tab(text: AppStrings.isRu ? 'Заказы' : 'Buyurtmalar'),
                  ],
                  indicatorColor: palette.primary,
                  labelColor: palette.textPrimary,
                  unselectedLabelColor: palette.textSecondary.withOpacity(0.5),
                  labelStyle: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              body: TabBarView(
                children: [
                  AdminUsersScreen(apiService: apiService),
                  AdminOrdersScreen(apiService: apiService),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
