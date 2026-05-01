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
import '../../utils/formatters.dart';
import 'chat_screen.dart';
import 'dart:async';
import '../../services/socket_service.dart';

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

  StreamSubscription? _socketSubscription;
  Timer? _countdownTimer;

  @override
  void initState() {
    super.initState();
    _loadOrders();
    _setupSocketListener();
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (mounted) setState(() {});
    });
  }

  void _setupSocketListener() {
    _socketSubscription = SocketService().messageStream.listen((data) {
      if (!mounted) return;
      if (data['type'] == 'order_accepted' || 
          data['type'] == 'order_completed' || 
          data['type'] == 'order_rejected' || 
          data['type'] == 'order_cancelled' ||
          data['type'] == 'vacancy_closed' ||
          data['type'] == 'hr_accepted' ||
          data['type'] == 'hr_expiry_warning') {
        _loadOrders();
      }
    });
  }

  @override
  void dispose() {
    _countdownTimer?.cancel();
    _socketSubscription?.cancel();
    super.dispose();
  }

  Future<void> _loadOrders() async {
    setState(() => _isLoading = true);
    try {
      final role = widget.authService.currentUser?.role;
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

  Future<void> _cancelOrder(int orderId) async {
    final confirmed = await _showConfirmDialog(
      AppStrings.isRu ? 'Отмена заказа' : 'Buyurtmani bekor qilish',
      AppStrings.isRu ? 'Вы уверены, что хотите отменить этот заказ?' : 'Haqiqatan ham ushbu buyurtmani bekor qilmoqchimisiz?',
    );
    if (!confirmed) return;

    try {
      await widget.apiService.cancelOrder(orderId);
      _loadOrders();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  Future<void> _withdrawApplication(int applicationId) async {
    final confirmed = await _showConfirmDialog(
      AppStrings.isRu ? 'Отозвать заявку' : 'Arizani qaytarib olish',
      AppStrings.isRu ? 'Вы уверены, что хотите отозвать эту заявку?' : 'Haqiqatan ham ushbu arizani qaytarib olmoqchimisiz?',
    );
    if (!confirmed) return;

    try {
      await widget.apiService.withdrawJobApplication(applicationId);
      _loadOrders();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  Future<void> _cancelOthers(int orderId) async {
    final confirmed = await _showConfirmDialog(
      AppStrings.isRu ? 'Отменить всем' : 'Barchasini bekor qilish',
      AppStrings.isRu ? 'Отменить все отклики на это HR-объявление? Все мастера получат уведомление об отмене.' : 'Barcha javoblarni bekor qilasizmi? Barcha ustalarga bildirishnoma yuboriladi.',
    );
    if (!confirmed) return;

    try {
      await widget.apiService.cancelOthers(orderId);
      _loadOrders();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  Future<void> _rejectMaster(int orderId) async {
    final confirmed = await _showConfirmDialog(
      AppStrings.reject,
      AppStrings.isRu ? 'Вы уверены, что хотите отклонить этого мастера? Статус заказа станет "Отказано".' : 'Haqiqatan ham ushbu ustani rad etmoqchimisiz? Buyurtma holati "Rad etildi" ga o\'zgaradi.',
    );
    if (!confirmed) return;

    try {
      await widget.apiService.rejectMaster(orderId);
      _loadOrders();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  Future<void> _hrAcceptMaster(int orderId) async {
    final confirmed = await _showConfirmDialog(
      AppStrings.isRu ? 'Принять мастера' : 'Ustani qabul qilish',
      AppStrings.isRu ? 'Вы уверены, что хотите принять этого кандидата?' : 'Haqiqatan ham ushbu nomzodni qabul qilmoqchimisiz?',
    );
    if (!confirmed) return;

    try {
      await widget.apiService.hrAcceptMaster(orderId);
      _loadOrders();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  Future<bool> _showConfirmDialog(String title, String content) async {
    return await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: Text(AppStrings.cancel)),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(AppStrings.ok, style: const TextStyle(color: AppColors.error)),
          ),
        ],
      ),
    ) ?? false;
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
    
    final String myRole = order['my_role'] ?? 'employer';
    final bool isEmployer = myRole == 'employer';
    final bool isWorker = myRole == 'worker';
    
    Color statusColor = Colors.orange;
    String statusText = AppStrings.isRu ? 'Открыто' : 'Ochiq';
    
    final bool isApp = order['is_application'] == true;

    if (status == 'accepted') {
      statusColor = Colors.blue;
      statusText = AppStrings.isRu ? 'Принято' : 'Qabul qilingan';
    } else if (status == 'accepted_hr') {
      statusColor = Colors.green;
      statusText = AppStrings.isRu ? 'Принято' : 'Qabul qilindi';  // Принято (вместо Завершено)
    } else if (status == 'completed') {
      statusColor = Colors.green;
      statusText = AppStrings.isRu ? 'Завершено' : 'Tugallangan';
    } else if (status == 'pending') {
      statusColor = Colors.amber;
      statusText = AppStrings.applicationPending;
    } else if (status == 'viewed') {
      statusColor = Colors.cyan;
      statusText = AppStrings.applicationViewed;
    } else if (status == 'vacancy_closed') {
      statusColor = Colors.deepOrange;
      statusText = AppStrings.isRu ? 'Вакансия закрыта' : 'Vakansiya yopildi';  // Вакансия закрыта (вместо Отказано)
    } else if (status == 'rejected') {
      statusColor = Colors.red;
      statusText = AppStrings.applicationRejected;
    } else if (status == 'cancelled') {
      statusColor = Colors.grey;
      statusText = AppStrings.isRu ? 'Вы отменили заказ' : 'Siz bekor qildingiz';
    }

    // Role badge text
    final String roleBadge = isEmployer
        ? (AppStrings.isRu ? 'Ваш заказ' : 'Sizning buyurtma')
        : (AppStrings.isRu ? 'Вы исполнитель' : 'Siz ijrochi');
    final Color roleBadgeColor = isEmployer ? Colors.deepPurple : Colors.teal;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: theme.cardTheme.color,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isApp ? statusColor.withOpacity(0.3) : theme.dividerColor.withOpacity(0.1),
          width: isApp ? 2 : 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Role badge
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: roleBadgeColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        isEmployer ? Icons.work_outline_rounded : Icons.construction_rounded,
                        size: 12,
                        color: roleBadgeColor,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        roleBadge,
                        style: TextStyle(color: roleBadgeColor, fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                if (isApp) ...[
                  const SizedBox(width: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      AppStrings.isRu ? 'ЗАЯВКА' : 'ARIZA',
                      style: TextStyle(color: statusColor, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ],
            ),
            if (order['is_company'] == true) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.business_rounded, size: 12, color: AppColors.primary),
                    const SizedBox(width: 4),
                    Text(
                      AppStrings.isRu ? 'КОМПАНИЯ' : 'KOMPANIYA',
                      style: const TextStyle(color: AppColors.primary, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 10),
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
            if (order['price'] != null) ...[
              const SizedBox(height: 12),
              Text(
                '${PriceFormatter.format(order['price'])} ${AppStrings.sum}',
                style: TextStyle(color: theme.textTheme.titleLarge?.color, fontSize: 16, fontWeight: FontWeight.w700),
              ),
            ],
            const SizedBox(height: 12),
            _buildOptionsRow(order),
            // Show the OTHER participant
            if (isEmployer && order['master_name'] != null && !(order['is_company'] == true && status == 'open')) ...[
              const SizedBox(height: 16),
              Divider(color: theme.dividerColor.withOpacity(0.1)),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.construction_rounded, color: Colors.teal, size: 16),
                  const SizedBox(width: 8),
                  Text(
                    '${AppStrings.isRu ? 'Мастер:' : 'Usta:'} ${order['master_name']}',
                    style: TextStyle(color: theme.textTheme.bodyLarge?.color, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ],
            if (isWorker && order['client_name'] != null) ...[
              const SizedBox(height: 16),
              Divider(color: theme.dividerColor.withOpacity(0.1)),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.person_rounded, color: Colors.deepPurple, size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${AppStrings.isRu ? 'Заказчик:' : 'Buyurtmachi:'} ${order['client_name']}${order['client_phone'] != null ? ' (${order['client_phone']})' : ''}',
                      style: TextStyle(color: theme.textTheme.bodyLarge?.color, fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
            ],
            if (status == 'accepted' || status == 'completed' || status == 'pending') ...[
              const SizedBox(height: 16),
              GradientButton(
                text: isEmployer
                    ? (AppStrings.isRu ? 'Чат с мастером' : 'Usta bilan chat')
                    : (AppStrings.isRu ? 'Чат с заказчиком' : 'Buyurtmachi bilan chat'),
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
            // Cancel/Withdraw buttons
            if (isEmployer) ...[
              if (isApp && (status == 'pending' || status == 'viewed')) ...[
                const SizedBox(height: 8),
                OutlinedButton.icon(
                  onPressed: () => _withdrawApplication(order['id']),
                  icon: const Icon(Icons.close_rounded, size: 18),
                  label: Text(AppStrings.withdraw),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppColors.error,
                    side: const BorderSide(color: AppColors.error),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    minimumSize: const Size(double.infinity, 45),
                  ),
                ),
              ] else if (!isApp && (status == 'accepted' || status == 'pending')) ...[
                if (order['is_company'] == true) ...[
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => _hrAcceptMaster(order['id']),
                          icon: const Icon(Icons.check_circle_outline_rounded, size: 18),
                          label: Text(AppStrings.isRu ? 'Принять' : 'Qabul qilish'),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: Colors.green,
                            side: const BorderSide(color: Colors.green),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            minimumSize: const Size(0, 45),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => _rejectMaster(order['id']),
                          icon: const Icon(Icons.person_remove_rounded, size: 18),
                          label: Text(AppStrings.reject),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: Colors.redAccent,
                            side: const BorderSide(color: Colors.redAccent),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            minimumSize: const Size(0, 45),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ] else if (!isApp && status == 'open') ...[
                // HR announcement: show Extend button + countdown
                if (order['is_company'] == true) ...[
                  const SizedBox(height: 8),
                  _buildHrExtendSection(order),
                  const SizedBox(height: 8),
                ],
                const SizedBox(height: 8),
                OutlinedButton.icon(
                  onPressed: () => _cancelOrder(order['id']),
                  icon: const Icon(Icons.cancel_outlined, size: 18),
                  label: Text(AppStrings.cancelOrder),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppColors.error,
                    side: const BorderSide(color: AppColors.error),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    minimumSize: const Size(double.infinity, 45),
                  ),
                ),
              ],
            ],
            // Review buttons
            if (status == 'completed') ...[
              if (isEmployer && order['master_id'] != null) ...[
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
              if (isWorker) ...[
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
                    onPressed: () => _showRateClientDialog(context, order),
                  ),
              ],
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

  void _showRateClientDialog(BuildContext context, dynamic order) {
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
              Text(
                AppStrings.isRu ? 'Оценить клиента' : 'Mijozni baholash',
                style: theme.textTheme.titleMedium,
              ),
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

  /// Builds countdown + extend button for open HR announcements.
  /// Shown directly in the card — reliable without WebSocket.
  Widget _buildHrExtendSection(dynamic order) {
    final expiresAtStr = order['expires_at'] as String?;
    DateTime? expiresAt;
    if (expiresAtStr != null) {
      try {
        String parseStr = expiresAtStr;
        if (!parseStr.endsWith('Z')) {
          parseStr += 'Z';
        }
        expiresAt = DateTime.parse(parseStr).toLocal();
      } catch (_) {}
    }

    final now = DateTime.now();
    Duration remaining = expiresAt != null ? expiresAt.difference(now) : Duration.zero;
    final bool isExpiringSoon = remaining.inSeconds <= 120; // Show extend button only in last 2 minutes
    final bool isStillOpen = remaining.inSeconds > 0;

    String countdownText = '';
    if (expiresAt != null) {
      if (!isStillOpen) {
        countdownText = AppStrings.isRu ? 'Объявление закрывается...' : 'E\'lon yopilmoqda...';
      } else {
        final min = remaining.inMinutes;
        final sec = remaining.inSeconds % 60;
        countdownText = AppStrings.isRu
            ? 'Осталось: ${min}м ${sec}с'
            : 'Qoldi: ${min}d ${sec}s';
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (countdownText.isNotEmpty)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: isExpiringSoon
                  ? Colors.orange.withOpacity(0.12)
                  : Colors.blue.withOpacity(0.08),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: isExpiringSoon
                    ? Colors.orange.withOpacity(0.4)
                    : Colors.blue.withOpacity(0.2),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  isExpiringSoon ? Icons.timer_outlined : Icons.schedule_rounded,
                  size: 16,
                  color: isExpiringSoon ? Colors.orange : Colors.blue,
                ),
                const SizedBox(width: 8),
                Text(
                  countdownText,
                  style: TextStyle(
                    color: isExpiringSoon ? Colors.orange : Colors.blue,
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        if (isExpiringSoon && isStillOpen) ...[
          const SizedBox(height: 8),
          ElevatedButton.icon(
            onPressed: () async {
              try {
                await widget.apiService.extendHrAnnouncement(order['id']);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(AppStrings.isRu
                          ? '✅ Объявление продлено ещё на 5 минут!'
                          : '✅ E\'lon yana 5 daqiqaga uzaytirildi!'),
                      backgroundColor: Colors.green,
                    ),
                  );
                  _loadOrders();
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('${AppStrings.isRu ? 'Ошибка:' : 'Xatolik:'} $e'),
                      backgroundColor: AppColors.error,
                    ),
                  );
                }
              }
            },
            icon: const Icon(Icons.more_time_rounded, size: 18),
            label: Text(AppStrings.isRu ? 'Продлить на 5 мин' : 'Ha, 5 daqiqa uzayt.'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              minimumSize: const Size(double.infinity, 45),
            ),
          ),
        ],
      ],
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
