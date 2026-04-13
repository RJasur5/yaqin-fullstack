import 'master.dart';

class UserModel {
  final int id;
  final String name;
  final String phone;
  final String role;
  final String? avatar;
  final String? city;
  final String lang;
  final double clientRating;
  final int clientReviewsCount;
  final bool isBlocked;
  final MasterModel? masterProfile;
  final List<Map<String, dynamic>>? reviewStats;

  UserModel({
    required this.id,
    required this.name,
    required this.phone,
    required this.role,
    this.avatar,
    this.city,
    this.lang = 'ru',
    this.clientRating = 0.0,
    this.clientReviewsCount = 0,
    this.isBlocked = false,
    this.masterProfile,
    this.reviewStats,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      name: json['name'] ?? '',
      phone: json['phone'] ?? '',
      role: json['role'] ?? 'client',
      avatar: json['avatar'],
      city: json['city'],
      lang: json['lang'] ?? 'ru',
      clientRating: (json['client_rating'] ?? 0.0).toDouble(),
      clientReviewsCount: json['client_reviews_count'] ?? 0,
      isBlocked: json['is_blocked'] ?? false,
      masterProfile: json['master_profile'] != null ? MasterModel.fromJson(json['master_profile']) : null,
      reviewStats: json['review_stats'] != null ? List<Map<String, dynamic>>.from(json['review_stats']) : null,
    );
  }

  bool get isMaster => role == 'master' || role == 'admin';
  bool get isAdmin => role == 'admin';
}

class ClientReviewModel {
  final int id;
  final int clientId;
  final int masterId;
  final String masterName;
  final String? masterAvatar;
  final int rating;
  final String? comment;
  final String? createdAt;

  ClientReviewModel({
    required this.id,
    required this.clientId,
    required this.masterId,
    required this.masterName,
    this.masterAvatar,
    required this.rating,
    this.comment,
    this.createdAt,
  });

  factory ClientReviewModel.fromJson(Map<String, dynamic> json) {
    return ClientReviewModel(
      id: json['id'],
      clientId: json['client_id'],
      masterId: json['master_id'],
      masterName: json['master_name'] ?? '',
      masterAvatar: json['master_avatar'],
      rating: json['rating'] ?? 0,
      comment: json['comment'],
      createdAt: json['created_at'],
    );
  }
}
