import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../config/localization.dart';
import '../models/category.dart';
import '../models/master.dart';
import '../services/api_service.dart';
import '../services/theme_service.dart';
import '../widgets/master_card.dart';
import 'master_detail_screen.dart';
import '../config/regions.dart';

class MastersListScreen extends StatefulWidget {
  final ApiService apiService;
  final List<CategoryModel> categories;
  final int? initialCategoryId;

  const MastersListScreen({
    super.key,
    required this.apiService,
    this.categories = const [],
    this.initialCategoryId,
  });

  @override
  State<MastersListScreen> createState() => _MastersListScreenState();
}

class _MastersListScreenState extends State<MastersListScreen> {
  List<MasterModel> _masters = [];
  bool _isLoading = true;
  int? _selectedCategoryId;
  int? _selectedSubcategoryId;
  String _searchQuery = '';
  String _sortBy = 'rating';
  String? _selectedCity;
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _selectedCategoryId = widget.initialCategoryId;
    _loadMasters();
  }

  Future<void> _loadMasters() async {
    setState(() => _isLoading = true);
    try {
      final masters = await widget.apiService.getMasters(
        categoryId: _selectedCategoryId,
        subcategoryId: _selectedSubcategoryId,
        city: _selectedCity,
        search: _searchQuery.isNotEmpty ? _searchQuery : null,
        sortBy: _sortBy,
      );
      if (mounted) {
        setState(() {
          _masters = masters;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  CategoryModel? get _selectedCategory {
    if (_selectedCategoryId == null) return null;
    try {
      return widget.categories.firstWhere((c) => c.id == _selectedCategoryId);
    } catch (_) {
      return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    final canPop = Navigator.of(context).canPop();
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: canPop ? AppBar(
        title: Text(AppStrings.isRu ? 'Категории' : 'Kategoriyalar'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: theme.textTheme.bodyLarge?.color,
      ) : null,
      body: Container(
        decoration: BoxDecoration(gradient: AppTheme.currentGradient(context)),
        child: SafeArea(
          child: Column(
            children: [
              // Search bar
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 10, 20, 16),
                child: TextField(
                  controller: _searchController,
                  style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color),
                  onChanged: (val) {
                    setState(() => _searchQuery = val);
                    _loadMasters();
                  },
                  decoration: InputDecoration(
                    hintText: AppStrings.searchHint,
                    prefixIcon: const Icon(Icons.search_rounded, color: AppColors.textHint),
                    suffixIcon: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (_searchQuery.isNotEmpty)
                          IconButton(
                            icon: const Icon(Icons.clear_rounded, color: AppColors.textHint),
                            onPressed: () {
                              _searchController.clear();
                              setState(() => _searchQuery = '');
                              _loadMasters();
                            },
                          ),
                        IconButton(
                          icon: const Icon(Icons.tune_rounded, color: AppColors.primary),
                          onPressed: _showSortDialog,
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              // City Filter
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: DropdownButtonFormField<String>(
                    value: _selectedCity,
                    dropdownColor: theme.cardTheme.color,
                    decoration: InputDecoration(
                      hintText: AppStrings.isRu ? 'Все города' : 'Barcha shaharlar',
                      prefixIcon: Icon(Icons.location_on_rounded, color: theme.textTheme.bodySmall?.color),
                      filled: true,
                      fillColor: theme.cardTheme.color,
                    ),
                    icon: Icon(Icons.arrow_drop_down_rounded, color: theme.textTheme.bodySmall?.color),
                    items: [
                      DropdownMenuItem<String>(
                        value: null, 
                        child: Text(AppStrings.isRu ? 'Все города' : 'Barcha shaharlar', style: theme.textTheme.bodyLarge)
                      ),
                      ...RegionsConfig.regionKeys.map((key) => DropdownMenuItem<String>(
                        value: RegionsConfig.getDisplayName(key), 
                        child: Text(RegionsConfig.getDisplayName(key), style: theme.textTheme.bodyLarge)
                      )),
                    ],
                    onChanged: (val) {
                      setState(() {
                        _selectedCity = val;
                      });
                      _loadMasters();
                    },
                  ),
              ),

              // Category Ribbon (Chips)
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
                            _loadMasters();
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
                          _loadMasters();
                        },
                      );
                    },
                  ),
                ),

              // Subcategory Ribbon
              if (_selectedCategory != null && _selectedCategory!.subcategories.isNotEmpty) ...[
                const SizedBox(height: 12),
                SizedBox(
                  height: 36,
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    scrollDirection: Axis.horizontal,
                    itemCount: _selectedCategory!.subcategories.length + 1,
                    itemBuilder: (context, index) {
                      if (index == 0) {
                        return _buildSmallChip(
                          label: AppStrings.isRu ? 'Все специальности' : 'Barcha mutaxassisliklar',
                          selected: _selectedSubcategoryId == null,
                          onTap: () {
                            setState(() => _selectedSubcategoryId = null);
                            _loadMasters();
                          },
                        );
                      }
                      final sub = _selectedCategory!.subcategories[index - 1];
                      return _buildSmallChip(
                        label: sub.name(AppStrings.lang),
                        selected: _selectedSubcategoryId == sub.id,
                        onTap: () {
                          setState(() => _selectedSubcategoryId = sub.id);
                          _loadMasters();
                        },
                      );
                    },
                  ),
                ),
              ],

              const SizedBox(height: 8),

              // Masters list
              Expanded(
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
                    : _masters.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.search_off_rounded, size: 64, color: AppColors.textHint),
                                const SizedBox(height: 16),
                                Text(
                                  AppStrings.isRu ? 'Мастера не найдены' : "Ustalar topilmadi",
                                  style: TextStyle(color: Theme.of(context).textTheme.bodyMedium?.color, fontSize: 16),
                                ),
                              ],
                            ),
                          )
                        : RefreshIndicator(
                            onRefresh: _loadMasters,
                            color: AppColors.primary,
                            child: ListView.builder(
                              padding: const EdgeInsets.symmetric(horizontal: 20),
                              itemCount: _masters.length,
                              itemBuilder: (context, index) {
                                return MasterCard(
                                  master: _masters[index],
                                  onTap: () {
                                    Navigator.push(
                                      context,
                                      MaterialPageRoute(
                                        builder: (_) => MasterDetailScreen(
                                          apiService: widget.apiService,
                                          masterId: _masters[index].id,
                                        ),
                                      ),
                                    );
                                  },
                                );
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



  void _showSortDialog() {
    final theme = Theme.of(context);
    showModalBottomSheet(
      context: context,
      backgroundColor: theme.cardTheme.color,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
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
            const SizedBox(height: 24),
            Text(
              AppStrings.sortBy, 
              style: theme.textTheme.titleMedium,
            ),
            const SizedBox(height: 20),
            _sortTile('rating', AppStrings.byRating, Icons.star_rounded),
            _sortTile('experience', AppStrings.byExperience, Icons.work_history_rounded),
            _sortTile('price', AppStrings.byPrice, Icons.attach_money_rounded),
            const SizedBox(height: 16),
          ],
        ),
      ),
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
        labelStyle: theme.textTheme.labelSmall?.copyWith(
          color: selected ? Colors.white : theme.textTheme.bodyMedium?.color,
          fontWeight: selected ? FontWeight.bold : FontWeight.w600,
          fontSize: 13,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
          side: BorderSide(
            color: selected ? theme.primaryColor : theme.dividerColor.withOpacity(0.1),
            width: 1,
          ),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
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
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: selected ? theme.primaryColor.withValues(alpha: 0.2) : Colors.transparent,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: selected ? theme.primaryColor : theme.dividerColor.withOpacity(0.1)),
          ),
          child: Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: selected ? theme.primaryColor : theme.textTheme.bodyMedium?.color,
              fontWeight: selected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ),
      ),
    );
  }

  Widget _sortTile(String value, String label, IconData icon) {
    final theme = Theme.of(context);
    final selected = _sortBy == value;
    return ListTile(
      leading: Icon(icon, color: selected ? theme.primaryColor : theme.textTheme.bodySmall?.color),
      title: Text(label, style: TextStyle(color: selected ? theme.primaryColor : theme.textTheme.bodyMedium?.color)),
      trailing: selected ? Icon(Icons.check_rounded, color: theme.primaryColor) : null,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      onTap: () {
        setState(() => _sortBy = value);
        Navigator.pop(context);
        _loadMasters();
      },
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }
}
