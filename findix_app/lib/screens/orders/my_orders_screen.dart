import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../config/theme.dart';
import '../../config/localization.dart';
import '../../services/api_service.dart';
import '../../widgets/gradient_button.dart';
import '../../services/auth_service.dart';
import '../../services/theme_service.dart';
import 'create_order_screen.dart';
import '../../widgets/rating_stars.dart';
import '../../utils/date_utils.dart';
import 'chat_screen.dart';

class MyOrdersScreen extends StatefulWidget {
  final ApiService apiService;
  final AuthService authService;
  const MyOrdersScreen({super.key, required this.apiService, required this.authService});

  @override
  State<MyOrdersScreen> createState() => _MyOrdersScreenState();
}

class _MyOrdersScreenState extends State<MyOrdersScreen> {
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
      final orders = await widget.apiService.getMyOrders(type: 'client');
      if (mounted) {
        setState(() {
          _orders = orders;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Failed to load orders';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      decoration: BoxDecoration(gradient: AppTheme.currentGradient(context)),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        extendBodyBehindAppBar: true,
        appBar: AppBar(
          title: Text(AppStrings.isRu ? 'Мои заказы' : 'Mening buyurtmalarim'),
          backgroundColor: Colors.transparent,
          elevation: 0,
          foregroundColor: theme.textTheme.bodyLarge?.color,
          actions: [
            IconButton(onPressed: _loadOrders, icon: const Icon(Icons.refresh_rounded)),
          ],
        ),
        body: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : _orders.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    padding: const EdgeInsets.only(top: 100, left: 16, right: 16, bottom: 100),
                    itemCount: _orders.length,
                    itemBuilder: (context, index) {
                      final order = _orders[index];
                      return _buildOrderCard(context, order);
                    },
                  ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => CreateOrderScreen(
                  apiService: widget.apiService,
                  authService: widget.authService,
                ),
              ),
            ).then((res) {
              if (res == true) _loadOrders();
            });
          },
          label: Text(AppStrings.isRu ? 'Подать объявление' : 'E\'lon berish'),
          icon: const Icon(Icons.add_rounded),
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Text(
        AppStrings.isRu ? 'У вас пока нет заказов' : 'Hozircha buyurtmalaringiz yo\'q',
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
    
    debugPrint('TIME DEBUG MY: Raw=${order['created_at']} | Local=${date.toString()}');
    
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
            const SizedBox(height: 12),
            _buildOptionsRow(order),
            if (order['master_name'] != null) ...[
              const SizedBox(height: 16),
              Divider(color: theme.dividerColor.withOpacity(0.1)),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.person_pin_rounded, color: theme.hintColor, size: 16),
                  const SizedBox(width: 8),
                  Text(
                    '${AppStrings.isRu ? 'Мастер:' : 'Usta:'} ${order['master_name']}',
                    style: TextStyle(color: theme.textTheme.bodyLarge?.color, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ],
            if (order['client_name'] != null && order['status'] == 'accepted') ...[
              const SizedBox(height: 16),
              Divider(color: theme.dividerColor.withOpacity(0.1)),
              const SizedBox(height: 8),
              Row(
                children: [
                   Icon(Icons.phone_rounded, color: theme.hintColor, size: 16),
                   const SizedBox(width: 8),
                   Text(
                     '${AppStrings.isRu ? 'Клиент:' : 'Mijoz:'} ${order['client_name']} (${order['client_phone']})',
                     style: TextStyle(color: theme.textTheme.bodyLarge?.color, fontWeight: FontWeight.w600),
                   ),
                ],
              ),
            ],
            if (status == 'accepted' || status == 'completed') ...[
              const SizedBox(height: 16),
              GradientButton(
                text: AppStrings.isRu ? 'Чат с мастером' : 'Usta bilan chat',
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
            ],
            if (status == 'completed' && order['master_id'] != null) ...[
              if (order['is_master_reviewed'] == true)
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
                      AppStrings.isRu ? 'Вы уже оценили мастера' : 'Usta baholangan',
                      style: TextStyle(color: theme.hintColor, fontWeight: FontWeight.w600),
                    ),
                  ),
                )
              else
                GradientButton(
                  text: AppStrings.isRu ? 'Оценить мастера' : 'Ustani baholash',
                  onPressed: () => _showRateMasterDialog(context, order),
                ),
            ],
          ],
        ),
      ),
    );
  }

  void _showRateMasterDialog(BuildContext context, dynamic order) {
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
              Text(AppStrings.writeReview, style: theme.textTheme.titleMedium),
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
                  hintText: AppStrings.isRu ? 'Ваш комментарий...' : 'Sharhingiz...',
                ),
              ),
              const SizedBox(height: 20),
              GradientButton(
                text: AppStrings.save,
                onPressed: () async {
                  try {
                    await widget.apiService.rateMasterByOrder(order['id'], rating, commentController.text);
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

  Widget _buildOptionsRow(dynamic order) {
    final theme = Theme.of(context);
    final includeLunch = order['include_lunch'] == true;
    final includeTaxi = order['include_taxi'] == true;

    if (!includeLunch && !includeTaxi) return const SizedBox.shrink();

    return Wrap(
      spacing: 8,
      children: [
        if (includeLunch)
          _buildOptionBadge(
            icon: Icons.restaurant_rounded,
            label: AppStrings.includeLunch,
            color: Colors.orange,
          ),
        if (includeTaxi)
          _buildOptionBadge(
            icon: Icons.local_taxi_rounded,
            label: AppStrings.includeTaxi,
            color: Colors.blue,
          ),
      ],
    );
  }

  Widget _buildOptionBadge({required IconData icon, required String label, required Color color}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}

class RatingInput extends StatelessWidget {
  final int value;
  final Function(int) onChanged;

  const RatingInput({super.key, required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(5, (index) {
        return IconButton(
          icon: Icon(
            index < value ? Icons.star_rounded : Icons.star_outline_rounded,
            color: Colors.amber,
            size: 40,
          ),
          onPressed: () => onChanged(index + 1),
        );
      }),
    );
  }
}
