import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../config/theme.dart';
import '../../config/localization.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../widgets/gradient_button.dart';
import '../../widgets/rating_stars.dart';
import '../../utils/date_utils.dart';
import 'chat_screen.dart';

class AcceptedOrdersScreen extends StatefulWidget {
  final ApiService apiService;
  final AuthService authService;
  const AcceptedOrdersScreen({super.key, required this.apiService, required this.authService});

  @override
  State<AcceptedOrdersScreen> createState() => _AcceptedOrdersScreenState();
}

class _AcceptedOrdersScreenState extends State<AcceptedOrdersScreen> {
  List<dynamic> _orders = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  Future<void> _loadOrders() async {
    setState(() => _isLoading = true);
    try {
      final orders = await widget.apiService.getMyOrders(type: 'master');
      if (mounted) {
        setState(() {
          _orders = orders;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Failed to load accepted orders';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(AppStrings.isRu ? 'Принятые заказы' : 'Qabul qilingan buyurtmalar'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: theme.textTheme.titleLarge?.color,
        actions: [
          IconButton(onPressed: _loadOrders, icon: const Icon(Icons.refresh_rounded)),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(gradient: AppTheme.currentGradient(context)),
        child: _isLoading
            ? Center(child: CircularProgressIndicator(color: theme.primaryColor))
            : _orders.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _orders.length,
                    itemBuilder: (context, index) {
                      final order = _orders[index];
                      return _buildOrderCard(context, order);
                    },
                  ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Text(
        AppStrings.isRu ? 'У вас пока нет принятых заказов' : 'Hozircha qabul qilingan buyurtmalar yo\'q',
        style: const TextStyle(color: AppColors.textHint, fontSize: 16),
      ),
    );
  }

  Widget _buildOrderCard(BuildContext context, dynamic order) {
    final theme = Theme.of(context);
    final subName = AppStrings.isRu ? order['subcategory_name_ru'] : order['subcategory_name_uz'];
    final status = order['status'];
    final date = DateTimeUtils.parseUtc(order['created_at']);
    final formattedDate = DateTimeUtils.formatFull(date);
    
    Color statusColor = Colors.orange;
    String statusText = AppStrings.isRu ? 'Открыто' : 'Ochiq';
    
    if (status == 'accepted') {
      statusColor = Colors.blue;
      statusText = AppStrings.isRu ? 'Принято' : 'Qabul qilingan';
    } else if (status == 'completed') {
      statusColor = Colors.green;
      statusText = AppStrings.isRu ? 'Завершено' : 'Tugallangan';
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: theme.cardTheme.color,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: theme.dividerColor.withOpacity(0.1)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    subName,
                    style: TextStyle(color: theme.primaryColor, fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    statusText,
                    style: TextStyle(color: statusColor, fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              formattedDate,
              style: const TextStyle(color: AppColors.textHint, fontSize: 12),
            ),
            const SizedBox(height: 12),
            Text(
              order['description'],
              style: TextStyle(color: theme.textTheme.bodyLarge?.color, fontSize: 15),
            ),
            const SizedBox(height: 16),
            Divider(color: theme.dividerColor.withOpacity(0.1)),
            const SizedBox(height: 8),
            Row(
              children: [
                 Icon(Icons.person_rounded, color: theme.hintColor, size: 16),
                 const SizedBox(width: 8),
                 Text(
                   '${AppStrings.isRu ? 'Клиент:' : 'Mijoz:'} ${order['client_name']}',
                   style: TextStyle(color: theme.textTheme.bodyLarge?.color, fontWeight: FontWeight.w600),
                 ),
                 const Spacer(),
                 Text(
                   order['client_phone'],
                   style: TextStyle(color: theme.primaryColor, fontWeight: FontWeight.bold),
                 ),
              ],
            ),
            if (status == 'accepted' || status == 'completed') ...[
              const SizedBox(height: 16),
              GradientButton(
                text: AppStrings.isRu ? 'Чат с клиентом' : 'Mijoz bilan chat',
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => ChatScreen(
                        order: order,
                        apiService: widget.apiService,
                        currentUserId: widget.authService.currentUser?.id ?? 0,
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 12),
              if (order['is_client_reviewed'] == true)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  decoration: BoxDecoration(
                    color: theme.dividerColor.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: theme.dividerColor.withOpacity(0.1)),
                  ),
                  child: Center(
                    child: Text(
                      AppStrings.isRu ? 'Вы уже оценили клиента' : 'Mijoz baholangan',
                      style: TextStyle(color: theme.hintColor, fontWeight: FontWeight.w600),
                    ),
                  ),
                )
              else
                GradientButton(
                  text: AppStrings.isRu ? 'Оценить клиента' : 'Mijozni baholash',
                  onPressed: () => _showRateClientDialog(order),
                ),
            ],
          ],
        ),
      ),
    );
  }

  void _showRateClientDialog(dynamic order) {
    final theme = Theme.of(context);
    int rating = 5;
    final commentController = TextEditingController();

    showModalBottomSheet(
      context: context,
      backgroundColor: theme.cardTheme.color,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) => Padding(
          padding: EdgeInsets.fromLTRB(20, 20, 20, MediaQuery.of(context).viewInsets.bottom + 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Center(
                child: Container(
                  width: 40, height: 4,
                  decoration: BoxDecoration(
                    color: theme.textTheme.bodySmall?.color?.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Text(AppStrings.isRu ? 'Оценить клиента' : 'Mijozni baholash', style: theme.textTheme.titleMedium),
              const SizedBox(height: 20),
              RatingInput(
                value: rating,
                onChanged: (v) => setModalState(() => rating = v),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: commentController,
                maxLines: 3,
                style: theme.textTheme.bodyLarge,
                decoration: InputDecoration(
                  hintText: AppStrings.isRu ? 'Ваш отзыв о клиенте...' : 'Mijoz haqida fikringiz...',
                ),
              ),
              const SizedBox(height: 20),
              GradientButton(
                text: AppStrings.save,
                onPressed: () async {
                  try {
                    await widget.apiService.rateClient(order['id'], rating, commentController.text);
                    if (mounted) {
                      Navigator.pop(context);
                      _loadOrders();
                    }
                  } catch (e) {
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Ошибка: $e'), backgroundColor: AppColors.error),
                      );
                    }
                  }
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
