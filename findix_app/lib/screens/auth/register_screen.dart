import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../config/localization.dart';
import '../../services/auth_service.dart';
import '../../services/theme_service.dart';
import '../../widgets/gradient_button.dart';
import '../../utils/phone_utils.dart';

class RegisterScreen extends StatefulWidget {
  final AuthService authService;
  const RegisterScreen({super.key, required this.authService});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController(text: '+998 ');
  final _passwordController = TextEditingController();
  final _phoneFormatter = PhoneUtils.maskFormatter;
  bool _isLoading = false;
  bool _obscurePassword = true;
  bool _acceptedPolicy = false;
  String _role = 'client';
  String? _selectedCity;
  String? _error;

  final List<String> _uzbekistanCities = [
    'Toshkent', 'Samarqand', 'Buxoro', 'Andijon', 'Namangan', 'Farg\'ona', 
    'Nukus', 'Navoiy', 'Urganch', 'Qarshi', 'Jizzax', 'Termiz', 'Xiva', 'Guliston'
  ];

  Future<void> _register() async {
    if (!_acceptedPolicy) {
      setState(() => _error = AppStrings.isRu ? 'Необходимо согласиться с политикой конфиденциальности' : 'Maxfiylik siyosatiga rozi bo\'lishingiz kerak');
      return;
    }
    if (_phoneController.text.isEmpty ||
        _passwordController.text.isEmpty) {
      setState(() => _error = 'Введите номер телефона и пароль');
      return;
    }
    // Phone digit count check: must have exactly 9 digits after 998
    final digits = _phoneController.text.replaceAll(RegExp(r'[^0-9]'), '');
    // digits starts with '998' (3 digits) + 9 subscriber digits = 12 total
    if (digits.length < 12) {
      setState(() => _error = AppStrings.isRu
          ? 'Номер телефона должен содержать ровно 9 цифр (после +998)'
          : 'Telefon raqami +998 dan keyin aynan 9 ta raqam bo\'lishi kerak');
      return;
    }
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      await widget.authService.register(
        name: _nameController.text.isEmpty ? null : _nameController.text.trim(),
        phone: PhoneUtils.normalize(_phoneController.text),
        password: _passwordController.text,
        role: 'client',
        city: null,
        lang: AppStrings.lang,
      );
      if (mounted) Navigator.pushReplacementNamed(context, '/home');
    } catch (e) {
      setState(() => _error = e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(gradient: AppTheme.currentGradient(context)),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 28),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 40),

                // Back
                IconButton(
                  onPressed: () => Navigator.pushReplacementNamed(context, '/login'),
                  icon: const Icon(Icons.arrow_back_rounded, color: AppColors.textPrimary),
                ),
                const SizedBox(height: 16),

                Text(
                  AppStrings.register,
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w800,
                    color: Theme.of(context).textTheme.titleLarge?.color,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  AppStrings.appSlogan,
                  style: TextStyle(fontSize: 14, color: Theme.of(context).textTheme.bodySmall?.color),
                ),
                const SizedBox(height: 24),

