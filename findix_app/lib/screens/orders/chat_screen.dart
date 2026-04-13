import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import '../../services/socket_service.dart';
import '../../config/theme.dart';
import '../../config/api_config.dart';
import '../../widgets/full_screen_image.dart';
import 'chat_screen.dart';
import '../master_detail_screen.dart';
import '../client_profile_screen.dart';
import 'package:intl/intl.dart';

class ChatScreen extends StatefulWidget {
  final Map<String, dynamic> order;
  final ApiService apiService;
  final int currentUserId;

  const ChatScreen({
    super.key,
    required this.order,
    required this.apiService,
    required this.currentUserId,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _textController = TextEditingController();
  final List<dynamic> _messages = [];
  bool _isLoading = true;
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _loadHistory();
    _markRead();
    // Listen to real-time events that hit our background listener
    SocketService().messageStream.listen((data) {
      if (!mounted) return;
      if (data['type'] == 'chat_message' && data['order_id'] == widget.order['id']) {
        setState(() {
          _messages.add(data);
        });
        _scrollToBottom();
        _markRead();
      }
    });
  }

  void _markRead() {
    widget.apiService.markAsRead(widget.order['id']).catchError((e) {
      print("Error marking as read: $e");
    });
  }

  Future<void> _loadHistory() async {
    try {
      final history = await widget.apiService.getChatHistory(widget.order['id']);
      if (mounted) {
        setState(() {
          _messages.clear();
          _messages.addAll(history);
          _isLoading = false;
        });
        _scrollToBottom();
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

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty) return;

    // Optimistically add to UI? Better wait for API to get correct ID.
    _textController.clear();

    try {
      final msg = await widget.apiService.sendChatMessage(widget.order['id'], text);
      setState(() {
        _messages.add(msg);
      });
      _scrollToBottom();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isClient = widget.order['client_id'] != null && widget.currentUserId == widget.order['client_id'];
    String? otherName = widget.order['other_name'];
    String? otherAvatar = widget.order['other_avatar'];

    if (otherName == null) {
      otherName = isClient ? widget.order['master_name'] : widget.order['client_name'];
    }
    if (otherAvatar == null) {
      otherAvatar = isClient ? widget.order['master_avatar'] : widget.order['client_avatar'];
    }

    final hasAvatar = otherAvatar != null && otherAvatar.toString().isNotEmpty;
    final avatarUrl = hasAvatar 
        ? (otherAvatar.toString().startsWith('http') 
            ? otherAvatar.toString() 
            : '${ApiConfig.baseUrl}${otherAvatar}')
        : null;

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 0,
        title: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: () {
            final otherRole = widget.order['other_user_role'];
            final otherMasterId = widget.order['other_master_id'];
            final otherUserId = widget.order['other_user_id'];

            if (otherRole == 'master' && otherMasterId != null) {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => MasterDetailScreen(
                    apiService: widget.apiService, 
                    masterId: otherMasterId
                  )
                )
              );
            } else if (otherUserId != null) {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ClientProfileScreen(
                    clientId: otherUserId, 
                    apiService: widget.apiService
                  )
                )
              );
            }
          },
          child: Row(
            children: [
              GestureDetector(
                onTap: () {
                  if (avatarUrl != null) {
                    Navigator.push(context, MaterialPageRoute(builder: (_) => FullScreenImage(imageUrl: avatarUrl, tag: 'chat_avatar_${widget.order['id']}')));
                  }
                },
                child: Hero(
                  tag: 'chat_avatar_${widget.order['id']}',
                  child: CircleAvatar(
                    radius: 18,
                    backgroundColor: AppColors.primary.withOpacity(0.1),
                    backgroundImage: avatarUrl != null ? NetworkImage(avatarUrl) : null,
                    child: avatarUrl == null 
                        ? Text(
                            (otherName ?? '?')[0].toUpperCase(), 
                            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.primary)
                          ) 
                        : null,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(otherName ?? 'Чат', style: const TextStyle(fontSize: 16)),
                    Text(
                      'Заказ #${widget.order['id']}',
                      style: TextStyle(fontSize: 11, color: theme.hintColor, fontWeight: FontWeight.normal),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: BoxDecoration(gradient: AppTheme.currentGradient(context)),
        child: Column(
          children: [
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.all(16),
                      itemCount: _messages.length,
                      itemBuilder: (context, index) {
                        final msg = _messages[index];
                        final isMe = msg['sender_id'] == widget.currentUserId;
                        return _buildMessageBubble(msg, isMe, theme);
                      },
                    ),
            ),
            _buildMessageInput(theme),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(dynamic msg, bool isMe, ThemeData theme) {
    DateTime time;
    try {
      time = DateTime.parse(msg['created_at']).toLocal();
    } catch (_) {
      time = DateTime.now();
    }
    final timeStr = DateFormat('HH:mm').format(time);

    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12, left: 16, right: 16),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: isMe ? AppColors.primary : theme.cardTheme.color,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isMe ? 16 : 0),
            bottomRight: Radius.circular(isMe ? 0 : 16),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 5,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            Text(
              msg['text'] ?? '',
              style: TextStyle(
                color: isMe ? Colors.white : theme.textTheme.bodyLarge?.color,
                fontSize: 15,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              timeStr,
              style: TextStyle(
                color: isMe ? Colors.white70 : theme.hintColor,
                fontSize: 10,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageInput(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.cardTheme.color,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _textController,
                style: TextStyle(color: theme.textTheme.bodyLarge?.color),
                decoration: InputDecoration(
                  hintText: 'Сообщение...',
                  hintStyle: TextStyle(color: theme.hintColor),
                  filled: true,
                  fillColor: theme.cardTheme.color,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                ),
                textCapitalization: TextCapitalization.sentences,
                maxLines: 3,
                minLines: 1,
              ),
            ),
            const SizedBox(width: 12),
            GestureDetector(
              onTap: _sendMessage,
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.send_rounded, color: Colors.white, size: 20),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
