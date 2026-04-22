import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../config/theme.dart';
import '../config/localization.dart';
import '../services/api_service.dart';
import '../models/subscription.dart';
import '../widgets/gradient_button.dart';
import 'card_payment_screen.dart';

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
                    _buildTrialPromo(),
                    const SizedBox(height: 20),
                    if (_sub != null) _buildCurrentStatus(_sub!),
                    const SizedBox(height: 32),
                    Text(
                      isRu ? 'Доступные тарифы' : 'Mavjud tariflar',
                      style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    // Worker tiers
                    Text(
                      isRu ? '👷 Иш олувчи (Работник)' : '👷 Ish oluvchi (Ishchi)',
                      style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    _tierCard('day', '1 День', '5,000 Сум', '1 Объявление', Icons.bolt_rounded, 5000),
                    _tierCard('week', '1 Неделя', '30,000 Сум', '10 Объявлений', Icons.auto_awesome_rounded, 30000),
                    _tierCard('month', '1 Месяц', '150,000 Сум', '45 Объявлений', Icons.star_rounded, 150000, isBest: true),
                    const SizedBox(height: 24),
                    // Employer tiers
                    Text(
                      isRu ? '💼 Иш берувчи (Работодатель)' : '💼 Ish beruvchi (Ish beruvchi)',
                      style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    _tierCard('day', '1 День', '20,000 Сум', '1 Объявление', Icons.bolt_rounded, 20000),
                    _tierCard('week', '1 Неделя', '150,000 Сум', '10 Объявлений', Icons.auto_awesome_rounded, 150000),
                    _tierCard('month', '1 Месяц', '300,000 Сум', '30 Объявлений', Icons.star_rounded, 300000, isBest: true),
                    
                    const SizedBox(height: 32),
                    _buildPaymentInfo(),
                    const SizedBox(height: 40),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildTrialPromo() {
    final isRu = AppStrings.isRu;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF00C853), Color(0xFF00E676)],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [BoxShadow(color: const Color(0xFF00C853).withOpacity(0.3), blurRadius: 15, offset: const Offset(0, 8))],
      ),
      child: Row(
        children: [
          const Icon(Icons.card_giftcard_rounded, color: Colors.white, size: 40),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isRu ? '🎉 АКЦИЯ!' : '🎉 AKSIYA!',
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 18),
                ),
                const SizedBox(height: 4),
                Text(
                  isRu ? 'Первые 2 минуты — БЕСПЛАТНО!\nПосле регистрации вы получаете полный доступ.' : 'Birinchi 2 daqiqa — BEPUL!\nRo\'yxatdan o\'tganingizdan keyin to\'liq kirish.',
                  style: const TextStyle(color: Colors.white, fontSize: 13, height: 1.4),
                ),
              ],
            ),
          ),
        ],
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

  Widget _tierCard(String planId, String title, String price, String limit, IconData icon, int priceVal, {bool isBest = false}) {
    final theme = Theme.of(context);
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: theme.cardTheme.color,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: isBest ? AppColors.primary : theme.dividerColor.withOpacity(0.1), width: isBest ? 2 : 1),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: (isBest ? AppColors.primary : theme.primaryColor).withOpacity(0.1),
            borderRadius: BorderRadius.circular(14),
          ),
          child: Icon(icon, color: isBest ? AppColors.primary : theme.primaryColor),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        subtitle: Text(limit, style: theme.textTheme.bodySmall),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(price, style: TextStyle(fontWeight: FontWeight.w900, color: isBest ? AppColors.primary : theme.textTheme.bodyLarge?.color, fontSize: 16)),
            const SizedBox(height: 4),
            Text(AppStrings.isRu ? 'Купить' : 'Sotib olish', style: const TextStyle(color: AppColors.primary, fontSize: 12, fontWeight: FontWeight.bold)),
          ],
        ),
        onTap: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => CardPaymentScreen(
                apiService: widget.apiService,
                planName: planId,
                price: priceVal,
              ),
            ),
          );
          if (result == true) {
            _loadSubscription();
          }
        },
      ),
    );
  }

  Widget _buildPaymentInfo() {
    final theme = Theme.of(context);
    final isRu = AppStrings.isRu;
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.05),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: theme.dividerColor.withOpacity(0.1)),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Image.network('https://upload.wikimedia.org/wikipedia/commons/b/b5/Payme_logo.png', height: 24, errorBuilder: (_,__,___) => const SizedBox()),
              const SizedBox(width: 12),
              Image.network('https://click.uz/static/img/logo.png', height: 24, errorBuilder: (_,__,___) => const SizedBox()),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            isRu 
              ? 'Выберите подходящий тариф и оплатите онлайн любой картой Узбекистана (Uzcard/Humo).' 
              : 'Mos tarifni tanlang va har qanday O\'zbekiston kartasi (Uzcard/Humo) orqali onlayn to\'lang.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 13, color: theme.hintColor),
          ),
        ],
      ),
    );
  }
}
