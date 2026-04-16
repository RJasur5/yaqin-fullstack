import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../config/theme.dart';
import '../../config/localization.dart';
import '../../services/api_service.dart';
import '../../services/theme_service.dart';
import '../../widgets/glass_container.dart';
import '../../widgets/gradient_button.dart';
import '../../models/category.dart';
import '../client_profile_screen.dart';
import '../../widgets/rating_stars.dart';
import '../../config/api_config.dart';
import '../../widgets/full_screen_image.dart';
import '../../utils/date_utils.dart';

class AvailableOrdersScreen extends StatefulWidget {
  final ApiService apiService;
  final List<CategoryModel> categories;
  final int? initialCategoryId;
  const AvailableOrdersScreen({super.key, required this.apiService, this.categories = const [], this.initialCategoryId});

  @override
  State<AvailableOrdersScreen> createState() => _AvailableOrdersScreenState();
}

class _AvailableOrdersScreenState extends State<AvailableOrdersScreen> {
  List<dynamic> _orders = [];
  bool _isLoading = true;
  String? _error;
  
  int? _selectedCategoryId;
  int? _selectedSubcategoryId;
  String _searchQuery = '';
  String? _selectedSearchCity;

  final List<String> _uzbekistanCities = [
    'Toshkent', 'Samarqand', 'Buxoro', 'Andijon', 'Namangan', 'Farg\'ona', 
    'Nukus', 'Navoiy', 'Urganch', 'Qarshi', 'Jizzax', 'Termiz', 'Xiva', 'Guliston'
  ];
  final _searchController = TextEditingController();


  @override
  void initState() {
    super.initState();
    _selectedCategoryId = widget.initialCategoryId;
    _loadOrders();
  }

  Future<void> _loadOrders() async {
    setState(() => _isLoading = true);
    try {
      final orders = await widget.apiService.getAvailableOrders(
        categoryId: _selectedCategoryId,
        subcategoryId: _selectedSubcategoryId,
        city: _selectedSearchCity,
        search: _searchQuery.isNotEmpty ? _searchQuery : null,
      );

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

  Future<void> _acceptOrder(int orderId) async {
    try {
      await widget.apiService.acceptOrder(orderId);
      if (mounted) {
        _loadOrders();
      }
    } catch (e) {
      if (mounted) {
        final errorMsg = e.toString();
        if (errorMsg.contains('already accepted')) {
          _showAlreadyAcceptedDialog();
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(errorMsg)),
          );
        }
      }
    }
  }

