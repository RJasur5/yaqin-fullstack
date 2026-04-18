import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../config/theme.dart';
import '../config/localization.dart';
import '../services/api_service.dart';
import '../models/subscription.dart';
import '../widgets/gradient_button.dart';

class SubscriptionScreen extends StatefulWidget {
  final ApiService apiService;
  const SubscriptionScreen({super.key, required this.apiService});

  @override
  State<SubscriptionScreen> createState() => _SubscriptionScreenState();
}

class _SubscriptionScreenState extends State<SubscriptionScreen> {
  SubscriptionModel? _sub;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSubscription();
  }

  Future<void> _loadSubscription() async {
    try {
      final sub = await widget.apiService.getMySubscription();
      if (mounted) setState(() { _sub = sub; _isLoading = false; });
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isRu = AppStrings.isRu;

    return Container(
      decoration: BoxDecoration(gradient: AppTheme.currentGradient(context)),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          title: Text(isRu ? 'Подписка' : 'Obuna'),
          backgroundColor: Colors.transparent,
          elevation: 0,
        ),
        body: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (_sub != null) _buildCurrentStatus(_sub!),
                    const SizedBox(height: 32),
                    Text(
                      isRu ? 'Доступные тарифы' : 'Mavjud tariflar',
                      style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    // Show based on role
                    if (_sub?.userRole == 'master' || _sub?.userRole == 'admin')
                      ..._buildWorkerTiers()
                    else
                      ..._buildEmployerTiers(),
                    
                    const SizedBox(height: 32),
                    _buildPaymentInfo(),
                    const SizedBox(height: 40),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildCurrentStatus(SubscriptionModel sub) {
    final theme = Theme.of(context);
    final isRu = AppStrings.isRu;
    final expiryStr = DateFormat('dd.MM.yyyy HH:mm').format(sub.expiresAt.toLocal());
    
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: sub.isActive ? [AppColors.primary, AppColors.secondary] : [Colors.grey, Colors.grey.shade700],
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(color: (sub.isActive ? AppColors.primary : Colors.black).withOpacity(0.3), blurRadius: 15, offset: const Offset(0, 8)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                sub.planTitle.toUpperCase(),
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 20, letterSpacing: 1.2),
              ),
              Icon(sub.isActive ? Icons.verified_rounded : Icons.info_outline_rounded, color: Colors.white, size: 28),
            ],
          ),
          const SizedBox(height: 20),
          Text(
            isRu ? 'Статус: ${sub.isActive ? "Активна" : "Истекла"}' : 'Holati: ${sub.isActive ? "Faol" : "Muddati o'tgan"}',
            style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Text(
            isRu ? 'Истекает: $expiryStr' : 'Tugash vaqti: $expiryStr',
            style: TextStyle(color: Colors.white.withOpacity(0.9), fontSize: 14),
          ),
          if (sub.isActive) ...[
             const SizedBox(height: 16),
             ClipRRect(
               borderRadius: BorderRadius.circular(10),
               child: LinearProgressIndicator(
                 value: sub.adsUsed / sub.adsLimit,
                 backgroundColor: Colors.white.withOpacity(0.2),
                 valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                 minHeight: 8,
               ),
             ),
             const SizedBox(height: 8),
             Text(
               isRu ? 'Использовано объявлений: ${sub.adsUsed} из ${sub.adsLimit}' : 'Ishlatilgan e\'lonlar: ${sub.adsUsed} dan ${sub.adsLimit}',
               style: TextStyle(color: Colors.white.withOpacity(0.9), fontSize: 13),
             ),
          ],
        ],
      ),
    );
  }

  List<Widget> _buildWorkerTiers() {
    return [
      _tierCard('1 День', '5,000 Сум', '1 Объявление', Icons.bolt_rounded),
      _tierCard('1 Неделя', '30,000 Сум', '10 Объявлений', Icons.auto_awesome_rounded),
      _tierCard('1 Месяц', '150,000 Сум', '45 Объявлений', Icons.star_rounded, isBest: true),
    ];
  }

  List<Widget> _buildEmployerTiers() {
    return [
      _tierCard('1 День', '20,000 Сум', '1 Объявление', Icons.bolt_rounded),
      _tierCard('1 Неделя', '150,000 Сум', '10 Объявлений', Icons.auto_awesome_rounded),
      _tierCard('1 Месяц', '300,000 Сум', '30 Объявлений', Icons.star_rounded, isBest: true),
    ];
  }

  Widget _tierCard(String title, String price, String limit, IconData icon, {bool isBest = false}) {
    final theme = Theme.of(context);
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: theme.cardTheme.color,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: isBest ? AppColors.primary : theme.dividerColor.withOpacity(0.1), width: isBest ? 2 : 1),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: (isBest ? AppColors.primary : theme.primaryColor).withOpacity(0.1),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(icon, color: isBest ? AppColors.primary : theme.primaryColor),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 4),
                Text(limit, style: theme.textTheme.bodySmall),
              ],
            ),
          ),
          Text(price, style: TextStyle(fontWeight: FontWeight.w900, color: isBest ? AppColors.primary : theme.textTheme.bodyLarge?.color, fontSize: 16)),
        ],
      ),
    );
  }

  Widget _buildPaymentInfo() {
    final theme = Theme.of(context);
    final isRu = AppStrings.isRu;
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.warning.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.warning.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          const Icon(Icons.info_outline_rounded, color: AppColors.warning, size: 32),
          const SizedBox(height: 12),
          Text(
            isRu ? 'Как активировать?' : 'Qanday faollashtirish kerak?',
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 17, color: AppColors.warning),
          ),
          const SizedBox(height: 8),
          Text(
            isRu 
              ? 'На данный момент активация происходит вручную. Пожалуйста, свяжитесь с администрацией для оплаты и активации тарифа.' 
              : 'Hozirda faollashtirish qo\'lda amalga oshiriladi. To\'lov va tarifni faollashtirish uchun ma\'muriyat bilan bog\'laning.',
            textAlign: TextAlign.center,
            style: TextStyle(height: 1.5, color: theme.textTheme.bodyMedium?.color),
          ),
          const SizedBox(height: 20),
          GradientButton(
            text: isRu ? 'Связаться с Администратором' : 'Admin bilan bog\'lanish',
            onPressed: () {
              // Open Link/Telegram (can use url_launcher later)
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Telegram: @yaqin_admin')));
            },
          ),
        ],
      ),
    );
  }
}