                // Error
                if (_error != null)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: AppColors.error.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.error.withValues(alpha: 0.3)),
                    ),
                    child: Text(_error!, style: const TextStyle(color: AppColors.error, fontSize: 13)),
                  ),

                const SizedBox(height: 24),

                // Name
                TextField(
                  controller: _nameController,
                  style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color),
                  decoration: InputDecoration(
                    labelText: AppStrings.name,
                    labelStyle: TextStyle(color: Theme.of(context).textTheme.bodySmall?.color),
                    prefixIcon: Icon(Icons.person_rounded, color: Theme.of(context).hintColor),
                  ),
                ),
                const SizedBox(height: 14),

                // Phone
                TextField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  inputFormatters: [_phoneFormatter],
                  style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color),
                  decoration: InputDecoration(
                    hintText: '+998 (99) 858-56-88',
                    hintStyle: TextStyle(color: Theme.of(context).hintColor),
                    labelText: AppStrings.phone,
                    labelStyle: TextStyle(color: Theme.of(context).textTheme.bodySmall?.color),
                    prefixIcon: Icon(Icons.phone_rounded, color: Theme.of(context).hintColor),
                  ),
                ),
                const SizedBox(height: 14),

                // Password
                TextField(
                  controller: _passwordController,
                  obscureText: _obscurePassword,
                  style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color),
                  decoration: InputDecoration(
                    labelText: AppStrings.password,
                    labelStyle: TextStyle(color: Theme.of(context).textTheme.bodySmall?.color),
                    prefixIcon: Icon(Icons.lock_rounded, color: Theme.of(context).hintColor),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword ? Icons.visibility_off_rounded : Icons.visibility_rounded,
                        color: Theme.of(context).hintColor,
                      ),
                      onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                
                // Privacy Policy Checkbox
                Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Checkbox(
                      value: _acceptedPolicy,
                      activeColor: Theme.of(context).primaryColor,
                      onChanged: (val) {
                        setState(() => _acceptedPolicy = val ?? false);
                      },
                    ),
                    Expanded(
                      child: GestureDetector(
                        onTap: () => _showPrivacyPolicy(context),
                        child: Text(
                          AppStrings.isRu
                            ? 'С политикой конфиденциальности ознакомлен(а) и согласен(а)'
                            : 'Maxfiylik siyosati bilan tanishdim va roziman',
                          style: TextStyle(
                            color: Theme.of(context).primaryColor,
                            fontSize: 13,
                            decoration: TextDecoration.underline,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                // Register button
                GradientButton(
                  text: AppStrings.register,
                  isLoading: _isLoading,
                  icon: Icons.person_add_rounded,
                  onPressed: _acceptedPolicy ? _register : () {
                    setState(() => _error = AppStrings.isRu ? 'Необходимо согласиться с политикой конфиденциальности' : 'Maxfiylik siyosatiga rozi bo\'lishingiz kerak');
                  },
                ),
                const SizedBox(height: 20),

                Center(
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        AppStrings.alreadyHaveAccount,
                        style: const TextStyle(color: AppColors.textSecondary),
                      ),
                      TextButton(
                        onPressed: () => Navigator.pushReplacementNamed(context, '/login'),
                        child: Text(
                          AppStrings.login,
                          style: const TextStyle(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showPrivacyPolicy(BuildContext context) {
    final theme = Theme.of(context);
    showModalBottomSheet(
      context: context,
      backgroundColor: theme.cardTheme.color,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.7,
        maxChildSize: 0.95,
        builder: (_, controller) => Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40, height: 4,
                  decoration: BoxDecoration(
                    color: theme.dividerColor,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                AppStrings.isRu ? 'Политика конфиденциальности' : 'Maxfiylik siyosati',
                style: theme.textTheme.titleMedium,
              ),
              const SizedBox(height: 16),
              Expanded(
                child: ListView(
                  controller: controller,
                  children: [
                    Text(
                      AppStrings.isRu
                        ? '''1. Мы собираем только необходимые данные: имя, номер телефона, город.

2. Ваши данные используются исключительно для работы платформы Yaqin.

3. Мы не передаём ваши данные третьим лицам без вашего согласия.

4. Фото профиля проверяется модераторами. Отсутствие лица на фото может привести к блокировке профиля.

5. 3 плохих отзыва = Блок профиля.

6. Вы можете удалить аккаунт, обратившись в поддержку.

7. Используя приложение, вы принимаете данную политику.'''
                        : '''1. Biz faqat kerakli ma\'lumotlarni yig\'amiz: ism, telefon, shahar.

2. Ma\'lumotlaringiz faqat Yaqin platformasi uchun ishlatiladi.

3. Roziligingizisiz ma\'lumotlaringizni uchinchi shaxslarga bermaymiz.

4. Profil rasmi moderatorlar tomonidan tekshiriladi. Yuzingiz ko'rsatilmagan rasm profilning bloklanishiga olib kelishi mumkin.

5. 3 ta yomon sharh = Profil bloki.

6. Akkauntni o\'chirish uchun qo\'llab-quvvatlash xizmatiga murojaat qiling.

7. Ilovadan foydalanib, siz ushbu siyosatni qabul qilasiz.''',
                      style: theme.textTheme.bodyMedium?.copyWith(height: 1.6),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
}
