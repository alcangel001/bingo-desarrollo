# bingo_app/context_processors.py
from .models import CreditRequestNotification, WithdrawalRequestNotification, Message, Announcement
from itertools import chain
from django.utils import timezone

def get_notification_date(notification):
    if hasattr(notification, 'timestamp'):
        return notification.timestamp
    elif hasattr(notification, 'created_at'):
        return notification.created_at
    return timezone.now()

def notifications_global(request):
    total_unread_notifications_count = 0
    all_unread_notifications = []

    if request.user.is_authenticated:
        # 1. Obtener mensajes para el usuario actual
        unread_messages = Message.objects.filter(recipient=request.user, is_read=False)
        
        admin_credit_reqs = CreditRequestNotification.objects.none()
        admin_withdrawal_reqs = WithdrawalRequestNotification.objects.none()

        # 2. Si es admin u organizador, obtener todas las solicitudes pendientes
        if request.user.is_admin or request.user.is_organizer:
            admin_credit_reqs = CreditRequestNotification.objects.filter(user=request.user, is_read=False)
            admin_withdrawal_reqs = WithdrawalRequestNotification.objects.filter(user=request.user, is_read=False)

        # 3. Calcular el total
        total_unread_notifications_count = unread_messages.count() + admin_credit_reqs.count() + admin_withdrawal_reqs.count()

        # 4. Combinar listas y ordenar
        all_unread_notifications = sorted(
            chain(unread_messages, admin_credit_reqs, admin_withdrawal_reqs),
            key=get_notification_date,
            reverse=True
        )

    return {
        'total_unread_notifications_count': total_unread_notifications_count,
        'all_unread_notifications': all_unread_notifications,
    }

def announcements_processor(request):
    announcements = Announcement.objects.filter(is_active=True).order_by('order', '-created_at')
    return {'global_announcements': announcements}

def system_settings_processor(request):
    """Inyecta configuraciones del sistema en el contexto global"""
    from .models import PercentageSettings, BingoTicketSettings
    
    percentage_settings = PercentageSettings.objects.first()
    ticket_settings = BingoTicketSettings.get_settings()
    
    return {
        'system_settings': {
            'credits_purchase_enabled': percentage_settings.credits_purchase_enabled if percentage_settings else True,
            'credits_withdrawal_enabled': percentage_settings.credits_withdrawal_enabled if percentage_settings else True,
            'referral_system_enabled': percentage_settings.referral_system_enabled if percentage_settings else True,
            'promotions_enabled': percentage_settings.promotions_enabled if percentage_settings else True,
            'ticket_system_enabled': ticket_settings.is_system_active if ticket_settings else False,
            'accounts_receivable_enabled': percentage_settings.accounts_receivable_enabled if percentage_settings else True,
        }
    }

def franchise_processor(request):
    """Inyecta información de la franquicia del usuario en el contexto global"""
    franchise = None
    is_franchise_owner = False
    
    if request.user.is_authenticated:
        # Verificar si el usuario es propietario de una franquicia
        try:
            if hasattr(request.user, 'owned_franchise') and request.user.owned_franchise:
                franchise = request.user.owned_franchise
                is_franchise_owner = True
            # Si no es propietario, verificar si pertenece a una franquicia
            elif hasattr(request.user, 'franchise') and request.user.franchise:
                franchise = request.user.franchise
        except Exception:
            # Si hay algún error, usar la franquicia del middleware
            franchise = getattr(request, 'franchise', None)
    
    return {
        'current_franchise': franchise,
        'is_franchise_owner': is_franchise_owner,
    }