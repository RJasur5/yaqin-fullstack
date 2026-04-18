import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/theme.dart';
import '../config/localization.dart';
import '../config/api_config.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';
import '../services/theme_service.dart';
import '../widgets/gradient_button.dart';
import 'master_profile_setup_screen.dart';
import '../models/master.dart';
import '../models/subscription.dart';
import 'subscription_screen.dart';

import 'admin/admin_panel_screen.dart';

class ProfileScreen extends StatefulWidget {
  final AuthService authService;
  final ApiService apiService;
  const ProfileScreen({super.key, required this.authService, required this.apiService});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  MasterModel? _masterProfile;
  SubscriptionModel? _subscription;
  bool _isLoadingMaster = false;
  String? _photoPath;

  @override
  void initState() {
    super.initState();
    _loadMasterProfile();
    _loadSubscription();
    _loadPhoto();
  }

  Future<void> _loadSubscription() async {
    try {
      final sub = await widget.apiService.getMySubscription();
      if (mounted) setState(() => _subscription = sub);
    } catch (_) {}
  }

  Future<void> _loadPhoto() async {
    // Legacy local photo loading removed in favor of remote API fetching.
  }

  Future<void> _pickPhoto() async {
    // Show warning dialog first
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) {
        final theme = Theme.of(ctx);
        return AlertDialog(
          backgroundColor: theme.cardTheme.color,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: AppColors.warning, size: 28),
              const SizedBox(width: 10),
              Text(
                AppStrings.isRu ? 'Важно!' : 'Muhim!',
                style: theme.textTheme.titleMedium?.copyWith(color: AppColors.warning),
              ),
            ],
          ),
          content: Text(
            AppStrings.isRu
              ? 'Фото должно быть вашим настоящим лицом.\nЕсли фото не соответствует требованиям, профиль может быть удалён через 3 дня.'
              : 'Foto haqiqiy yuzingiz bo\'lishi kerak.\nAks holda, profil 3 kun ichida o\'chirilishi mumkin.',
            style: theme.textTheme.bodyMedium?.copyWith(height: 1.5),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: Text(
                AppStrings.isRu ? 'Отмена' : 'Bekor',
                style: TextStyle(color: theme.textTheme.bodySmall?.color),
              ),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: theme.primaryColor,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: () => Navigator.pop(ctx, true),
              child: Text(AppStrings.isRu ? 'Понятно, выбрать' : 'Tushunarli, tanlash'),
            ),
          ],
        );
      },
    );

    if (confirmed != true) return;

    final picker = ImagePicker();
    final picked = await picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 512,
      maxHeight: 512,
      imageQuality: 85,
    );
    if (picked != null) {
      setState(() => _isLoadingMaster = true); // reuse loading
      try {
        await widget.authService.uploadAvatar(picked.path);
        if (mounted) setState(() {}); // Trigger rebuild to show new avatar
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
        }
      } finally {
        if (mounted) setState(() => _isLoadingMaster = false);
      }
    }
  }

  Future<void> _loadMasterProfile() async {
    // First, force refresh user data from server to catch role changes
    final user = await widget.authService.refreshUser();
    if (user != null && user.isMaster) {
      setState(() => _isLoadingMaster = true);
      try {
        final profile = await widget.apiService.getMyMasterProfile();
        if (mounted) setState(() => _masterProfile = profile);
      } catch (_) {} finally {
        if (mounted) setState(() => _isLoadingMaster = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final user = widget.authService.currentUser;
    if (user == null) {
      return const Center(child: Text('Not logged in', style: TextStyle(color: AppColors.textPrimary)));
    }

    return Container(
      decoration: BoxDecoration(gradient: AppTheme.currentGradient(context)),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
            children: [
              const SizedBox(height: 20),
              // Avatar with photo upload
              GestureDetector(
                onTap: _pickPhoto,
                child: Stack(
                  children: [
                    Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        gradient: user.avatar == null ? AppColors.primaryGradient : null,
                        borderRadius: BorderRadius.circular(30),
                        boxShadow: [
                          BoxShadow(
                            color: theme.primaryColor.withOpacity(0.4),
                            blurRadius: 20,
                            offset: const Offset(0, 8),
                          ),
                        ],
                      ),
                      child: user.avatar != null
                        ? ClipRRect(
                            borderRadius: BorderRadius.circular(30),
                            child: Image.network(
                              user.avatar!.startsWith('http') 
                                ? user.avatar! 
                                : '${ApiConfig.baseUrl.replaceAll("/api", "")}${user.avatar}',
                              fit: BoxFit.cover,
                            ),
                          )
                        : Center(
                            child: Text(
                              user.name.isNotEmpty
                                  ? user.name.split(' ').map((w) => w.isNotEmpty ? w[0] : '').take(2).join().toUpperCase()
                                  : '?',
                              style: const TextStyle(fontSize: 36, fontWeight: FontWeight.w900, color: Colors.white),
                            ),
                          ),
                    ),
                    // Camera overlay
                    Positioned(
                      bottom: 0,
                      right: 0,
                      child: Container(
                        width: 32,
                        height: 32,
                        decoration: BoxDecoration(
                          color: theme.primaryColor,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: theme.scaffoldBackgroundColor, width: 2),
                        ),
                        child: const Icon(Icons.camera_alt_rounded, color: Colors.white, size: 16),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Text(
                user.name,
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: Theme.of(context).textTheme.bodyLarge?.color),
              ),
              if (_subscription != null && _subscription!.isActive) ...[
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(colors: [Color(0xFFFFD700), Color(0xFFFFA500)]),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.stars_rounded, color: Colors.white, size: 14),
                      const SizedBox(width: 6),
                      Text(
                        _subscription!.planTitle.toUpperCase(),
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 10, letterSpacing: 0.5),
                      ),
                    ],
                  ),
                ),
              ],
              const SizedBox(height: 32),

              // Info cards
              _infoTile(Icons.phone_rounded, AppStrings.phone, user.phone),
              _infoTile(Icons.location_city_rounded, AppStrings.city, user.city ?? '-'),
              _infoTile(Icons.language_rounded, AppStrings.language, user.lang == 'ru' ? AppStrings.russian : AppStrings.uzbek),

              // Master Info
              if (_isLoadingMaster)
                CircularProgressIndicator(color: theme.primaryColor)
              else if (_masterProfile != null) ...[
                const SizedBox(height: 24),
                // Section header — no Divider line
                Row(
                  children: [
                    Container(
                      width: 4,
                      height: 20,
                      decoration: BoxDecoration(
                        gradient: AppColors.primaryGradient,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Text(
                      AppStrings.isRu ? 'Профиль мастера' : 'Mutaxassis profili',
                      style: theme.textTheme.titleMedium,
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => MasterProfileSetupScreen(
                          apiService: widget.apiService,
                          authService: widget.authService,
                        ),
                      ),
                    ).then((_) => _loadMasterProfile());
                  },
                  child: Column(
                    children: [
                      _infoTile(Icons.medical_services_rounded, AppStrings.isRu ? 'Специализация' : 'Mutaxassislik', '${_masterProfile!.categoryName(AppStrings.lang)} -> ${_masterProfile!.subcategoryName(AppStrings.lang)}'),
                      _infoTile(Icons.work_history_rounded, AppStrings.experience, '${_masterProfile!.experienceYears} ${AppStrings.years}'),
                      if (_masterProfile!.hourlyRate != null)
                        _infoTile(Icons.payments_rounded, AppStrings.hourlyRate, '${_masterProfile!.hourlyRate!.toStringAsFixed(0)} ${AppStrings.sum}${AppStrings.perHour}'),
                      if (_masterProfile!.city == 'Toshkent' && _masterProfile!.district != null)
                        _infoTile(Icons.location_on_rounded, AppStrings.isRu ? 'Район' : 'Tuman', _masterProfile!.district!),
                      
                      // For non-Tashkent cities, show address. For Tashkent, hide address if district is present.
                      if (_masterProfile!.city != 'Toshkent' && _masterProfile!.address != null && _masterProfile!.address!.isNotEmpty)
                        _infoTile(Icons.map_rounded, AppStrings.isRu ? 'Адрес' : 'Manzil', _masterProfile!.address!),
                      
                      if (_masterProfile!.skills.isNotEmpty)
                        _infoTile(Icons.check_circle_outline_rounded, AppStrings.skills, _masterProfile!.skills.join(', ')),
                    ],
                  ),
                ),
              ],
              const SizedBox(height: 20),

              const SizedBox(height: 8),

              // SUBSCRIPTION BUTTON [GOLD STYLE]
              Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.primary.withOpacity(0.2),
                      blurRadius: 15,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: GradientButton(
                  text: AppStrings.isRu ? 'Управление подпиской' : 'Obunani boshqarish',
                  icon: Icons.workspace_premium_rounded,
                  colors: const [Color(0xFF6A11CB), Color(0xFF2575FC)], // Sharp blue/purple premium look
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => SubscriptionScreen(apiService: widget.apiService),
                      ),
                    ).then((_) => _loadSubscription());
                  },
                ),
              ),
              const SizedBox(height: 16),
              
              // Admin Panel (Visible only to admins)
              if (user.isAdmin) ...[
                GradientButton(
                  text: AppStrings.isRu ? 'Админ-панель' : 'Admin paneli',
                  icon: Icons.admin_panel_settings_rounded,
                  onPressed: () {
                    Navigator.push(context, MaterialPageRoute(builder: (_) => AdminPanelScreen(apiService: widget.apiService)));
                  },
                ),
                const SizedBox(height: 16),
              ],

              // Post Ad Button (for everyone)
              GradientButton(
                text: AppStrings.isRu ? 'Подать объявление' : 'E\'lon berish',
                icon: Icons.add_circle_outline_rounded,
                onPressed: () {
                  Navigator.pushNamed(context, '/create-order').then((_) => _loadMasterProfile());
                },
              ),
              const SizedBox(height: 16),

              // My Orders Button
              GradientButton(
                text: AppStrings.isRu ? 'Мои заказы' : 'Mening buyurtmalarim',
                icon: Icons.assignment_rounded,
                onPressed: () {
                  Navigator.pushNamed(context, '/my-orders');
                },
              ),
              const SizedBox(height: 16),

              // Master Specific Actions
              if (user.isMaster) ...[
                GradientButton(
                  text: AppStrings.isRu ? 'Принятые заказы' : 'Qabul qilingan buyurtmalar',
                  icon: Icons.history_rounded,
                  onPressed: () {
                    Navigator.pushNamed(context, '/accepted-orders');
                  },
                ),
                const SizedBox(height: 16),
                GradientButton(
                  text: AppStrings.isRu ? 'Настроить профиль мастера' : 'Master profilini sozlash',
                  icon: Icons.edit_note_rounded,
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => MasterProfileSetupScreen(
                          apiService: widget.apiService,
                          authService: widget.authService,
                        ),
                      ),
                    ).then((_) {
                      _loadMasterProfile();
                    });
                  },
                ),
              ] else ...[
                 // Not a master yet
                 GradientButton(
                  text: AppStrings.isRu ? 'Стать мастером' : 'Usta bo\'lish',
                  icon: Icons.engineering_rounded,
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => MasterProfileSetupScreen(
                          apiService: widget.apiService,
                          authService: widget.authService,
                        ),
                      ),
                    ).then((_) {
                      _loadMasterProfile();
                    });
                  },
                ),
              ],
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    ),
    );
  }

  Widget _infoTile(IconData icon, String label, String value) {
    final theme = Theme.of(context);
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.cardTheme.color,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: theme.dividerColor.withOpacity(0.5)),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: theme.primaryColor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: theme.primaryColor, size: 20),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: TextStyle(fontSize: 12, color: theme.textTheme.bodySmall?.color)),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: theme.textTheme.bodyLarge?.color,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
