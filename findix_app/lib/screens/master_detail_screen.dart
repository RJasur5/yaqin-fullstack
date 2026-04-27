import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../config/localization.dart';
import '../config/api_config.dart';
import '../models/master.dart';
import '../services/api_service.dart';
import '../services/theme_service.dart';
import '../widgets/rating_stars.dart';
import '../widgets/gradient_button.dart';
import '../widgets/full_screen_image.dart';
import '../utils/phone_utils.dart';
import '../utils/formatters.dart';

class MasterDetailScreen extends StatefulWidget {
  final ApiService apiService;
  final int masterId;
  const MasterDetailScreen({super.key, required this.apiService, required this.masterId});

  @override
  State<MasterDetailScreen> createState() => _MasterDetailScreenState();
}

class _MasterDetailScreenState extends State<MasterDetailScreen> {
  MasterModel? _master;
  bool _isLoading = true;
  bool _isFavorite = false;

  @override
  void initState() {
    super.initState();
    _loadMaster();
  }

  Future<void> _loadMaster() async {
    try {
      final master = await widget.apiService.getMasterDetail(widget.masterId);
      if (mounted) setState(() { _master = master; _isLoading = false; });
    } catch (e) {
      debugPrint('Error loading master: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _toggleFavorite() async {
    try {
      await widget.apiService.toggleFavorite(widget.masterId);
      setState(() => _isFavorite = !_isFavorite);
    } catch (_) {}
  }

  void _showReviewDialog() {
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
                    await widget.apiService.createReview(widget.masterId, rating, commentController.text);
                    if (mounted) {
                      Navigator.pop(context);
                      _loadMaster();
                    }
                  } catch (_) {}
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showJobApplicationDialog() {
    final theme = Theme.of(context);
    final descController = TextEditingController();
    final phoneController = TextEditingController();
    final _phoneFormatter = PhoneUtils.maskFormatter;
    final cityController = TextEditingController();
    bool isSending = false;

    showModalBottomSheet(
      context: context,
      backgroundColor: theme.cardTheme.color,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModalState) => Padding(
          padding: EdgeInsets.fromLTRB(20, 20, 20, MediaQuery.of(ctx).viewInsets.bottom + 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Drag handle
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
              // Header with icon
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      AppColors.primary.withOpacity(0.1),
                      AppColors.secondary.withOpacity(0.05),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(Icons.work_outline_rounded, color: AppColors.primary, size: 28),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            AppStrings.submitApplication,
                            style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            _master?.userName ?? '',
                            style: const TextStyle(color: AppColors.primary, fontSize: 13, fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              // Description field
              TextField(
                controller: descController,
                maxLines: 4,
                style: theme.textTheme.bodyLarge,
                decoration: InputDecoration(
                  hintText: AppStrings.applicationDescription,
                  labelText: AppStrings.isRu ? 'Описание работы *' : 'Ish tavsifi *',
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
                  prefixIcon: const Icon(Icons.description_rounded),
                ),
              ),
              const SizedBox(height: 14),
              // City field
              TextField(
                controller: cityController,
                style: theme.textTheme.bodyLarge,
                decoration: InputDecoration(
                  hintText: AppStrings.isRu ? 'Город' : 'Shahar',
                  labelText: AppStrings.city,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
                  prefixIcon: const Icon(Icons.location_on_rounded),
                ),
              ),
              const SizedBox(height: 14),
              // Phone field
              TextField(
                controller: phoneController,
                keyboardType: TextInputType.phone,
                inputFormatters: [_phoneFormatter],
                style: theme.textTheme.bodyLarge,
                decoration: InputDecoration(
                  hintText: '+998 (99) 858-56-88',
                  labelText: AppStrings.applicationPhone,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
                  prefixIcon: const Icon(Icons.phone_rounded),
                ),
              ),
              const SizedBox(height: 24),
              // Submit button
              GradientButton(
                text: isSending
                    ? (AppStrings.isRu ? 'Отправка...' : 'Yuborilmoqda...')
                    : AppStrings.submitApplication,
                icon: Icons.send_rounded,
                onPressed: isSending ? null : () async {
                  if (descController.text.trim().length < 5) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(AppStrings.isRu
                          ? 'Опишите работу (минимум 5 символов)'
                          : 'Ishni tavsiflang (kamida 5 belgi)')),
                    );
                    return;
                  }
                  setModalState(() => isSending = true);
                  try {
                    await widget.apiService.createJobApplication(
                      widget.masterId,
                      description: descController.text.trim(),
                      city: cityController.text.trim().isNotEmpty ? cityController.text.trim() : null,
                      phone: phoneController.text.trim().isNotEmpty ? phoneController.text.trim() : null,
                    );
                    if (mounted) {
                      Navigator.pop(ctx);
                      _showApplicationSentSuccess();
                    }
                  } catch (e) {
                    setModalState(() => isSending = false);
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
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

  void _showApplicationSentSuccess() {
    final theme = Theme.of(context);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: theme.cardTheme.color,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.success.withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Icon(Icons.check_circle_rounded, color: AppColors.success, size: 64),
            ),
            const SizedBox(height: 20),
            Text(
              AppStrings.applicationSent,
              style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              AppStrings.isRu
                  ? 'Мастер получит уведомление о вашей заявке и свяжется с вами.'
                  : "Usta sizning arizangiz haqida bildirishnoma oladi va siz bilan bog'lanadi.",
              style: theme.textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
          ],
        ),
        actions: [
          Center(
            child: TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text(
                'OK',
                style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final palette = AppTheme.getPalette(ThemeService().currentMode);

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: BoxDecoration(gradient: palette.bgGradient),
        child: _isLoading
            ? Center(child: CircularProgressIndicator(color: theme.primaryColor))
            : _master == null
                ? Center(child: Text(AppStrings.error, style: theme.textTheme.bodyMedium))
                : CustomScrollView(
                    slivers: [
                      // App bar with gradient header
                      SliverAppBar(
                        expandedHeight: 240,
                        pinned: true,
                        backgroundColor: palette.primary,
                        leading: IconButton(
                          icon: Container(
                            padding: const EdgeInsets.all(6),
                            decoration: BoxDecoration(
                              color: Colors.black.withOpacity(0.25),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: const Icon(Icons.arrow_back_rounded, color: Colors.white),
                          ),
                          onPressed: () => Navigator.pop(context),
                        ),
                        actions: [
                          IconButton(
                            icon: Container(
                              padding: const EdgeInsets.all(6),
                              decoration: BoxDecoration(
                                color: Colors.black.withOpacity(0.25),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Icon(
                                _isFavorite ? Icons.favorite_rounded : Icons.favorite_border_rounded,
                                color: _isFavorite ? Colors.red.shade300 : Colors.white,
                              ),
                            ),
                            onPressed: _toggleFavorite,
                          ),
                        ],
                        flexibleSpace: FlexibleSpaceBar(
                          background: Container(
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  palette.primary.withOpacity(0.95),
                                  palette.primaryDark.withOpacity(0.8),
                                  palette.bg,
                                ],
                                begin: Alignment.topCenter,
                                end: Alignment.bottomCenter,
                              ),
                            ),
                            child: Center(
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const SizedBox(height: 40),
                                  GestureDetector(
                                    onTap: () {
                                      final avatar = _master!.userAvatar;
                                      if (avatar != null) {
                                        final url = avatar.startsWith('http')
                                            ? avatar
                                            : '${ApiConfig.baseUrl.replaceAll("/api", "")}$avatar';
                                        Navigator.push(context, MaterialPageRoute(builder: (_) => FullScreenImage(imageUrl: url, tag: 'master_avatar_${_master!.id}')));
                                      }
                                    },
                                    child: Hero(
                                      tag: 'master_avatar_${_master!.id}',
                                      child: Container(
                                        width: 90,
                                        height: 90,
                                        decoration: BoxDecoration(
                                          color: Colors.white.withOpacity(0.2),
                                          borderRadius: BorderRadius.circular(28),
                                          border: Border.all(color: Colors.white.withOpacity(0.4), width: 2),
                                          image: _master!.userAvatar != null
                                              ? DecorationImage(
                                                  image: NetworkImage(
                                                    _master!.userAvatar!.startsWith('http')
                                                        ? _master!.userAvatar!
                                                        : '${ApiConfig.baseUrl.replaceAll("/api", "")}${_master!.userAvatar}',
                                                  ),
                                                  fit: BoxFit.cover,
                                                )
                                              : null,
                                        ),
                                        child: _master!.userAvatar == null
                                          ? Center(
                                              child: Text(
                                                _master!.initials,
                                                style: const TextStyle(
                                                  fontSize: 34,
                                                  fontWeight: FontWeight.w900,
                                                  color: Colors.white,
                                                ),
                                              ),
                                            )
                                          : null,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(height: 12),
                                  Text(
                                    _master!.userName,
                                    style: const TextStyle(
                                      fontSize: 22,
                                      fontWeight: FontWeight.w800,
                                      color: Colors.white,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    _master!.subcategoryName(AppStrings.lang),
                                    style: TextStyle(
                                      fontSize: 14,
                                      color: Colors.white.withOpacity(0.8),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),

                      // Content
                      SliverToBoxAdapter(
                        child: Padding(
                          padding: const EdgeInsets.all(20),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Stats row
                              Row(
                                children: [
                                  _statCard(Icons.star_rounded, _master!.rating.toStringAsFixed(1), AppStrings.rating, AppColors.warning),
                                  const SizedBox(width: 12),
                                  _statCard(Icons.work_rounded, '${_master!.experienceYears}', AppStrings.experience, AppColors.blue),
                                  const SizedBox(width: 12),
                                  _statCard(Icons.chat_rounded, '${_master!.reviewsCount}', AppStrings.reviews, AppColors.success),
                                ],
                              ),
                              const SizedBox(height: 24),

                              // Availability badge
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                                decoration: BoxDecoration(
                                  color: (_master!.isAvailable ? AppColors.success : AppColors.error).withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: (_master!.isAvailable ? AppColors.success : AppColors.error).withOpacity(0.3),
                                  ),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(
                                      _master!.isAvailable ? Icons.check_circle_rounded : Icons.cancel_rounded,
                                      size: 18,
                                      color: _master!.isAvailable ? AppColors.success : AppColors.error,
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      _master!.isAvailable ? AppStrings.available : AppStrings.unavailable,
                                      style: TextStyle(
                                        color: _master!.isAvailable ? AppColors.success : AppColors.error,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(height: 20),

                              // Description
                              if (_master!.description != null) ...[
                                Text(AppStrings.description, style: theme.textTheme.titleMedium),
                                const SizedBox(height: 8),
                                Text(
                                  _master!.description!,
                                  style: theme.textTheme.bodyMedium?.copyWith(height: 1.6),
                                ),
                                const SizedBox(height: 20),
                              ],

                              // Info rows
                              if (_master!.city != null)
                                _infoRow(Icons.location_on_rounded, '${AppStrings.city}: ${_master!.city!}'),
                              if (_master!.hourlyRate != null)
                                _infoRow(Icons.payments_rounded, '${AppStrings.hourlyRate}: ${PriceFormatter.format(_master!.hourlyRate)} ${AppStrings.sum}'),
                              _infoRow(Icons.category_rounded, '${_master!.categoryName(AppStrings.lang)} → ${_master!.subcategoryName(AppStrings.lang)}'),

                              // Skills
                              if (_master!.skills.isNotEmpty) ...[
                                const SizedBox(height: 20),
                                Text(AppStrings.skills, style: theme.textTheme.titleMedium),
                                const SizedBox(height: 8),
                                Wrap(
                                  spacing: 8,
                                  runSpacing: 8,
                                  children: _master!.skills.map((s) => Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                    decoration: BoxDecoration(
                                      color: theme.primaryColor.withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(10),
                                      border: Border.all(color: theme.primaryColor.withOpacity(0.3)),
                                    ),
                                    child: Text(s, style: TextStyle(color: theme.primaryColor, fontSize: 13, fontWeight: FontWeight.w600)),
                                  )).toList(),
                                ),
                              ],

                              // Reviews
                              const SizedBox(height: 24),
                              Row(
                                children: [
                                  Text(AppStrings.reviews, style: theme.textTheme.titleMedium),
                                  const SizedBox(width: 8),
                                  Text('(${_master!.reviewsCount})', style: theme.textTheme.bodySmall),
                                ],
                              ),
                              const SizedBox(height: 12),

                              if (_master!.reviews == null || _master!.reviews!.isEmpty)
                                Text(AppStrings.noReviews, style: theme.textTheme.bodySmall)
                              else
                                ..._master!.reviews!.map((r) => Container(
                                  margin: const EdgeInsets.only(bottom: 12),
                                  padding: const EdgeInsets.all(14),
                                  decoration: BoxDecoration(
                                    color: theme.cardTheme.color,
                                    borderRadius: BorderRadius.circular(14),
                                    border: Border.all(color: theme.dividerColor.withOpacity(0.5)),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        children: [
                                          Text(r.clientName, style: theme.textTheme.bodyLarge),
                                          const Spacer(),
                                          RatingStars(rating: r.rating.toDouble(), size: 14, showNumber: false),
                                        ],
                                      ),
                                      if (r.comment != null && r.comment!.isNotEmpty) ...[
                                        const SizedBox(height: 8),
                                        Text(r.comment!, style: theme.textTheme.bodyMedium?.copyWith(height: 1.4)),
                                      ],
                                    ],
                                  ),
                                )),

                              const SizedBox(height: 100),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
      ),
      bottomNavigationBar: _master != null
          ? Container(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
              decoration: BoxDecoration(
                color: theme.cardTheme.color,
                border: Border(top: BorderSide(color: theme.dividerColor.withOpacity(0.5))),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: GradientButton(
                      text: AppStrings.submitApplication,
                      icon: Icons.work_outline_rounded,
                      onPressed: _showJobApplicationDialog,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      color: theme.primaryColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: theme.primaryColor.withOpacity(0.3)),
                    ),
                    child: IconButton(
                      icon: Icon(Icons.rate_review_rounded, color: theme.primaryColor),
                      onPressed: _showReviewDialog,
                    ),
                  ),
                ],
              ),
            )
          : null,
    );
  }

  Widget _statCard(IconData icon, String value, String label, Color color) {
    final theme = Theme.of(context);
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: theme.cardTheme.color,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: theme.dividerColor.withOpacity(0.5)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 22),
            const SizedBox(height: 6),
            Text(value, style: theme.textTheme.titleMedium),
            const SizedBox(height: 2),
            Text(label, style: theme.textTheme.bodySmall),
          ],
        ),
      ),
    );
  }

  Widget _infoRow(IconData icon, String text) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Icon(icon, size: 18, color: theme.textTheme.bodySmall?.color),
          const SizedBox(width: 10),
          Expanded(child: Text(text, style: theme.textTheme.bodyMedium)),
        ],
      ),
    );
  }
}
