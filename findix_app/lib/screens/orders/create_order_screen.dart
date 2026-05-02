import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../config/localization.dart';
import '../../services/api_service.dart';
import '../../widgets/gradient_button.dart';
import '../../models/category.dart';
import '../../services/auth_service.dart';
import '../../services/theme_service.dart';
import 'package:flutter/services.dart';
import '../../utils/formatters.dart';
import '../../config/regions.dart';

class CreateOrderScreen extends StatefulWidget {
  final ApiService apiService;
  final AuthService authService;
  const CreateOrderScreen({super.key, required this.apiService, required this.authService});

  @override
  State<CreateOrderScreen> createState() => _CreateOrderScreenState();
}

class _CreateOrderScreenState extends State<CreateOrderScreen> {
  final _descController = TextEditingController();
  final _priceController = TextEditingController();
  
  bool _isLoading = true;
  bool _isSaving = false;
  String? _error;

  List<CategoryModel> _categories = [];
  int? _selectedCategoryId;
  int? _selectedSubcategoryId;
  bool _includeLunch = false;
  bool _includeTaxi = false;
  bool _isCompany = false;

  String? _selectedCityKey;
  String? _selectedDistrictKey;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final cats = await widget.apiService.getCategories();
      if (mounted) {
        setState(() {
          _categories = cats;
          _selectedCityKey = widget.authService.currentUser?.city != null
              ? RegionsConfig.getKey(widget.authService.currentUser!.city!)
              : null;
          if (_selectedCityKey == null || !RegionsConfig.regionKeys.contains(_selectedCityKey)) {
            _selectedCityKey = RegionsConfig.regionKeys.first;
          }
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Failed to load categories';
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _submit() async {
    if (_selectedSubcategoryId == null) {
      setState(() => _error = AppStrings.isRu ? 'Выберите специализацию' : 'Mutaxassislikni tanlang');
      return;
    }
    if (_descController.text.trim().isEmpty) {
      setState(() => _error = AppStrings.isRu ? 'Опишите задачу' : 'Vazifani tavsiflang');
      return;
    }
    if (_selectedCityKey != null && _selectedDistrictKey == null) {
      setState(() => _error = AppStrings.isRu ? 'Выберите район' : 'Tumanni tanlang');
      return;
    }


    setState(() {
      _isSaving = true;
      _error = null;
    });

    try {
      final rawPrice = _priceController.text.replaceAll(' ', '');
      final cityForApi = _selectedCityKey != null ? RegionsConfig.getDisplayName(_selectedCityKey!) : RegionsConfig.getDisplayName(RegionsConfig.regionKeys.first);
      final districtForApi = _selectedDistrictKey != null ? RegionsConfig.getDistrictDisplay(_selectedDistrictKey!, _selectedCityKey) : null;
      await widget.apiService.createOrder(
        subcategoryId: _selectedSubcategoryId!,
        description: _descController.text.trim(),
        city: cityForApi,
        district: districtForApi,
        price: double.tryParse(rawPrice),
        includeLunch: _includeLunch,
        includeTaxi: _includeTaxi,
        isCompany: _isCompany,
      );
      if (mounted) {
        Navigator.pop(context, true);
      }
    } catch (e) {
      setState(() => _error = e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      decoration: BoxDecoration(gradient: AppTheme.currentGradient(context)),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          title: Text(AppStrings.isRu ? 'Подать объявление' : 'E\'lon berish'),
          backgroundColor: Colors.transparent,
          elevation: 0,
          foregroundColor: theme.textTheme.bodyLarge?.color,
        ),
        body: _isLoading 
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : SingleChildScrollView(
                padding: const EdgeInsets.only(top: 8, left: 20, right: 20, bottom: 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (_error != null) ...[
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppColors.error.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppColors.error.withValues(alpha: 0.3)),
                        ),
                        child: Text(_error!, style: const TextStyle(color: AppColors.error, fontSize: 13)),
                      ),
                      const SizedBox(height: 16),
                    ],

                    Text(
                      AppStrings.isRu ? 'Какая услуга нужна?' : 'Qanday xizmat kerak?',
                      style: TextStyle(color: Theme.of(context).textTheme.titleLarge?.color, fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 12),
                    
                    // Category
                    _dropdownWrapper(
                      child: DropdownButton<int>(
                        isExpanded: true,
                        value: _selectedCategoryId,
                        hint: Text(AppStrings.isRu ? 'Выберите категорию' : 'Kategoriyani tanlang', style: TextStyle(color: Theme.of(context).textTheme.bodySmall?.color)),
                        dropdownColor: Theme.of(context).cardTheme.color,
                        items: _categories.map((c) {
                          return DropdownMenuItem<int>(
                            value: c.id,
                            child: Text(c.name(AppStrings.lang), style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color)),
                          );
                        }).toList(),
                        onChanged: (val) {
                          setState(() {
                            _selectedCategoryId = val;
                            _selectedSubcategoryId = null;
                          });
                        },
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Subcategory
                    if (_selectedCategoryId != null)
                      _dropdownWrapper(
                        child: DropdownButton<int>(
                          isExpanded: true,
                          value: _selectedSubcategoryId,
                          hint: Text(AppStrings.isRu ? 'Специализация' : 'Mutaxassislik', style: TextStyle(color: Theme.of(context).textTheme.bodySmall?.color)),
                          dropdownColor: Theme.of(context).cardTheme.color,
                          items: _categories.firstWhere((c) => c.id == _selectedCategoryId).subcategories.map((sub) {
                            return DropdownMenuItem<int>(
                              value: sub.id,
                              child: Text(sub.name(AppStrings.lang), style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color)),
                            );
                          }).toList(),
                          onChanged: (val) => setState(() => _selectedSubcategoryId = val),
                        ),
                      ),
                    
                    const SizedBox(height: 24),
                    Text(
                      AppStrings.city,
                      style: TextStyle(color: Theme.of(context).textTheme.titleLarge?.color, fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 8),
                    _dropdownWrapper(
                      child: DropdownButton<String>(
                        isExpanded: true,
                        value: _selectedCityKey,
                        hint: Text(AppStrings.isRu ? 'Выберите регион' : 'Viloyatni tanlang', style: TextStyle(color: Theme.of(context).textTheme.bodySmall?.color)),
                        dropdownColor: Theme.of(context).cardTheme.color,
                        items: RegionsConfig.regionKeys.map((key) {
                          return DropdownMenuItem<String>(
                            value: key,
                            child: Text(RegionsConfig.getDisplayName(key), style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color)),
                          );
                        }).toList(),
                        onChanged: (val) {
                          setState(() {
                            _selectedCityKey = val;
                            _selectedDistrictKey = null;
                          });
                        },
                      ),
                    ),

                    const SizedBox(height: 24),
                    if (_selectedCityKey != null && RegionsConfig.getDistricts(_selectedCityKey).isNotEmpty) ...[
                      Text(
                        AppStrings.isRu ? 'Район' : 'Tuman',
                        style: TextStyle(color: Theme.of(context).textTheme.titleLarge?.color, fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 8),
                      _dropdownWrapper(
                        child: DropdownButton<String>(
                          isExpanded: true,
                          value: _selectedDistrictKey,
                          hint: Text(AppStrings.isRu ? 'Выберите район' : 'Tumanni tanlang', style: TextStyle(color: Theme.of(context).textTheme.bodySmall?.color)),
                          dropdownColor: Theme.of(context).cardTheme.color,
                          items: RegionsConfig.getDistricts(_selectedCityKey).map((displayName) {
                            final key = RegionsConfig.getDistrictKey(displayName, _selectedCityKey);
                            return DropdownMenuItem<String>(
                              value: key,
                              child: Text(displayName, style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color)),
                            );
                          }).toList(),
                          onChanged: (val) => setState(() => _selectedDistrictKey = val),
                        ),
                      ),
                    ],

                    const SizedBox(height: 24),
                    Text(
                      AppStrings.isRu ? 'О работе' : 'Ish haqida',
                      style: TextStyle(color: Theme.of(context).textTheme.titleLarge?.color, fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _descController,
                      minLines: 4,
                      maxLines: null,
                      keyboardType: TextInputType.multiline,
                      style: theme.textTheme.bodyLarge,
                      decoration: InputDecoration(
                        hintText: AppStrings.isRu ? 'Расскажите, что нужно сделать...' : 'Nima qilish kerakligini aytib bering...',
                      ),
                    ),

                    const SizedBox(height: 24),
                    Text(
                      AppStrings.isRu ? 'Ожидаемая цена (необязательно)' : 'Kutilayayotgan narx (ixtiyoriy)',
                      style: TextStyle(color: Theme.of(context).textTheme.titleLarge?.color, fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _priceController,
                      keyboardType: TextInputType.number,
                      inputFormatters: [
                        FilteringTextInputFormatter.digitsOnly,
                        ThousandsSeparatorInputFormatter(),
                      ],
                      style: theme.textTheme.bodyLarge,
                      decoration: InputDecoration(
                        suffixText: AppStrings.sum,
                        suffixStyle: theme.textTheme.bodyMedium?.copyWith(color: theme.primaryColor, fontWeight: FontWeight.bold),
                      ),
                    ),

                    const SizedBox(height: 24),
                    _buildOptionToggle(
                      title: AppStrings.includeLunch,
                      subtitle: AppStrings.isRu ? 'Мастеру будет предоставлен обед' : 'Usta tushlik bilan ta\'minlanadi',
                      icon: Icons.restaurant_rounded,
                      value: _includeLunch,
                      onChanged: (v) => setState(() => _includeLunch = v),
                    ),
                    const SizedBox(height: 12),
                    _buildOptionToggle(
                      title: AppStrings.includeTaxi,
                      subtitle: AppStrings.isRu ? 'Расходы на дорогу оплачиваются' : 'Yo\'l harajatlari qoplanadi',
                      icon: Icons.local_taxi_rounded,
                      value: _includeTaxi,
                      onChanged: (v) => setState(() => _includeTaxi = v),
                    ),

                    const SizedBox(height: 12),
                    _buildOptionToggle(
                      title: AppStrings.isRu ? 'Набор персонала (HR)' : 'Xodimlar yollash (HR)',
                      subtitle: AppStrings.isRu ? 'Множество мастеров могут принять' : 'Ko\'plab ustalar qabul qilishi mumkin',
                      icon: Icons.groups_rounded,
                      value: _isCompany,
                      onChanged: (v) => setState(() => _isCompany = v),
                    ),


                    const SizedBox(height: 40),
                    GradientButton(
                      text: AppStrings.isRu ? 'Опубликовать' : 'E\'lonni joylash',
                      isLoading: _isSaving,
                      onPressed: _submit,
                    ),
                    const SizedBox(height: 40),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _dropdownWrapper({required Widget child}) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: theme.cardTheme.color,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: theme.dividerColor.withOpacity(0.5)),
      ),
      child: DropdownButtonHideUnderline(
        child: Theme(
          data: theme.copyWith(
            canvasColor: theme.cardTheme.color,
          ),
          child: child,
        ),
      ),
    );
  }

  Widget _buildOptionToggle({
    required String title,
    String? subtitle,
    required IconData icon,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    final theme = Theme.of(context);
    return Container(
      decoration: BoxDecoration(
        color: theme.cardTheme.color,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: theme.dividerColor.withOpacity(0.1)),
      ),
      child: SwitchListTile(
        secondary: Icon(icon, color: value ? theme.primaryColor : theme.hintColor),
        title: Text(
          title,
          style: TextStyle(
            color: theme.textTheme.bodyLarge?.color,
            fontSize: 14,
            fontWeight: value ? FontWeight.bold : FontWeight.normal,
          ),
        ),
        subtitle: subtitle != null ? Text(subtitle, style: const TextStyle(fontSize: 11, color: AppColors.textHint)) : null,
        value: value,
        onChanged: onChanged,
        activeColor: theme.primaryColor,
      ),
    );
  }


  @override
  void dispose() {
    _descController.dispose();
    _priceController.dispose();
    super.dispose();
  }
}
