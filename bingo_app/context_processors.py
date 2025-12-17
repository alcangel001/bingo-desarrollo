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
    from .models import Franchise
    
    franchise = None
    is_franchise_owner = False
    
    # 1. PRIMERO: Intentar obtener del middleware (detectada por dominio o usuario)
    franchise = getattr(request, 'franchise', None)
    
    # 2. SEGUNDO: Si no hay del middleware, intentar obtener de la sesión (después de logout)
    if not franchise:
        franchise_id = request.session.get('franchise_id')
        if franchise_id:
            try:
                franchise = Franchise.objects.get(id=franchise_id, is_active=True)
            except Franchise.DoesNotExist:
                # Si la franquicia ya no existe, limpiar sesión
                request.session.pop('franchise_id', None)
    
    # 3. TERCERO: Si hay usuario autenticado, verificar si es propietario
    if request.user.is_authenticated:
        try:
            # Verificar si el usuario es propietario de una franquicia
            try:
                # Buscar directamente si el usuario es owner de alguna franquicia
                owned_franchise = Franchise.objects.filter(owner=request.user).first()
                if owned_franchise:
                    franchise = owned_franchise
                    is_franchise_owner = True
                    # Guardar en sesión para mantenerla después de logout
                    request.session['franchise_id'] = owned_franchise.id
            except Exception:
                pass
            
            # Si no es propietario, verificar si pertenece a una franquicia
            if not is_franchise_owner:
                try:
                    # Refrescar el usuario desde la base de datos para obtener relaciones
                    user = request.user.__class__.objects.select_related('franchise', 'owned_franchise').get(pk=request.user.pk)
                    if hasattr(user, 'owned_franchise') and user.owned_franchise:
                        franchise = user.owned_franchise
                        is_franchise_owner = True
                        request.session['franchise_id'] = user.owned_franchise.id
                    elif hasattr(user, 'franchise') and user.franchise:
                        franchise = user.franchise
                        request.session['franchise_id'] = user.franchise.id
                except Exception:
                    pass
            
            # Si aún no tenemos franquicia, usar la del middleware o sesión
            if not franchise:
                franchise = getattr(request, 'franchise', None)
                if franchise:
                    request.session['franchise_id'] = franchise.id
        except Exception:
            # Si hay algún error, intentar obtener del middleware o sesión
            if not franchise:
                franchise = getattr(request, 'franchise', None)
            # Intentar verificar si es propietario de forma simple
            try:
                if request.user.is_authenticated:
                    owned = Franchise.objects.filter(owner=request.user).exists()
                    if owned:
                        is_franchise_owner = True
            except Exception:
                pass
    
    return {
        'current_franchise': franchise,
        'is_franchise_owner': is_franchise_owner,
    }