import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../config/api_config.dart';
import '../services/api_service.dart';
import '../../widgets/full_screen_image.dart';
import '../../utils/date_utils.dart';
import 'package:intl/intl.dart';

class ClientProfileScreen extends StatefulWidget {
  final int clientId;
  final ApiService apiService;

  const ClientProfileScreen({
    super.key,
    required this.clientId,
    required this.apiService,
  });

  @override
  State<ClientProfileScreen> createState() => _ClientProfileScreenState();
}

class _ClientProfileScreenState extends State<ClientProfileScreen> {
  Map<String, dynamic>? _client;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final profile = await widget.apiService.getClientProfile(widget.clientId);
      if (mounted) {
        setState(() {
          _client = profile;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка загрузки: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Профиль клиента', style: TextStyle(fontWeight: FontWeight.bold)),
        elevation: 0,
        backgroundColor: Colors.transparent,
      ),
      extendBodyBehindAppBar: true,
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: BoxDecoration(gradient: AppTheme.currentGradient(context)),
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : _client == null
                ? const Center(child: Text('Профиль не найден'))
                : _buildContent(theme),
      ),
    );
  }

  Widget _buildContent(ThemeData theme) {
    final avatar = _client!['avatar'];
    final avatarUrl = avatar != null 
        ? (avatar.toString().startsWith('http') ? avatar : '${ApiConfig.baseUrl}$avatar')
        : null;

    final createdAt = DateTimeUtils.parseUtc(_client!['created_at']);
    final joinDate = DateTimeUtils.formatMonthYear(createdAt, 'ru');

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 100, 20, 20),
      child: Column(
        children: [
          // Header Card
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: theme.cardTheme.color,
              borderRadius: BorderRadius.circular(30),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Column(
              children: [
                GestureDetector(
                  onTap: () {
                    if (avatarUrl != null) {
                      Navigator.push(context, MaterialPageRoute(builder: (_) => FullScreenImage(imageUrl: avatarUrl, tag: 'profile_avatar_${widget.clientId}')));
                    }
                  },
                  child: Hero(
                    tag: 'profile_avatar_${widget.clientId}',
                    child: CircleAvatar(
                      radius: 50,
                      backgroundColor: theme.primaryColor.withOpacity(0.1),
                      backgroundImage: avatarUrl != null ? NetworkImage(avatarUrl) : null,
                      child: avatarUrl == null 
                          ? Text(_client!['name'][0].toUpperCase(), style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: theme.primaryColor))
                          : null,
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  _client!['name'],
                  style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.location_on_rounded, size: 16, color: theme.primaryColor),
                    const SizedBox(width: 4),
                    Text(_client!['city'] ?? 'Город не указан', style: TextStyle(color: theme.hintColor)),
                  ],
                ),
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    _buildStatCol('Рейтинг', '⭐ ${_client!['client_rating']?.toStringAsFixed(1) ?? '0.0'}', theme),
                    Container(width: 1, height: 30, color: theme.dividerColor.withOpacity(0.2)),
                    _buildStatCol('Отзывы', '${_client!['client_reviews_count'] ?? 0}', theme),
                  ],
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 24),
          
          // Details
          _buildInfoRow(Icons.calendar_today_rounded, 'На Yaqin с', joinDate, theme),
          if (_client!['phone'] != null)
            _buildInfoRow(Icons.phone_rounded, 'Телефон', _client!['phone'], theme),

          const SizedBox(height: 32),
          
          // Reviews
          const Align(
            alignment: Alignment.centerLeft,
            child: Text(
              'Отзывы мастеров',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 16),
          _buildReviewsList(theme),
        ],
      ),
    );
  }

  Widget _buildStatCol(String label, String value, ThemeData theme) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: theme.primaryColor)),
        const SizedBox(height: 4),
        Text(label, style: TextStyle(fontSize: 12, color: theme.hintColor)),
      ],
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value, ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        children: [
          Icon(icon, size: 20, color: theme.hintColor),
          const SizedBox(width: 12),
          Text(label, style: TextStyle(color: theme.hintColor)),
          const Spacer(),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildReviewsList(ThemeData theme) {
    final List<dynamic> reviews = _client!['reviews'] ?? [];
    if (reviews.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(24),
        width: double.infinity,
        decoration: BoxDecoration(
          color: theme.cardTheme.color?.withOpacity(0.5),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          children: [
            Icon(Icons.rate_review_outlined, size: 48, color: theme.hintColor.withOpacity(0.5)),
            const SizedBox(height: 12),
            Text('У этого клиента пока нет отзывов', style: TextStyle(color: theme.hintColor)),
          ],
        ),
      );
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: reviews.length,
      itemBuilder: (context, index) {
        final r = reviews[index];
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: theme.cardTheme.color,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text('⭐ ${r['rating']}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.orange)),
                  const Spacer(),
                  Text(
                    DateTimeUtils.formatDate(DateTimeUtils.parseUtc(r['created_at'])),
                    style: TextStyle(fontSize: 12, color: theme.hintColor),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(r['comment'] ?? 'Без комментария', style: const TextStyle(fontSize: 14)),
              const SizedBox(height: 8),
              Row(
                children: [
                  Text('Мастер: ', style: TextStyle(fontSize: 12, color: theme.hintColor)),
                  Text(r['master_name'] ?? 'Аноним', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
