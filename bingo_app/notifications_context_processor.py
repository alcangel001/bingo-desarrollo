from .models import CreditRequestNotification, WithdrawalRequestNotification, Message
from itertools import chain
from django.utils import timezone

def get_notification_date(notification):
    if hasattr(notification, 'timestamp'):
        return notification.timestamp
    elif hasattr(notification, 'created_at'):
        return notification.created_at
    # Fallback for any object without a date, to avoid crashes
    return timezone.now()

def notifications(request):
    total_unread_notifications_count = 0
    all_unread_notifications = []

    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(recipient=request.user, is_read=False)
        
        admin_credit_reqs = CreditRequestNotification.objects.none()
        admin_withdrawal_reqs = WithdrawalRequestNotification.objects.none()

        if request.user.is_admin:
            admin_credit_reqs = CreditRequestNotification.objects.filter(is_read=False)
            admin_withdrawal_reqs = WithdrawalRequestNotification.objects.filter(is_read=False)

        total_unread_notifications_count = unread_messages.count() + admin_credit_reqs.count() + admin_withdrawal_reqs.count()

        all_notifications_list = sorted(
            chain(unread_messages, admin_credit_reqs, admin_withdrawal_reqs),
            key=get_notification_date,
            reverse=True
        )
        
        all_unread_notifications = all_notifications_list

    win_notification = request.session.pop('show_win_notification', None)

    return {
        'win_notification': win_notification,
        'total_unread_notifications_count': total_unread_notifications_count,
        'all_unread_notifications': all_unread_notifications,
    }