  void _showAlreadyAcceptedDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Theme.of(context).cardTheme.color,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            const Icon(Icons.warning_amber_rounded, color: Colors.orange),
            const SizedBox(width: 10),
            Text(
              AppStrings.isRu ? 'Вы не успели' : 'Ulgurmadingiz',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        content: Text(
          AppStrings.isRu 
            ? 'Этот заказ только что принял другой мастер. Не расстраивайтесь, скоро появятся новые заказы!' 
            : 'Bu buyurtmani boshqa usta qabul qilib bo\'ldi. Xafa bo\'lmang, tez orada yangi buyurtmalar paydo bo\'ladi!',
          style: const TextStyle(fontSize: 16),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              _loadOrders();
            },
            child: Text(
              AppStrings.isRu ? 'Понятно' : 'Tushunarli',
              style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
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
          title: Text(AppStrings.isRu ? 'Доступные заказы' : 'Mavjud buyurtmalar'),
          backgroundColor: Colors.transparent,
          elevation: 0,
          foregroundColor: theme.textTheme.bodyLarge?.color,
          actions: [
            IconButton(onPressed: _loadOrders, icon: const Icon(Icons.refresh_rounded)),
          ],
        ),
        body: Padding(
          padding: const EdgeInsets.only(top: 80),
          child: Column(
            children: [
              _buildSearchAndFilters(),
              Expanded(
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
                    : _orders.isEmpty
                        ? _buildEmptyState()
                        : RefreshIndicator(
                            onRefresh: _loadOrders,
                            color: AppColors.primary,
                            child: ListView.builder(
                              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                              itemCount: _orders.length,
                              itemBuilder: (context, index) {
                                final order = _orders[index];
                                return _buildOrderCard(order);
                              },
                            ),
                          ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSearchAndFilters() {
    final theme = Theme.of(context);
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _searchController,
                  style: theme.textTheme.bodyLarge,
                  onChanged: (v) {
                    setState(() => _searchQuery = v);
                    _loadOrders();
                  },
                  decoration: InputDecoration(
                    hintText: AppStrings.searchHint,
                    prefixIcon: Icon(Icons.search_rounded, color: theme.textTheme.bodySmall?.color),
                    suffixIcon: _searchQuery.isNotEmpty 
                      ? IconButton(
                          icon: Icon(Icons.clear_rounded, color: theme.textTheme.bodySmall?.color),
                          onPressed: () {
                            _searchController.clear();
                            setState(() => _searchQuery = '');
                            _loadOrders();
                          },
                        )
                      : null,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              _buildCityPicker(),
            ],
          ),
        ),
        if (widget.categories.isNotEmpty)
          SizedBox(
            height: 48,
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              scrollDirection: Axis.horizontal,
              itemCount: widget.categories.length + 1,
              itemBuilder: (context, index) {
                if (index == 0) {
                  return _buildFilterChip(
                    label: AppStrings.isRu ? 'Все' : 'Barchasi',
                    selected: _selectedCategoryId == null,
                    onSelected: (s) {
                      setState(() {
                        _selectedCategoryId = null;
                        _selectedSubcategoryId = null;
                      });
                      _loadOrders();
                    },
                  );
                }
                final cat = widget.categories[index - 1];
                return _buildFilterChip(
                  label: cat.name(AppStrings.lang),
                  selected: _selectedCategoryId == cat.id,
                  onSelected: (s) {
                    setState(() {
                      _selectedCategoryId = cat.id;
                      _selectedSubcategoryId = null;
                    });
                    _loadOrders();
                  },
                );
              },
            ),
          ),
        if (_selectedCategoryId != null) ...[
          const SizedBox(height: 12),
          _buildSubcategoryRibbon(),
        ],
        const SizedBox(height: 12),
      ],
    );
  }

  Widget _buildCityPicker() {
    final theme = Theme.of(context);
    return PopupMenuButton<String?>(
      initialValue: _selectedSearchCity,
      tooltip: AppStrings.isRu ? 'Выбрать город' : 'Shaharni tanlash',
      onSelected: (String? value) {
        setState(() {
          _selectedSearchCity = value;
        });
        _loadOrders();
      },
      child: Container(
        height: 52,
        width: 52,
        decoration: BoxDecoration(
          color: theme.cardTheme.color,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: theme.dividerColor.withOpacity(0.5)),
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            Icon(
              Icons.tune_rounded, // filter/settings icon as requested
              color: _selectedSearchCity == null ? theme.hintColor : theme.primaryColor,
              size: 24,
            ),
            if (_selectedSearchCity != null)
              Positioned(
                right: 12,
                top: 12,
                child: Container(
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(
                    color: theme.primaryColor,
                    shape: BoxShape.circle,
                    border: Border.all(color: theme.cardTheme.color ?? theme.scaffoldBackgroundColor, width: 2),
                  ),
                ),
              ),
          ],
        ),
      ),

      itemBuilder: (BuildContext context) {
        return [
          PopupMenuItem<String?>(
            value: null,
            child: Row(
              children: [
                Icon(Icons.all_inclusive, size: 18, color: theme.hintColor),
                const SizedBox(width: 10),
                Text(AppStrings.isRu ? 'Все города' : 'Barcha shaharlar'),
              ],
            ),
          ),
          ..._uzbekistanCities.map((String city) {
            final isSelected = _selectedSearchCity == city;
            return PopupMenuItem<String?>(
              value: city,
              child: Row(
                children: [
                  Icon(
                    Icons.location_city_rounded, 
                    size: 18, 
                    color: isSelected ? theme.primaryColor : theme.primaryColor.withOpacity(0.4)
                  ),
                  const SizedBox(width: 10),
                  Text(
                    city,
                    style: TextStyle(
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      color: isSelected ? theme.primaryColor : theme.textTheme.bodyLarge?.color,
                    ),
                  ),
                ],
              ),
            );
          }),
        ];
      },
    );
  }


  Widget _buildFilterChip({required String label, required bool selected, required Function(bool) onSelected}) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text(label),
        selected: selected,
        onSelected: onSelected,
        backgroundColor: theme.cardTheme.color,
        selectedColor: theme.primaryColor,
        checkmarkColor: Colors.white,
        labelStyle: TextStyle(
          color: selected ? Colors.white : theme.textTheme.bodyMedium?.color,
          fontWeight: selected ? FontWeight.bold : FontWeight.normal,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: selected ? theme.primaryColor : theme.dividerColor.withOpacity(0.1)),
        ),
      ),
    );
  }

  Widget _buildSubcategoryRibbon() {
    final cat = widget.categories.firstWhere((c) => c.id == _selectedCategoryId);
    return SizedBox(
      height: 36,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        scrollDirection: Axis.horizontal,
        itemCount: cat.subcategories.length + 1,
        itemBuilder: (context, index) {
          if (index == 0) {
            return _buildSmallChip(
              label: AppStrings.isRu ? 'Все специальности' : 'Barcha mutaxassisliklar',
              selected: _selectedSubcategoryId == null,
              onTap: () {
                setState(() => _selectedSubcategoryId = null);
                _loadOrders();
              },
            );
          }
          final sub = cat.subcategories[index - 1];
          return _buildSmallChip(
            label: sub.name(AppStrings.lang),
            selected: _selectedSubcategoryId == sub.id,
            onTap: () {
              setState(() => _selectedSubcategoryId = sub.id);
              _loadOrders();
            },
          );
        },
      ),
    );
  }

  Widget _buildSmallChip({required String label, required bool selected, required VoidCallback onTap}) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          decoration: BoxDecoration(
            color: selected ? theme.primaryColor.withOpacity(0.15) : Colors.transparent,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: selected ? theme.primaryColor : theme.dividerColor.withOpacity(0.3),
              width: 1,
            ),
          ),
          child: Text(
            label,
            style: theme.textTheme.labelSmall?.copyWith(
              color: selected ? theme.primaryColor : theme.textTheme.bodySmall?.color,
              fontWeight: selected ? FontWeight.bold : FontWeight.w600,
              fontSize: 12,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.assignment_late_rounded, size: 80, color: theme.textTheme.bodySmall?.color?.withOpacity(0.2)),
          const SizedBox(height: 16),
          Text(
            AppStrings.isRu ? 'Нет доступных заказов' : 'Mavjud buyurtmalar yo\'q',
            style: theme.textTheme.titleMedium?.copyWith(color: theme.textTheme.bodySmall?.color),
          ),
          const SizedBox(height: 8),
          Text(
            AppStrings.isRu ? 'Попробуйте обновить позже' : 'Keyinroq yangilab ko\'ring',
            style: theme.textTheme.bodySmall,
          ),
        ],
      ),
    );
  }

  Widget _buildOrderCard(dynamic order) {
    final theme = Theme.of(context);
    final subName = AppStrings.isRu ? order['subcategory_name_ru'] : order['subcategory_name_uz'];
    final date = DateTimeUtils.parseUtc(order['created_at']);
    final formattedDate = DateTimeUtils.formatFull(date);
    
    // Debug to console to verify the 5-hour shift
    debugPrint('TIME DEBUG: Raw=${order['created_at']} | Local=${date.toString()}');

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
                Text(
                  formattedDate,
                  style: TextStyle(color: theme.textTheme.bodySmall?.color, fontSize: 12),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.location_on_rounded, color: theme.textTheme.bodyMedium?.color, size: 14),
                const SizedBox(width: 4),
                Text(
                  '${order['city']}, ${order['district'] ?? ''}',
                  style: TextStyle(color: theme.textTheme.bodyMedium?.color, fontSize: 13),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              order['description'],
              style: TextStyle(color: theme.textTheme.bodyLarge?.color, fontSize: 15),
            ),
            const SizedBox(height: 12),
            _buildOptionsRow(order),
            const SizedBox(height: 16),
            Divider(color: theme.dividerColor.withOpacity(0.1)),
            const SizedBox(height: 12),
            GestureDetector(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (ctx) => ClientProfileScreen(
                      clientId: order['client_id'],
                      apiService: widget.apiService,
                    ),
                  ),
                );
              },
              child: Row(
                children: [
                   GestureDetector(
                     onTap: () {
                       final avatarUrl = order['client_avatar'] != null && order['client_avatar'].toString().isNotEmpty
                         ? (order['client_avatar'].toString().startsWith('http') 
                             ? order['client_avatar'] 
                             : '${ApiConfig.baseUrl}${order['client_avatar']}')
                         : null;
                       if (avatarUrl != null) {
                         Navigator.push(context, MaterialPageRoute(builder: (_) => FullScreenImage(imageUrl: avatarUrl, tag: 'order_avatar_${order['id']}')));
                       }
                     },
                     child: Hero(
                       tag: 'order_avatar_${order['id']}',
                       child: ClipOval(
                         child: order['client_avatar'] != null && order['client_avatar'].toString().isNotEmpty
                           ? Image.network(
                               order['client_avatar'].toString().startsWith('http') 
                                 ? order['client_avatar'] 
                                 : '${ApiConfig.baseUrl}${order['client_avatar']}',
                               width: 40,
                               height: 40,
                               fit: BoxFit.cover,
                               errorBuilder: (context, error, stackTrace) => Icon(Icons.person_outline_rounded, color: theme.primaryColor, size: 40),
                             )
                           : Icon(Icons.person_outline_rounded, color: theme.primaryColor, size: 40),
                       ),
                     ),
                   ),
                   const SizedBox(width: 12),
                   Expanded(
                     child: GestureDetector(
                       behavior: HitTestBehavior.opaque,
                       onTap: () {
                         Navigator.push(
                           context,
                           MaterialPageRoute(
                             builder: (ctx) => ClientProfileScreen(
                               clientId: order['client_id'],
                               apiService: widget.apiService,
                             ),
                           ),
                         );
                       },
                       child: Column(
                         crossAxisAlignment: CrossAxisAlignment.start,
                         children: [
                            Text(
                              order['client_name'],
                              style: TextStyle(color: theme.textTheme.bodyLarge?.color, fontWeight: FontWeight.bold, fontSize: 15),
                            ),
                            const SizedBox(height: 2),
                            Row(
                              children: [
                                RatingStars(rating: (order['client_rating'] ?? 0.0).toDouble(), size: 12),
                                const SizedBox(width: 4),
                                Text(
                                  '(${order['client_reviews_count']})',
                                  style: TextStyle(color: theme.hintColor, fontSize: 11),
                                ),
                              ],
                            ),
                         ],
                       ),
                     ),
                   ),
                   Icon(Icons.chevron_right_rounded, color: theme.hintColor, size: 20),
                ],
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                if (order['price'] != null) ...[
                  Text(
                    '${order['price'].toStringAsFixed(0)} ${AppStrings.sum}',
                    style: TextStyle(color: theme.textTheme.titleLarge?.color, fontSize: 18, fontWeight: FontWeight.w700),
                  ),
                  const Spacer(),
                ],
                SizedBox(
                  width: 140,
                  height: 48,
                  child: GradientButton(
                    text: AppStrings.isRu ? 'Принять' : 'Qabul qilish',
                    onPressed: () => _acceptOrder(order['id']),
                  ),
                ),
              ],
            ),
          ],
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
