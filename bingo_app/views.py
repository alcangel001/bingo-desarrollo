from asyncio.log import logger
import sentry_sdk
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from .error_monitor import get_facebook_error_summary, reset_facebook_error_counters, facebook_monitor
from allauth.socialaccount.models import SocialAccount
import secrets
import json
import uuid
import random

from django.core.management import call_command
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum, Q, Count, Avg, F
from django.db.models.functions import TruncDay
from django.db import transaction
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .flash_messages import add_flash_message
from django.template.loader import render_to_string
from django.conf import settings
from agora_token_builder import RtcTokenBuilder
import time


from .forms import (
    PercentageSettingsForm, RegistrationForm, GameForm, GameEditForm, BuyTicketForm, 
    RaffleForm, CreditRequestForm, UserWithdrawalRequestForm, 
    AdminWithdrawalProcessForm, PaymentMethodForm, AnnouncementForm, PromotionForm,
    GeneralAnnouncementForm, ExternalAdForm, AccountsReceivableForm, AccountsReceivablePaymentForm
)
from .models import (
    User, Game, Player, ChatMessage, Raffle, Ticket,
    Transaction, Message, CreditRequest, PercentageSettings, UserBlockHistory, WithdrawalRequest, BankAccount, CreditRequestNotification, WithdrawalRequestNotification, PrintableCard, Announcement, VideoCallGroup, BingoTicket, DailyBingoSchedule, BingoTicketSettings, AccountsReceivable, AccountsReceivablePayment, PackageTemplate, Franchise, FranchiseManual,
    DiceModuleSettings, DiceGame, DicePlayer, DiceRound, DiceMatchmakingQueue
)
from .serializers import VideoCallGroupSerializer
from .smart_assistant import smart_assistant
from .ai_assistant import ai_assistant
# Sistema híbrido: usa IA real (Gemini) si está disponible, sino usa asistente local

# PWA Views - Deben estar al inicio para evitar problemas de importación
from django.http import HttpResponse
import os

def manifest_view(request):
    """Servir el manifest.json para PWA"""
    # Intentar múltiples ubicaciones
    possible_paths = [
        os.path.join(settings.STATIC_ROOT, 'bingo_app', 'static', 'manifest.json') if settings.STATIC_ROOT else None,
        os.path.join(settings.BASE_DIR, 'bingo_app', 'static', 'manifest.json'),
        os.path.join(settings.BASE_DIR, 'staticfiles', 'bingo_app', 'static', 'manifest.json'),
    ]
    
    manifest_path = None
    for path in possible_paths:
        if path and os.path.exists(path):
            manifest_path = path
            break
    
    if manifest_path and os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ajustar las rutas de los iconos para que funcionen en producción
        try:
            manifest_data = json.loads(content)
            # Asegurar que las rutas de iconos sean absolutas desde la raíz
            for icon in manifest_data.get('icons', []):
                if icon.get('src', '').startswith('/static/'):
                    # Ya está correcto
                    pass
                elif not icon.get('src', '').startswith('http') and not icon.get('src', '').startswith('/'):
                    icon['src'] = '/static/images/' + os.path.basename(icon.get('src', ''))
            
            content = json.dumps(manifest_data, ensure_ascii=False, indent=2)
        except:
            pass  # Si falla el parse, usar el contenido original
        
        response = HttpResponse(content, content_type='application/manifest+json')
        # Temporalmente sin cache para forzar actualización del nombre
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    else:
        return HttpResponse('Manifest not found', status=404)


def service_worker_view(request):
    """Servir el service-worker.js para PWA"""
    # Intentar múltiples ubicaciones
    possible_paths = [
        os.path.join(settings.STATIC_ROOT, 'bingo_app', 'static', 'js', 'service-worker.js') if settings.STATIC_ROOT else None,
        os.path.join(settings.BASE_DIR, 'bingo_app', 'static', 'js', 'service-worker.js'),
        os.path.join(settings.BASE_DIR, 'staticfiles', 'bingo_app', 'static', 'js', 'service-worker.js'),
    ]
    
    sw_path = None
    for path in possible_paths:
        if path and os.path.exists(path):
            sw_path = path
            break
    
    if sw_path and os.path.exists(sw_path):
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
        response = HttpResponse(content, content_type='application/javascript')
        response['Service-Worker-Allowed'] = '/'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    else:
        return HttpResponse('Service Worker not found', status=404)


def _finalize_player_win(player):
    """
    Marca el bingo como ganado, distribuye premios y notifica a los jugadores.
    Busca TODOS los ganadores antes de finalizar el juego para dividir el premio correctamente.
    Devuelve True si el juego terminó correctamente.
    """
    from django.db import transaction
    
    game = player.game
    
    # Usar select_for_update para evitar condiciones de carrera
    # Solo un proceso puede finalizar el juego a la vez
    try:
        with transaction.atomic():
            # Bloquear el juego para evitar procesamiento simultáneo
            game = Game.objects.select_for_update().get(id=game.id)
            
            # Verificar si el juego ya fue finalizado por otro proceso
            if game.is_finished:
                logger.warning(f"[Game {game.id}] Juego ya finalizado, ignorando intento de finalización.")
                return False
            
            # Buscar TODOS los jugadores que tienen bingo en este momento
            # Esto asegura que el premio se divida entre todos los ganadores
            players = Player.objects.filter(game=game)
            winners = [p.user for p in players if p.check_bingo()]
            
            # Si no hay ganadores, algo salió mal
            if not winners:
                logger.warning(f"[Game {game.id}] No se encontraron ganadores al finalizar manualmente.")
                return False
            
            # Usar end_game_manual con TODOS los ganadores para dividir el premio correctamente
            success = game.end_game_manual(winners)
            return success
    except Exception as e:
        logger.error(f"Error finalizando juego para {player.user.username}: {e}", exc_info=True)
        return False


def register(request):
    # Obtener código de franquicia de la URL (si viene)
    franchise_slug = request.GET.get('franchise', '').strip()
    franchise_from_url = None
    if franchise_slug:
        try:
            franchise_from_url = Franchise.objects.get(slug=franchise_slug, is_active=True)
        except Franchise.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        referral_code = request.POST.get('referral_code', '').strip()
        franchise_code = request.POST.get('franchise_code', '').strip()
        
        if form.is_valid():
            user = form.save()
            
            # Asignar franquicia si se proporcionó código o viene de URL
            franchise_to_assign = None
            if franchise_code:
                # Buscar franquicia por slug o nombre
                try:
                    franchise_to_assign = Franchise.objects.get(
                        slug__iexact=franchise_code, 
                        is_active=True
                    )
                except Franchise.DoesNotExist:
                    try:
                        franchise_to_assign = Franchise.objects.get(
                            name__iexact=franchise_code,
                            is_active=True
                        )
                    except Franchise.DoesNotExist:
                        messages.warning(request, f'Código de franquicia "{franchise_code}" no encontrado o inactivo.')
            
            # Si no se encontró por código, usar el de la URL
            if not franchise_to_assign and franchise_from_url:
                franchise_to_assign = franchise_from_url
            
            # Asignar la franquicia al usuario
            if franchise_to_assign:
                user.franchise = franchise_to_assign
                user.save()
                messages.success(request, f'¡Te has registrado en la franquicia "{franchise_to_assign.name}"!')
            
            # Procesar código de referido si se proporcionó
            if referral_code:
                process_referral_code(user, referral_code, request)
            
            # Enviar email de bienvenida
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                from datetime import datetime
                
                if user.email:
                    subject = '🎉 ¡Bienvenido a Bingo JyM!'
                    fecha = datetime.now().strftime('%d/%m/%Y')
                    message = f'''
Hola {user.username},

¡Bienvenido a Bingo JyM!

Tu cuenta ha sido creada exitosamente el {fecha}.

Ahora puedes:
✅ Participar en juegos de bingo
✅ Comprar tickets para rifas
✅ Gestionar tus créditos
✅ Crear tus propios juegos (si eres organizador)

¡Gracias por unirte a nuestra comunidad!

Saludos,
El equipo de Bingo JyM
                    '''
                    
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=True,  # No fallar el registro si el email falla
                    )
            except Exception as e:
                # Log el error pero no interrumpir el registro
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error enviando email de bienvenida a {user.email}: {str(e)}")
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('lobby')
        
        else:
            # Agregar mensajes de error detallados
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistrationForm()
        # Pre-llenar código de referido si viene en la URL
        referral_code = request.GET.get('referral_code', '')
        # Pre-llenar código de franquicia si viene de la URL
        if franchise_from_url:
            form.fields['franchise_code'].initial = franchise_from_url.slug
            form.fields['franchise_code'].widget.attrs['readonly'] = True
            messages.info(request, f'Registro para la franquicia: {franchise_from_url.name}')
        
    return render(request, 'bingo_app/register.html', {
        'form': form, 
        'referral_code': referral_code,
        'franchise': franchise_from_url
    })

def process_referral_code(new_user, referral_code, request):
    """Procesar código de referido y otorgar tickets de bingo"""
    from .models import User, ReferralProgram, BingoTicket, BingoTicketSettings
    from django.contrib import messages
    from datetime import timedelta
    
    try:
        # Verificar si el sistema de referidos está habilitado
        percentage_settings = PercentageSettings.objects.first()
        if not percentage_settings or not percentage_settings.referral_system_enabled:
            messages.warning(request, "El sistema de referidos está temporalmente deshabilitado.")
            return
        
        # Obtener configuración de tickets
        ticket_settings = BingoTicketSettings.get_settings()
        
        # Si el sistema de tickets no está activo, usar el sistema anterior de créditos
        if not ticket_settings.is_system_active:
            # Sistema anterior con créditos
            referrer = User.objects.get(username__iexact=referral_code)
            
            if referrer.id == new_user.id:
                messages.warning(request, "No puedes usar tu propio código de referido.")
                return
            
            if ReferralProgram.objects.filter(referred_user=new_user).exists():
                messages.warning(request, "Ya has usado un código de referido anteriormente.")
                return
            
            referral = ReferralProgram.objects.create(
                referrer=referrer,
                referred_user=new_user,
                referral_code=referral_code.upper(),
                bonus_amount=5.00
            )
            
            bonus_amount = 5.00
            new_user.credit_balance += bonus_amount
            new_user.save()
            
            referrer.credit_balance += bonus_amount
            referrer.save()
            
            referral.is_paid = True
            referral.save()
            
            messages.success(request, f"¡Código de referido válido! Has recibido ${bonus_amount} en créditos.")
            messages.success(request, f"Tu amigo {referrer.username} también recibió ${bonus_amount} en créditos.")
            return
        
        # Sistema nuevo con tickets
        referrer = User.objects.get(username__iexact=referral_code)
        
        if referrer.id == new_user.id:
            messages.warning(request, "No puedes usar tu propio código de referido.")
            return
        
        if ReferralProgram.objects.filter(referred_user=new_user).exists():
            messages.warning(request, "Ya has usado un código de referido anteriormente.")
            return
        
        # Crear el registro de referido
        referral = ReferralProgram.objects.create(
            referrer=referrer,
            referred_user=new_user,
            referral_code=referral_code.upper(),
            bonus_amount=0.00  # Ya no usamos créditos
        )
        
        # Calcular fecha de expiración
        expiration_date = timezone.now() + timedelta(days=ticket_settings.ticket_expiration_days)
        
        # Otorgar tickets al nuevo usuario
        for i in range(ticket_settings.referred_ticket_bonus):
            BingoTicket.objects.create(
                user=new_user,
                ticket_type='REFERRAL',
                expires_at=expiration_date
            )
        
        # Otorgar tickets al referidor
        for i in range(ticket_settings.referral_ticket_bonus):
            BingoTicket.objects.create(
                user=referrer,
                ticket_type='REFERRAL',
                expires_at=expiration_date
            )
        
        # Marcar como pagado
        referral.is_paid = True
        referral.save()
        
        # Mensajes de éxito
        messages.success(request, f"¡Código de referido válido! Has recibido {ticket_settings.referred_ticket_bonus} ticket(s) de bingo.")
        messages.success(request, f"Tu amigo {referrer.username} también recibió {ticket_settings.referral_ticket_bonus} ticket(s) de bingo.")
        
    except User.DoesNotExist:
        messages.error(request, f"El código de referido '{referral_code}' no es válido.")
    except Exception as e:
        messages.error(request, f"Error al procesar el código de referido: {str(e)}")

def custom_login_view(request):
    from .models import Franchise
    
    # 1. PRIMERO: Intentar obtener franquicia del middleware (detectada por dominio)
    franchise = getattr(request, 'franchise', None)
    
    # 2. SEGUNDO: Si no hay franquicia del middleware, intentar obtener de la URL
    if not franchise:
        franchise_slug = request.GET.get('franchise', '').strip()
        if franchise_slug:
            try:
                franchise = Franchise.objects.get(slug=franchise_slug, is_active=True)
                # Guardar en sesión para mantenerla después de logout
                request.session['franchise_id'] = franchise.id
            except Franchise.DoesNotExist:
                pass
    
    # 3. TERCERO: Si aún no hay franquicia, intentar obtener de la sesión (después de logout)
    if not franchise:
        franchise_id = request.session.get('franchise_id')
        if franchise_id:
            try:
                franchise = Franchise.objects.get(id=franchise_id, is_active=True)
            except Franchise.DoesNotExist:
                # Si la franquicia ya no existe, limpiar sesión
                request.session.pop('franchise_id', None)
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # Si hay franquicia detectada, guardarla en sesión
            if franchise:
                request.session['franchise_id'] = franchise.id
            return redirect('lobby')
        else:
            # Usar los mensajes de error genéricos del formulario de login
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error)
            else:
                # Fallback por si no hay non_field_errors pero el form es inválido
                messages.error(request, "Por favor, introduce un nombre de usuario y contraseña correctos.")

    else:
        form = AuthenticationForm()
    return render(request, 'bingo_app/login.html', {
        'form': form,
        'franchise': franchise  # Usar la franquicia detectada (por dominio, URL o sesión)
    })

def home(request):
    """Vista para la ruta raíz - redirige a lobby si está autenticado, sino a login"""
    if request.user.is_authenticated:
        return redirect('lobby')
    else:
        return redirect('login')

def franchise_landing(request, franchise_slug):
    # Trigger deploy - Railway
    """
    Página de bienvenida/landing para una franquicia
    Muestra la imagen personalizada y permite registrarse
    """
    try:
        # Intentar buscar por slug (case-insensitive)
        franchise = Franchise.objects.get(slug__iexact=franchise_slug, is_active=True)
    except Franchise.DoesNotExist:
        # Intentar buscar sin verificar is_active para dar más información
        try:
            franchise_inactive = Franchise.objects.get(slug__iexact=franchise_slug)
            messages.error(request, f'La franquicia "{franchise_inactive.name}" existe pero está inactiva. Contacta al administrador.')
        except Franchise.DoesNotExist:
            # Listar todas las franquicias activas para debugging
            all_franchises = Franchise.objects.filter(is_active=True).values_list('slug', 'name')
            messages.error(request, f'Franquicia con slug "{franchise_slug}" no encontrada. Franquicias activas: {", ".join([f"{name} ({slug})" for slug, name in all_franchises])}')
        return redirect('register')
    
    return render(request, 'bingo_app/franchise_landing.html', {
        'franchise': franchise
    })

@login_required
def lobby(request):
    # Obtener la franquicia del usuario (si tiene)
    franchise = getattr(request, 'franchise', None)
    
    # Filtrar juegos y rifas por franquicia
    # Si es super admin, puede ver todo (franchise = None)
    # Si tiene franquicia, solo ve los de su franquicia
    if franchise:
        active_games = Game.objects.filter(is_active=True, is_finished=False, franchise=franchise)
        active_raffles = Raffle.objects.filter(status__in=['WAITING', 'IN_PROGRESS'], franchise=franchise)
    elif request.user.is_superuser or request.user.is_admin:
        # Super admin puede ver todo
        active_games = Game.objects.filter(is_active=True, is_finished=False)
        active_raffles = Raffle.objects.filter(status__in=['WAITING', 'IN_PROGRESS'])
    else:
        # Usuario sin franquicia solo ve juegos/rifas sin franquicia asignada
        active_games = Game.objects.filter(is_active=True, is_finished=False, franchise__isnull=True)
        active_raffles = Raffle.objects.filter(status__in=['WAITING', 'IN_PROGRESS'], franchise__isnull=True)
    
    joined_game_ids = list(Player.objects.filter(user=request.user).values_list('game_id', flat=True))
    
    if request.user.is_authenticated:
        if franchise:
            wins_count = Game.objects.filter(winner=request.user, franchise=franchise).count()
        else:
            wins_count = Game.objects.filter(winner=request.user).count()
    else:
        wins_count = 0
    
    # Fetch active announcements for the lobby
    announcements = Announcement.objects.filter(is_active=True).order_by('order')
    
    # Verificar si el módulo de dados está habilitado y si el usuario puede acceder
    from .utils.dice_module import is_dice_module_enabled, can_user_access_dice_module
    dice_module_enabled = False
    dice_module_enabled_global = is_dice_module_enabled()
    if dice_module_enabled_global:
        if request.user.is_authenticated:
            can_access, _ = can_user_access_dice_module(request.user)
            dice_module_enabled = can_access
        else:
            # Usuario no autenticado - solo mostrar si está habilitado globalmente
            dice_module_enabled = True

    context = {
        'games': active_games,
        'raffles': active_raffles,
        'wins_count': wins_count,
        'announcements': announcements, # Add this line
        'joined_game_ids': joined_game_ids,
        'dice_module_enabled': dice_module_enabled,
    }
    
    return render(request, 'bingo_app/lobby.html', context)

@login_required
def create_game(request):
    if not request.user.is_organizer:
        messages.error(request, "Solo los organizadores pueden crear juegos")
        return redirect('lobby')
    
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            # Verificar que el organizador tenga suficiente saldo
            base_prize = form.cleaned_data['base_prize']
            
            try:
                with transaction.atomic():
                    # Calcular tarifa de creación de juego (solo si está activada)
                    percentage_settings = PercentageSettings.objects.first()
                    creation_fee = Decimal('0.00')
                    
                    if percentage_settings and percentage_settings.game_creation_fee_enabled:
                        creation_fee = percentage_settings.game_creation_fee
                    elif not percentage_settings:
                        # Si no hay configuración, usar tarifa por defecto
                        creation_fee = Decimal('1.00')
                    
                    total_cost = base_prize + creation_fee
                    
                    # Verificar que el organizador tenga suficiente saldo para el premio + tarifa
                    if request.user.credit_balance < total_cost:
                        messages.error(request, f'Saldo insuficiente. Necesitas {total_cost} créditos (premio: {base_prize} + tarifa: {creation_fee})')
                        return render(request, 'bingo_app/create_game.html', {'form': form})
                    
                    # Descontar el premio base y la tarifa del saldo del organizador
                    request.user.credit_balance -= total_cost
                    # Bloquear el premio base en blocked_credits
                    request.user.blocked_credits += base_prize
                    request.user.save()
                    
                    # Crear el juego
                    game = form.save(commit=False)
                    game.organizer = request.user
                    game.prize = base_prize  # Establecer premio inicial
                    # Asignar la franquicia del organizador al juego
                    franchise = getattr(request, 'franchise', None)
                    if franchise:
                        game.franchise = franchise
                    game.save()

                    # Crear el grupo de videollamada asociado al juego (si el usuario lo desea)
                    if form.cleaned_data.get('create_video_room', True):
                        video_room_type = form.cleaned_data.get('video_room_type', 'public')
                        video_password = form.cleaned_data.get('video_room_password', '')
                        is_public = (video_room_type == 'public')
                        
                        video_channel_name = f"game-{game.id}-video-{uuid.uuid4().hex[:8]}"
                        video_group = VideoCallGroup.objects.create(
                            game=game,
                            name=f"Sala de video para {game.name}",
                            created_by=request.user,
                            agora_channel_name=video_channel_name,
                            is_public=is_public,
                            password=video_password if not is_public else '',
                            is_persistent=True  # La sala persiste incluso después de que termine el juego
                        )
                        video_group.participants.add(request.user)

                    # Notify lobby
                    channel_layer = get_channel_layer()
                    html = render_to_string('bingo_app/partials/game_card.html', {
                        'game': game,
                        'level': game.organizer.reputation_level,
                        'joined_game_ids': []
                    })
                    async_to_sync(channel_layer.group_send)(
                        'lobby',
                        {
                            'type': 'new_game_created',
                            'html': html
                        }
                    )

                    # Manejar patrón personalizado
                    if game.winning_pattern == 'CUSTOM':
                        if 'pattern_file' in request.FILES:
                            try:
                                pattern_data = json.load(request.FILES['pattern_file'])
                                game.custom_pattern = pattern_data
                            except json.JSONDecodeError:
                                messages.error(request, "El archivo de patrón debe ser un JSON válido")
                                return render(request, 'bingo_app/create_game.html', {'form': form})
                
                    
                    # Registrar las transacciones
                    # 1. Premio base (para el organizador)
                    Transaction.objects.create(
                        user=request.user,
                        amount=-base_prize,
                        transaction_type='PRIZE_LOCK',
                        description=f"Premio base para juego {game.name}",
                        related_game=game
                    )
                    
                    # 2. Tarifa de creación (para la plataforma) - solo si está activada
                    if creation_fee > 0:
                        Transaction.objects.create(
                            user=request.user,
                            amount=-creation_fee,
                            transaction_type='GAME_CREATION_FEE',
                            description=f"Tarifa de creación de juego {game.name}",
                            related_game=game
                        )
                        
                        # 3. Dar la tarifa al admin
                        admin = User.objects.filter(is_superuser=True).first()
                        if admin:
                            admin.credit_balance += creation_fee
                            admin.save()
                            Transaction.objects.create(
                                user=admin,
                                amount=creation_fee,
                                transaction_type='GAME_CREATION_FEE',
                                description=f"Tarifa por creación de juego {game.name}",
                                related_game=game
                            )
                    
                    messages.success(request, '¡Juego creado exitosamente!')
                    return redirect('game_room', game_id=game.id)
                    
            except Exception as e:
                messages.error(request, f'Error al crear el juego: {str(e)}')
    else:
        form = GameForm()
    
    return render(request, 'bingo_app/create_game.html', {
        'form': form,
        'current_balance': request.user.credit_balance
    })

@login_required
def edit_game_config(request, game_id):
    """
    Vista para editar la configuración de un juego NO iniciado.
    Permite editar niveles progresivos y algunos campos básicos.
    """
    game = get_object_or_404(Game, id=game_id)
    
    # Verificar que el usuario sea el organizador
    if game.organizer != request.user:
        messages.error(request, "No tienes permiso para editar este juego")
        return redirect('game_room', game_id=game_id)
    
    # Verificar que el juego no haya iniciado
    if game.is_started:
        messages.error(request, "No se puede editar un juego que ya ha iniciado")
        return redirect('game_room', game_id=game_id)
    
    if request.method == 'POST':
        form = GameEditForm(request.POST, instance=game)
        if form.is_valid():
            try:
                with transaction.atomic():
                    organizer = request.user
                    
                    # Procesar ajuste del premio base si se proporcionó y hay diferencia
                    new_base_prize = form.cleaned_data.get('new_base_prize')
                    if new_base_prize is not None:
                        current_prize = game.base_prize
                        diferencia = Decimal(str(new_base_prize)) - Decimal(str(current_prize))
                        
                        # Solo procesar si hay una diferencia real
                        if diferencia > 0:  # AUMENTAR premio
                            # Verificar saldo suficiente
                            if organizer.credit_balance >= diferencia:
                                # Bloquear créditos adicionales
                                organizer.credit_balance -= diferencia
                                organizer.blocked_credits += diferencia
                                organizer.save()
                                
                                # Actualizar premio
                                game.base_prize = new_base_prize
                                
                                # Registrar transacción
                                Transaction.objects.create(
                                    user=organizer,
                                    amount=-diferencia,
                                    transaction_type='PRIZE_LOCK',
                                    description=f"Ajuste de premio base: {current_prize} → {new_base_prize} créditos",
                                    related_game=game
                                )
                                
                                messages.success(request, 
                                    f'Premio aumentado de {current_prize} a {new_base_prize} créditos. '
                                    f'Se bloquearon {diferencia} créditos adicionales.'
                                )
                            else:
                                messages.error(request, 
                                    f'Saldo insuficiente. Necesitas {diferencia} créditos adicionales. '
                                    f'Tu saldo disponible es {organizer.credit_balance} créditos.'
                                )
                                return render(request, 'bingo_app/edit_game_config.html', {
                                    'form': form,
                                    'game': game,
                                    'percentage_settings': PercentageSettings.objects.first()
                                })
                        
                        elif diferencia < 0:  # REDUCIR premio
                            diferencia_abs = abs(diferencia)
                            
                            # Verificar que hay suficientes créditos bloqueados
                            if organizer.blocked_credits >= diferencia_abs:
                                # Desbloquear créditos
                                organizer.blocked_credits -= diferencia_abs
                                organizer.credit_balance += diferencia_abs
                                organizer.save()
                                
                                # Actualizar premio
                                game.base_prize = new_base_prize
                                
                                # Registrar transacción
                                Transaction.objects.create(
                                    user=organizer,
                                    amount=diferencia_abs,
                                    transaction_type='PRIZE_UNLOCK',
                                    description=f"Reducción de premio base: {current_prize} → {new_base_prize} créditos",
                                    related_game=game
                                )
                                
                                messages.warning(request, 
                                    f'Premio reducido de {current_prize} a {new_base_prize} créditos. '
                                    f'Se desbloquearon {diferencia_abs} créditos. '
                                    f'⚠️ Esto puede decepcionar a los jugadores.'
                                )
                            else:
                                messages.error(request, 
                                    f'No hay suficientes créditos bloqueados. Tienes {organizer.blocked_credits} bloqueados, '
                                    f'pero necesitas {diferencia_abs} para reducir el premio.'
                                )
                                return render(request, 'bingo_app/edit_game_config.html', {
                                    'form': form,
                                    'game': game,
                                    'percentage_settings': PercentageSettings.objects.first()
                                })
                    
                    # Guardar los cambios del formulario
                    game = form.save()
                    
                    # Recalcular premio total (incluye niveles progresivos)
                    game.prize = game.calculate_prize()
                    game.save()
                    
                    # Notificar actualización a la sala
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'game_{game.id}',
                        {
                            'type': 'game_updated',
                            'message': 'La configuración del juego ha sido actualizada',
                            'new_prize': float(game.prize),
                            'new_base_prize': float(game.base_prize),
                            'progressive_prizes': game.progressive_prizes
                        }
                    )
                    
                    messages.success(request, '¡Configuración actualizada exitosamente!')
                    return redirect('game_room', game_id=game_id)
            except Exception as e:
                messages.error(request, f'Error al actualizar la configuración: {str(e)}')
    else:
        form = GameEditForm(instance=game)
    
    percentage_settings = PercentageSettings.objects.first()
    
    return render(request, 'bingo_app/edit_game_config.html', {
        'form': form,
        'game': game,
        'percentage_settings': percentage_settings
    })

@login_required
def game_room(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # Verificar si el jugador ya existe ANTES de crear
    player = Player.objects.filter(user=request.user, game=game).first()
    created = False
    
    if not player:
        # Solo crear si realmente no existe
        player, created = Player.objects.get_or_create(user=request.user, game=game)
    
    percentage_settings = PercentageSettings.objects.first()

    # Get all video call groups for this game (incluso si el juego terminó)
    # También incluir salas persistentes donde el usuario es participante o creador
    # Esto permite ver tus salas desde cualquier juego
    video_groups = VideoCallGroup.objects.filter(
        is_persistent=True
    ).filter(
        Q(game=game) | Q(participants=request.user) | Q(created_by=request.user)
    ).distinct()
    
    # Auto-join public video groups del juego actual si el jugador acaba de unirse O si vuelve a la sala
    # Esto permite que los usuarios se re-unan a salas existentes incluso después de salir
    game_video_groups = video_groups.filter(game=game, is_public=True)
    for vg in game_video_groups:
        if request.user not in vg.participants.all():
            vg.participants.add(request.user)
    
    # NO se cobra entrada - solo se cobra al comprar cartones
    # Los jugadores pueden entrar libremente a la sala

    # Handle card purchases
    if request.method == 'POST' and 'buy_card' in request.POST and not game.is_started:
        if len(player.cards) >= game.max_cards_per_player:
            messages.error(request, 'Has alcanzado el límite de cartones')
        elif request.user.credit_balance < game.card_price:
            messages.error(request, f'Saldo insuficiente. Necesitas {game.card_price} créditos')
        else:
            try:
                with transaction.atomic():
                    # Generate new card
                    new_card = generate_bingo_card()
                    player.cards.append(new_card)
                    player.save()
                    
                    # Charge for card
                    request.user.credit_balance -= game.card_price
                    request.user.save()
                    
                    # Record transaction
                    Transaction.objects.create(
                        user=request.user,
                        amount=-game.card_price,
                        transaction_type='PURCHASE',
                        description=f"Cartón adicional para {game.name}",
                        related_game=game
                    )
                    
                    # Distribute purchase
                    distribute_purchase(game, game.card_price, percentage_settings)
                    
                    # Update game stats
                    game.total_cards_sold += 1
                    game.save()
                    
                    # Check for progressive prize
                    check_progressive_prize(game)
                    
                    messages.success(request, '¡Cartón comprado exitosamente!')
                    
            except Exception as e:
                messages.error(request, f'Error al comprar cartón: {str(e)}')

    # Handle bingo claims
    if request.method == 'POST' and 'claim_bingo' in request.POST and game.is_started and not game.is_finished:
        if player.check_bingo():
            try:
                with transaction.atomic():
                    # Mark winner
                    player.is_winner = True
                    player.save()
                    
                    game.winner = request.user
                    game.is_finished = True
                    game.save()

                    print("PASE POR AQUI EN CLAIM 1")
                    add_flash_message(request, f"¡GANASTE EL BINGO! Premio: {game.prize} créditos")

                    
                    
                     # Enviar notificación via WebSocket

                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{request.user.id}",  # Grupo único por usuario
                        {
                            'type': 'win_notification',
                            'message': f"¡BINGO! Ganaste {game.prize} créditos",
                            'prize': float(game.prize)
                        }
                    )
                    
            except Exception as e:
                messages.error(request, f'Error al procesar el premio: {str(e)}')
        else:
            messages.error(request, 'No has completado el patrón ganador')

    chat_messages = ChatMessage.objects.filter(game=game).order_by('-timestamp')[:50]
    
    # Fetch active announcements
    announcements = Announcement.objects.filter(is_active=True).order_by('order')
    
    # Obtener todos los ganadores del juego
    winners = Player.objects.filter(game=game, is_winner=True).select_related('user')
    winners_list = [w.user for w in winners]

    return render(request, 'bingo_app/game_room.html', {
        'game': game,
        'player': player,
        'chat_messages': chat_messages,
        'announcements': announcements,
        'video_groups': video_groups,
        'agora_app_id': settings.AGORA_APP_ID,
        'winners': winners_list,
    })

def distribute_purchase(game, amount, percentage_settings):
    """Distribute card purchase according to percentages"""
    # Si la comisión está habilitada, calcular comisión de plataforma
    if percentage_settings.platform_commission_enabled:
        commission_rate = percentage_settings.platform_commission / 100
        admin_share = amount * Decimal(commission_rate)
        organizer_share = amount - admin_share
        
        # Credit admin
        admin = User.objects.filter(is_admin=True).first()
        if admin:
            admin.credit_balance += admin_share
            admin.save()
            Transaction.objects.create(
                user=admin,
                amount=admin_share,
                transaction_type='ADMIN_ADD',
                description=f"Comisión de plataforma de compra en {game.name} ({percentage_settings.platform_commission}%)",
                related_game=game
            )
        
        # Credit organizer (después de comisión)
        game.organizer.credit_balance += organizer_share
        game.organizer.save()
        Transaction.objects.create(
            user=game.organizer,
            amount=organizer_share,
            transaction_type='ADMIN_ADD',
            description=f"Ingresos de compra en {game.name} (después de comisión)",
            related_game=game
        )
    else:
        # Sin comisión, el organizador recibe todo
        game.organizer.credit_balance += amount
        game.organizer.save()
        Transaction.objects.create(
            user=game.organizer,
            amount=amount,
            transaction_type='ADMIN_ADD',
            description=f"Ingresos de compra en {game.name}",
            related_game=game
        )

def check_progressive_prize(self):
    """Verifica y aplica premios progresivos, devuelve el incremento del premio"""
    old_prize = self.prize
    self.prize = self.calculate_prize()
    self.save()
    
    # Calcula el próximo objetivo si hay premios progresivos
    if self.progressive_prizes:
        next_target = None
        for prize in sorted(self.progressive_prizes, key=lambda x: x['target']):
            if self.total_cards_sold < prize['target']:
                next_target = prize['target']
                break
        
        self.next_prize_target = next_target
        self.save()
    
    return self.prize - old_prize  # Devuelve solo el incremento

def distribute_remaining_funds(game, percentage_settings):
    """Distribute remaining funds after game ends"""
    # NO se cobra entrada - solo se calcula por cartones vendidos
    # total_collected = game.card_price * game.total_cards_sold (ya está en game.held_balance)
    total_collected = game.held_balance if game.held_balance else 0
    total_prize = game.prize if game.prize else 0
    
    remaining_funds = total_collected - total_prize
    
    if remaining_funds > 0:
        # Si la comisión está habilitada, calcular distribución
        if percentage_settings.platform_commission_enabled:
            commission_rate = percentage_settings.platform_commission / 100
            admin_share = remaining_funds * Decimal(commission_rate)
            organizer_share = remaining_funds - admin_share
        else:
            # Sin comisión, el organizador recibe todo
            admin_share = Decimal('0.00')
            organizer_share = remaining_funds
        
        # Credit admin
        admin = User.objects.filter(is_admin=True).first()
        if admin:
            admin.credit_balance += admin_share
            admin.save()
            Transaction.objects.create(
                user=admin,
                amount=admin_share,
                transaction_type='ADMIN_ADD',
                description=f"Porcentaje admin final de {game.name}",
                related_game=game
            )
        
        # Credit organizer
        game.organizer.credit_balance += organizer_share
        game.organizer.save()
        Transaction.objects.create(
            user=game.organizer,
            amount=organizer_share,
            transaction_type='ADMIN_ADD',
            description=f"Porcentaje organizador final de {game.name}",
            related_game=game
        )


def generate_bingo_card():
    """Genera un cartón de Bingo tradicional 5x5 con letras B-I-N-G-O y comodín central"""
    # Rangos para cada columna según las letras B-I-N-G-O
    ranges = {
        'B': (1, 15),
        'I': (16, 30),
        'N': (31, 45),
        'G': (46, 60),
        'O': (61, 75)
    }
    
    card = []
    for letter in ['B', 'I', 'N', 'G', 'O']:
        # Generar 5 números únicos para cada columna
        start, end = ranges[letter]
        numbers = random.sample(range(start, end+1), 5)
        
        # Para la columna N (tercera columna), el tercer número es comodín (0 o vacío)
        if letter == 'N':
            numbers[2] = 0  # O usar "" para representar el comodín
        
        card.append(numbers)
    
    # Transponer la matriz para tener filas en lugar de columnas
    card_rows = list(zip(*card))
    
    return list(card_rows)

@login_required
def profile(request):
    if request.method == 'POST':
        # El valor de un checkbox no marcado no se envía, así que usamos .get()
        is_organizer_val = request.POST.get('is_organizer', 'off') == 'on'
        
        # Solo actualizamos si hay un cambio para evitar escrituras innecesarias
        if request.user.is_organizer != is_organizer_val:
            request.user.is_organizer = is_organizer_val
            request.user.save(update_fields=['is_organizer'])
            messages.success(request, 'Tu perfil ha sido actualizado.')
        
        return redirect('profile')

    won_raffles = Raffle.objects.filter(winner=request.user)
    games_playing = request.user.player_set.all()
    
    # Calcular victorias: verificar tanto game.winner como player.is_winner
    # Algunos juegos pueden tener winner pero el player.is_winner no estar marcado
    won_games_by_winner = Game.objects.filter(winner=request.user)
    won_players = games_playing.filter(is_winner=True)
    # Combinar ambas fuentes para obtener todas las victorias
    won_game_ids = set(won_games_by_winner.values_list('id', flat=True))
    won_game_ids.update(won_players.values_list('game_id', flat=True))
    won_count = len(won_game_ids)
    
    # Calcular estadísticas de partidas
    total_games = games_playing.count()  # Total de partidas en las que participó
    # Solo contar partidas terminadas para estadísticas precisas
    finished_games = games_playing.filter(game__is_finished=True)
    total_finished_games = finished_games.count()
    # Las partidas perdidas son las terminadas donde el usuario no ganó
    lost_count = total_finished_games - won_count
    
    # Calcular total de cartones comprados
    total_cards = sum(len(player.cards) for player in games_playing)
    
    # Calcular gastos en cartones de bingo
    card_transactions = Transaction.objects.filter(
        user=request.user,
        transaction_type='PURCHASE',
        related_game__isnull=False
    )
    total_spent_on_cards = abs(sum(t.amount for t in card_transactions))
    
    # Calcular gastos en rifas (transacciones de tipo PURCHASE que mencionan "rifa" en la descripción)
    # Las transacciones de rifas tienen "rifa" en la descripción y no tienen related_game
    raffle_transactions = Transaction.objects.filter(
        user=request.user,
        transaction_type='PURCHASE',
        description__icontains='rifa'
    )
    total_spent_on_raffles = abs(sum(t.amount for t in raffle_transactions))
    
    # Calcular ganancias totales
    prize_transactions = Transaction.objects.filter(
        user=request.user,
        transaction_type='PRIZE'
    )
    total_earnings = sum(t.amount for t in prize_transactions)
    
    # Obtener todas las transacciones ordenadas por fecha (más antiguas primero)
    # Excluir PRIZE_UNLOCK porque son solo desbloqueos internos, no movimientos reales de créditos disponibles
    # El desbloqueo no aumenta el saldo disponible, solo libera créditos que ya estaban bloqueados
    all_transactions = Transaction.objects.filter(
        user=request.user
    ).exclude(
        transaction_type='PRIZE_UNLOCK'
    ).order_by('created_at')
    
    # Calcular saldo acumulado desde el principio
    # Primero calculamos el saldo total de todas las transacciones
    total_from_transactions = sum(t.amount for t in all_transactions)
    
    # Calcular saldo antes y después de cada transacción
    # Empezamos desde el saldo actual y vamos hacia atrás para verificar
    transaction_history = []
    running_balance = Decimal('0.00')
    
    # Calcular desde el principio hacia adelante
    for trans in all_transactions:
        balance_before = running_balance
        running_balance += trans.amount
        balance_after = running_balance
        
        transaction_history.append({
            'transaction': trans,
            'balance_before': balance_before,
            'balance_after': balance_after,
            'amount': trans.amount,
            'amount_abs': abs(trans.amount),  # Valor absoluto para mostrar en template
        })
    
    # Invertir el orden para mostrar las más recientes primero
    transaction_history.reverse()
    
    # Nota: El saldo final calculado debería coincidir con el saldo actual del usuario
    # Si hay discrepancias, puede haber transacciones no registradas o modificaciones manuales
    
    return render(request, 'bingo_app/profile.html', {
        'user': request.user,
        'games_created': request.user.organized_games.all(),
        'games_playing': games_playing,
        'won_games': Game.objects.filter(id__in=won_game_ids) if won_game_ids else Game.objects.none(),
        'won_raffles': won_raffles,
        'total_games': total_games,
        'won_count': won_count,
        'lost_count': lost_count,
        'total_cards': total_cards,
        'total_spent_on_cards': total_spent_on_cards,
        'total_spent_on_raffles': total_spent_on_raffles,
        'total_earnings': total_earnings,
        'transaction_history': transaction_history,
    })

@login_required
def request_credits(request):
    # Verificar si el sistema de compra de créditos está habilitado
    settings_obj = PercentageSettings.objects.first()
    if not settings_obj or not settings_obj.credits_purchase_enabled:
        messages.error(request, 'El sistema de compra de créditos está temporalmente deshabilitado.')
        return redirect('profile')
    
    if request.method == 'POST':
        form = CreditRequestForm(request.POST, request.FILES)
        if form.is_valid():
            credit_request = form.save(commit=False)
            credit_request.user = request.user
            # Asignar la franquicia del usuario a la solicitud
            franchise = getattr(request, 'franchise', None)
            if franchise:
                credit_request.franchise = franchise
            credit_request.save()

            # --- INICIO DE LA CORRECCIÓN ---
            # 1. Crear notificaciones en la base de datos
            # Si la solicitud pertenece a una franquicia, notificar al propietario de la franquicia
            # Si no, notificar a los superusuarios
            if credit_request.franchise and credit_request.franchise.owner:
                # Notificar al propietario de la franquicia
                franchise_owner = credit_request.franchise.owner
                CreditRequestNotification.objects.create(
                    user=franchise_owner,
                    credit_request=credit_request
                )
                notification_url = reverse('franchise_owner_credit_requests')
                print(f"🔊 request_credits: Notificación para propietario de franquicia: {franchise_owner.username}")
            else:
                # Notificar a superusuarios (solicitudes sin franquicia)
                admins_and_organizers = User.objects.filter(is_superuser=True)
                for user in admins_and_organizers:
                    CreditRequestNotification.objects.create(
                        user=user,
                        credit_request=credit_request
                    )
                notification_url = reverse('credit_requests_list')
                print(f"🔊 request_credits: Notificación para superusuarios")

            # 2. Notificar via WebSocket
            try:
                channel_layer = get_channel_layer()
                
                print(f"🔊 request_credits: Enviando notificación WebSocket")
                print(f"🔊 request_credits: Usuario solicitante: {credit_request.user.username}")
                print(f"🔊 request_credits: Monto: ${credit_request.amount}")
                print(f"🔊 request_credits: Franquicia: {credit_request.franchise.name if credit_request.franchise else 'Sin franquicia'}")
                
                # Obtener el ID de la notificación creada
                notification_id = None
                if credit_request.franchise and credit_request.franchise.owner:
                    notification = CreditRequestNotification.objects.filter(
                        user=credit_request.franchise.owner,
                        credit_request=credit_request
                    ).first()
                    if notification:
                        notification_id = notification.id
                else:
                    # Para superusuarios, obtener la primera notificación creada
                    notification = CreditRequestNotification.objects.filter(
                        credit_request=credit_request
                    ).first()
                    if notification:
                        notification_id = notification.id
                
                # Enviar a un grupo general de admins (para sonido)
                async_to_sync(channel_layer.group_send)(
                    'admin_notifications',
                    {
                        'type': 'admin_notification',
                        'notification_type': 'new_credit_request',
                        'message': f'Nueva solicitud de crédito de {credit_request.user.username} por ${credit_request.amount}.',
                        'url': notification_url,
                        'sound_type': 'credit_request',
                        'notification_id': notification_id
                    }
                )
                print(f"🔊 request_credits: Notificación WebSocket enviada exitosamente con ID: {notification_id}")
            except Exception as e:
                logger.error(f"Error sending WebSocket notification: {e}")
                print(f"🔊 request_credits: ERROR enviando notificación WebSocket: {e}")
            # --- FIN DE LA CORRECCIÓN ---

            messages.success(request, 'Solicitud de créditos enviada')
            return redirect('profile')
    else:
        form = CreditRequestForm()
    
    # Filtrar métodos de pago por franquicia del usuario
    franchise = getattr(request, 'franchise', None)
    if franchise:
        # Usuario de franquicia: solo ver cuentas de su franquicia
        active_payment_methods = BankAccount.objects.filter(
            franchise=franchise,
            is_active=True
        ).order_by('-order', 'title')
    else:
        # Usuario sin franquicia: ver cuentas globales (sin franquicia)
        active_payment_methods = BankAccount.objects.filter(
            franchise__isnull=True,
            is_active=True
        ).order_by('-order', 'title')
    
    return render(request, 'bingo_app/credit_request.html', {
        'form': form,
        'payment_methods': active_payment_methods
    })

@staff_member_required
def credit_requests_list(request):
    requests = CreditRequest.objects.filter(status='pending').order_by('created_at')
    return render(request, 'bingo_app/admin/credit_requests.html', {'requests': requests})

@staff_member_required
def process_request(request, request_id):
    credit_request = get_object_or_404(CreditRequest, id=request_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            credit_request.status = 'approved'
            credit_request.user.credit_balance += credit_request.amount
            credit_request.user.save()
            
            # Crear transacción para el historial
            Transaction.objects.create(
                user=credit_request.user,
                amount=credit_request.amount,
                transaction_type='ADMIN_ADD',
                description=f"Recarga aprobada por admin: {request.user.username}"
            )
            
            # Enviar notificación de sonido al usuario
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{credit_request.user.id}",
                {
                    'type': 'credit_approved_notification',
                    'amount': float(credit_request.amount),
                    'message': f'¡Solicitud de créditos aprobada! Se agregaron ${credit_request.amount} a tu cuenta.'
                }
            )
            
            messages.success(request, 'Solicitud aprobada y créditos asignados')
        elif action == 'reject':
            credit_request.status = 'rejected'
            
            # Enviar notificación de sonido al usuario
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{credit_request.user.id}",
                {
                    'type': 'credit_rejected_notification',
                    'amount': float(credit_request.amount),
                    'message': f'Solicitud de créditos rechazada por ${credit_request.amount}.'
                }
            )
            
            messages.success(request, 'Solicitud rechazada')
        credit_request.admin_notes = request.POST.get('notes', '')
        credit_request.processed_at = datetime.now()
        credit_request.save()
        return redirect('credit_requests_list')
    return render(request, 'bingo_app/admin/process_request.html', {'request': credit_request})

@login_required
@require_http_methods(["POST"])
def buy_card(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = get_object_or_404(Player, user=request.user, game=game)
    
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (json.JSONDecodeError, ValueError):
        quantity = 1

    # Validaciones
    if game.is_started:
        return JsonResponse({'success': False, 'error': 'El juego ya ha comenzado'}, status=400)
    
    if (len(player.cards) + quantity) > game.max_cards_per_player:
        return JsonResponse({'success': False, 'error': f'No puedes comprar {quantity} cartones. Excederías el límite de {game.max_cards_per_player} por jugador.'}, status=400)
    
    total_cost = game.card_price * quantity
    if request.user.credit_balance < total_cost:
        return JsonResponse({'success': False, 'error': f'Saldo insuficiente. Necesitas {total_cost} créditos.'}, status=400)
    
    try:
        with transaction.atomic():
            # Generar nuevos cartones
            new_cards = [generate_bingo_card() for _ in range(quantity)]
            player.cards.extend(new_cards)
            player.save()
            
            # Descontar créditos
            request.user.credit_balance -= total_cost
            request.user.save()
            
            # Registrar transacción
            Transaction.objects.create(
                user=request.user,
                amount=-total_cost,
                transaction_type='PURCHASE',
                description=f"Compra de {quantity} cartón(es) para partida: {game.name}",
                related_game=game
            )
            
            # Actualizar saldo bloqueado del juego (held_balance)
            game.held_balance += total_cost
            
            # Actualizar estadísticas del juego
            game.total_cards_sold += quantity
            game.save()
            
            # Verificar premio progresivo
            prize_increase = game.check_progressive_prize()
            
            response_data = {
                'success': True,
                'new_balance': float(request.user.credit_balance),
                'player_cards_count': len(player.cards),
                'new_cards': new_cards,
                'prize_increased': prize_increase > 0,
                'new_prize': float(game.prize),
                'increase_amount': float(prize_increase) if prize_increase > 0 else 0,
                'total_cards_sold': game.total_cards_sold,
                'max_cards_sold': game.max_cards_sold,
                'next_prize_target': game.next_prize_target,
                'progress_percentage': game.progress_percentage
            }
            
            # Notificar a otros jugadores via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'game_{game.id}',
                {
                    'type': 'card_purchased',
                    'user': request.user.username,
                    'new_cards': new_cards,
                    'prize_increased': prize_increase > 0,
                    'sound_type': 'credit_purchase',
                    'new_prize': float(game.prize),
                    'increase_amount': float(prize_increase) if prize_increase > 0 else 0,
                    'total_cards_sold': game.total_cards_sold,
                    'max_cards_sold': game.max_cards_sold,
                    'next_prize_target': game.next_prize_target,
                    'progress_percentage': game.progress_percentage
                }
            )
            
            return JsonResponse(response_data)
            
    except Exception as e:
        logger.error(f"Error en compra de cartón: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error en la transacción: {str(e)}'
        }, status=500)
    
@login_required
@require_http_methods(["POST"])
def start_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    if request.user != game.organizer:
        return JsonResponse({
            'success': False, 
            'error': 'Solo el organizador puede iniciar el juego'
        })
    
    if game.is_started:
        return JsonResponse({
            'success': False, 
            'error': 'El juego ya ha comenzado'
        })
    
    if game.is_finished:
        return JsonResponse({
            'success': False, 
            'error': 'El juego ya ha terminado'
        })
    
    with transaction.atomic():
        game.refresh_from_db()
        if game.total_cards_sold > game.max_cards_sold:
            game.max_cards_sold = game.total_cards_sold
            game.save()
    
        if game.start_game():
            return JsonResponse({
                'success': True,
                'max_cards_sold': game.max_cards_sold,
                'total_cards_sold': game.total_cards_sold
            })
        else:
            return JsonResponse({
                'success': False, 
                'error': 'No se pudo iniciar el juego'
            })

@login_required
@require_http_methods(["POST"])
def toggle_auto_call(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    if request.user != game.organizer:
        return JsonResponse({
            'success': False, 
            'error': 'Solo el organizador puede controlar la llamada automática'
        })
    
    if not game.is_started or game.is_finished:
        return JsonResponse({
            'success': False, 
            'error': 'El juego no está en progreso'
        })
    
    if game.is_auto_calling:
        game.stop_auto_calling()
        return JsonResponse({
            'success': True, 
            'is_auto_calling': False, 
            'message': 'Llamada automática detenida'
        })
    else:
        game.start_auto_calling()
        return JsonResponse({
            'success': True, 
            'is_auto_calling': True, 
            'message': 'Llamada automática iniciada'
        })


@login_required
@require_POST
def toggle_player_marking(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # Validar estado del juego
    if game.is_finished:
        return JsonResponse({'success': False, 'error': 'El juego ya terminó'}, status=400)
    if not game.is_started:
        return JsonResponse({'success': False, 'error': 'El juego aún no ha comenzado'}, status=400)
    
    try:
        player = Player.objects.get(game=game, user=request.user)
    except Player.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No formas parte de este juego.'
        }, status=400)

    player.is_manual_marking = not player.is_manual_marking
    if not player.is_manual_marking:
        player.marked_numbers = []

    player.save(update_fields=['is_manual_marking', 'marked_numbers'])

    bingo_detected = False
    if not player.is_manual_marking:
        try:
            if player.check_bingo():
                bingo_detected = _finalize_player_win(player)
        except Exception as e:
            logger.error(f'Error comprobando bingo tras cambiar a modo automático: {e}', exc_info=True)

    return JsonResponse({
        'success': True,
        'is_manual_marking': player.is_manual_marking,
        'message': 'Modo manual activado' if player.is_manual_marking else 'Modo automático activado',
        'has_bingo': bingo_detected
    })


@login_required
@require_POST
def update_marked_numbers(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # Validar estado del juego
    if game.is_finished:
        return JsonResponse({'success': False, 'error': 'El juego ya terminó'}, status=400)
    if not game.is_started:
        return JsonResponse({'success': False, 'error': 'El juego aún no ha comenzado'}, status=400)
    
    try:
        player = Player.objects.get(game=game, user=request.user)
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No participas en este juego'}, status=400)

    try:
        payload = json.loads(request.body or '{}')
        numbers = payload.get('marked_numbers', [])
        if not isinstance(numbers, list):
            raise ValueError('Formato inválido')
        sanitized = []
        for value in numbers:
            num = int(value)
            if num < 0 or num > 90:
                continue
            sanitized.append(num)
        player.marked_numbers = sanitized
        player.save(update_fields=['marked_numbers'])

        bingo_detected = False
        if player.check_bingo():
            bingo_detected = _finalize_player_win(player)

        return JsonResponse({
            'success': True,
            'marked_numbers': player.marked_numbers,
            'has_bingo': bingo_detected
        })
    except Exception as e:
        logger.error(f'Error actualizando números marcados: {e}', exc_info=True)
        return JsonResponse({'success': False, 'error': 'No se pudieron actualizar los números'}, status=400)


@login_required
@require_POST
def mark_number(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # Validar estado del juego
    if game.is_finished:
        return JsonResponse({'success': False, 'error': 'El juego ya terminó'}, status=400)
    if not game.is_started:
        return JsonResponse({'success': False, 'error': 'El juego aún no ha comenzado'}, status=400)
    
    try:
        player = Player.objects.get(game=game, user=request.user)
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No participas en este juego'}, status=400)

    if not player.is_manual_marking:
        return JsonResponse({'success': False, 'error': 'Debes estar en modo manual para marcar números'}, status=400)

    try:
        data = json.loads(request.body or '{}')
        number = int(data.get('number'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Número inválido'}, status=400)

    if number == 0:
        return JsonResponse({'success': False, 'error': 'La casilla libre ya está marcada automáticamente'}, status=400)

    if number not in game.called_numbers:
        return JsonResponse({'success': False, 'error': 'Solo puedes marcar números ya llamados'}, status=400)

    # Verificar que el número esté en alguno de los cartones del jugador
    if not any(number in row for card in player.cards for row in card):
        return JsonResponse({'success': False, 'error': 'Este número no pertenece a tus cartones'}, status=400)

    marked = set(player.marked_numbers or [])
    if number in marked:
        marked.remove(number)
        action = 'desmarcado'
    else:
        marked.add(number)
        action = 'marcado'

    player.marked_numbers = list(marked)
    player.save(update_fields=['marked_numbers'])

    bingo_detected = False
    if player.check_bingo():
        bingo_detected = _finalize_player_win(player)

    return JsonResponse({
        'success': True,
        'action': action,
        'marked_numbers': player.marked_numbers,
        'has_bingo': bingo_detected
    })

@login_required
def message_list_api(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id parameter is required'}, status=400)
    
    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('timestamp')
    
    messages_data = [{
        'id': msg.id,
        'sender': {
            'id': msg.sender.id,
            'username': msg.sender.username,
            'is_admin': msg.sender.is_admin,
            'is_organizer': msg.sender.is_organizer
        },
        'content': msg.content,
        'timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        'is_read': msg.is_read
    } for msg in messages]
    
    return JsonResponse({'messages': messages_data})

@login_required
@require_http_methods(["POST"])
def send_message_api(request):
    try:
        data = json.loads(request.body)
        recipient = User.objects.get(id=data.get('recipient_id'))
        
        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=data.get('content', '')
        )

        # --- INICIO DE LA CORRECCIÓN ---
        # Notificar al destinatario en tiempo real
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{recipient.id}',
                {
                    'type': 'new_message',
                    'message': {
                        'id': message.id,
                        'sender': {
                            'id': message.sender.id,
                            'username': message.sender.username
                        }
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error sending message notification via WebSocket: {e}")
        # --- FIN DE LA CORRECCIÓN ---
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'sender': {
                    'id': message.sender.id,
                    'username': message.sender.username,
                    'is_admin': message.sender.is_admin,
                    'is_organizer': message.sender.is_organizer
                },
                'content': message.content,
                'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def unread_count_api(request):
    total_unread = Message.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'unread_count': total_unread})

@login_required
@require_http_methods(["POST"])
def mark_conversation_read_api(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id parameter is required'}, status=400)
    
    try:
        sender = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    Message.objects.filter(
        sender=sender,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    return JsonResponse({'status': 'success'})

@login_required
def messaging(request):
    # Get all users except current user
    all_users = User.objects.exclude(id=request.user.id)
    
    # Get existing conversations
    user_messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    )
    
    # Get user IDs with conversations
    user_ids_with_chats = set()
    for message in user_messages:
        if message.sender != request.user:
            user_ids_with_chats.add(message.sender.id)
        if message.recipient != request.user:
            user_ids_with_chats.add(message.recipient.id)
    
    # Separate users with and without conversations
    users_with_chats = User.objects.filter(id__in=user_ids_with_chats)
    users_without_chats = all_users.exclude(id__in=user_ids_with_chats)
    
    # Prepare conversation data
    conversations = []
    for user in users_with_chats:
        last_message = Message.objects.filter(
            Q(sender=request.user, recipient=user) |
            Q(sender=user, recipient=request.user)
        ).order_by('-timestamp').first()
        
        unread_count = Message.objects.filter(
            sender=user,
            recipient=request.user,
            is_read=False
        ).count()
        
        conversations.append({
            'other_user': user,
            'last_message': last_message.content if last_message else '',
            'unread_count': unread_count,
            'last_message_time': last_message.timestamp if last_message else None
        })
    
    # Sort conversations by last message
    conversations.sort(key=lambda x: x['last_message_time'] or datetime.min, reverse=True)
    
    return render(request, 'bingo_app/messaging.html', {
        'conversations': conversations,
        'users_without_chats': users_without_chats
    })

@login_required
def create_raffle(request):
    if not request.user.is_organizer:
        return redirect('lobby')
    
    if request.method == 'POST':
        form = RaffleForm(request.POST)
        if form.is_valid():
            raffle = form.save(commit=False)
            
            # Verificar que el organizador tenga suficiente saldo para el premio
            # Calculate total prize amount
            total_prize_amount = raffle.prize
            if raffle.multiple_winners_enabled and raffle.prize_structure:
                # Sum all prizes in the structure
                total_prize_amount = sum(Decimal(str(p.get('prize', 0))) for p in raffle.prize_structure)
            
            if request.user.credit_balance < total_prize_amount:
                messages.error(request, f'Saldo insuficiente. Necesitas {total_prize_amount} créditos para establecer los premios')
                return render(request, 'bingo_app/create_raffle.html', {'form': form})
            
            try:
                with transaction.atomic():
                    # Descontar el total de premios del saldo del organizador
                    request.user.credit_balance -= total_prize_amount
                    # Bloquear el total de premios en blocked_credits
                    request.user.blocked_credits += total_prize_amount
                    request.user.save()
                    
                    # Crear la rifa
                    raffle.organizer = request.user
                    # Asignar la franquicia del organizador a la rifa
                    franchise = getattr(request, 'franchise', None)
                    if franchise:
                        raffle.franchise = franchise
                    raffle.save()

                    # Notify lobby
                    channel_layer = get_channel_layer()
                    html = render_to_string('bingo_app/partials/raffle_card.html', {'raffle': raffle})
                    async_to_sync(channel_layer.group_send)(
                        'lobby',
                        {
                            'type': 'new_raffle_created',
                            'html': html
                        }
                    )
                    html_raffle_lobby = render_to_string('bingo_app/partials/raffle_card_lobby.html', {'raffle': raffle})
                    async_to_sync(channel_layer.group_send)(
                        'raffle_lobby',
                        {
                            'type': 'new_raffle_created',
                            'html': html_raffle_lobby
                        }
                    )
                    
                    # Registrar la transacción
                    Transaction.objects.create(
                        user=request.user,
                        amount=-total_prize_amount,
                        transaction_type='PURCHASE',
                        description=f"Premios para rifa {raffle.title} ({len(raffle.prize_structure) if raffle.multiple_winners_enabled else 1} ganador{'es' if raffle.multiple_winners_enabled and len(raffle.prize_structure) > 1 else ''})",
                        related_game=None
                    )
                    
                    messages.success(request, '¡Rifa creada exitosamente!')
                    return redirect('raffle_detail', raffle_id=raffle.id)
                    
            except Exception as e:
                messages.error(request, f'Error al crear la rifa: {str(e)}')
    else:
        form = RaffleForm()
    
    return render(request, 'bingo_app/create_raffle.html', {
        'form': form,
        'current_balance': request.user.credit_balance
    })

@login_required
def raffle_lobby(request):
    # Obtener la franquicia del usuario (si tiene)
    franchise = getattr(request, 'franchise', None)
    
    # Filtrar rifas por franquicia
    if franchise:
        active_raffles = Raffle.objects.filter(status__in=['WAITING', 'IN_PROGRESS'], franchise=franchise)
        finished_raffles = Raffle.objects.filter(status='FINISHED', franchise=franchise)[:5]
    elif request.user.is_superuser or request.user.is_admin:
        # Super admin puede ver todo
        active_raffles = Raffle.objects.filter(status__in=['WAITING', 'IN_PROGRESS'])
        finished_raffles = Raffle.objects.filter(status='FINISHED')[:5]
    else:
        # Usuario sin franquicia solo ve rifas sin franquicia asignada
        active_raffles = Raffle.objects.filter(status__in=['WAITING', 'IN_PROGRESS'], franchise__isnull=True)
        finished_raffles = Raffle.objects.filter(status='FINISHED', franchise__isnull=True)[:5]
    
    announcements = Announcement.objects.filter(is_active=True).order_by('order')

    unread_count = 0
    if request.user.is_authenticated:
        unread_count = request.user.credit_notifications.filter(is_read=False).count()
    
    return render(request, 'bingo_app/raffle_lobby.html', {
        'active_raffles': active_raffles,
        'finished_raffles': finished_raffles,
        'announcements': announcements,
    })

@login_required
def raffle_detail(request, raffle_id):
    raffle = get_object_or_404(Raffle, id=raffle_id)
    percentage_settings = PercentageSettings.objects.first()
    
    # Preparar datos de tickets
    tickets_dict = {t.number: t for t in raffle.tickets.select_related('owner')}
    user_tickets = raffle.tickets.filter(owner=request.user)
    available_numbers = list(range(raffle.start_number, raffle.end_number + 1))
    sold_numbers = list(tickets_dict.keys())
    
    # Manejar compra de tickets
    if request.method == 'POST' and raffle.status == 'WAITING':
        form = BuyTicketForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data['number']
            
            if number not in available_numbers:
                messages.error(request, 'Número fuera de rango')
            elif number in sold_numbers:
                messages.error(request, 'Este número ya está comprado')
            elif request.user.credit_balance < raffle.ticket_price:
                messages.error(request, 'Saldo insuficiente')
            else:
                try:
                    with transaction.atomic():
                        # Crear ticket
                        Ticket.objects.create(
                            raffle=raffle,
                            number=number,
                            owner=request.user
                        )
                        
                        # Descontar créditos
                        request.user.credit_balance -= raffle.ticket_price
                        request.user.save()
                        
                        # Registrar transacción
                        Transaction.objects.create(
                            user=request.user,
                            amount=-raffle.ticket_price,
                            transaction_type='PURCHASE',
                            description=f"Ticket #{number} para rifa: {raffle.title}",
                            related_game=None
                        )
                        
                        channel_layer = get_channel_layer()
                        sold_count = raffle.tickets.count()
                        progress_percentage = (sold_count / raffle.total_tickets) * 100 if raffle.total_tickets else 0
                        buyer_username = request.user.username

                        transaction.on_commit(lambda channel_layer=channel_layer, raffle_id=raffle.id, number=number, buyer=buyer_username, progress=progress_percentage, sold_count=sold_count: async_to_sync(channel_layer.group_send)(
                            f"raffle_{raffle_id}",
                            {
                                'type': 'ticket_purchased',
                                'number': number,
                                'numbers': [number],
                                'buyer': buyer,
                                'progress_percentage': progress,
                                'total_tickets_sold': sold_count
                            }
                        ))

                        
                        messages.success(request, f'¡Has comprado el ticket #{number}!')
                        
                        # Verificar si la rifa debe cambiar de estado
                        check_raffle_progress(raffle)
                        
                except Exception as e:
                    messages.error(request, f'Error al comprar ticket: {str(e)}')
            
            return redirect('raffle_detail', raffle_id=raffle.id)
    else:
        form = BuyTicketForm()
    
    # Handle raffle draw (organizer only)
    if request.method == 'POST' and 'draw_raffle' in request.POST and request.user == raffle.organizer:
        if raffle.status != 'WAITING' and raffle.status != 'IN_PROGRESS':
            messages.error(request, 'Esta rifa ya ha sido sorteada')
        elif not tickets_dict:
            messages.error(request, 'No hay tickets vendidos para sortear')
        else:
            try:
                with transaction.atomic():
                    # Seleccionar ganador aleatorio
                    winning_number = random.choice(list(tickets_dict.keys()))
                    winner = tickets_dict[winning_number].owner
                    
                    # Actualizar rifa
                    raffle.winning_number = winning_number
                    raffle.winner = winner
                    raffle.status = 'FINISHED'
                    raffle.save()
                    
                    # Premiar al ganador
                    winner.credit_balance += raffle.prize
                    winner.save()

                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{winner.id}",
                        {
                            'type': 'win_notification',
                            'message': f"¡Felicidades! Ganaste {raffle.title}",
                        }
                    )

                    
                    Transaction.objects.create(
                        user=winner,
                        amount=raffle.prize,
                        transaction_type='PRIZE',
                        description=f"Premio de rifa: {raffle.title}",
                        related_game=None
                    )
                    
                    
                    messages.success(request, f'¡El ganador es {winner.username} con el ticket #{winning_number}!')
                    
            except Exception as e:
                messages.error(request, f'Error al realizar el sorteo: {str(e)}')
            
            return redirect('raffle_detail', raffle_id=raffle.id)
    
    # Get all video call groups for this raffle
    video_groups = VideoCallGroup.objects.filter(raffle=raffle)
    
    return render(request, 'bingo_app/raffle_detail.html', {
        'raffle': raffle,
        'user_tickets': user_tickets,
        'available_numbers': available_numbers,
        'sold_numbers': sold_numbers,
        'tickets_dict': tickets_dict,
        'form': form,
        'progress_percentage': (len(sold_numbers) / raffle.total_tickets) * 100,
        'video_groups': video_groups,
        'agora_app_id': settings.AGORA_APP_ID,
    })

@staff_member_required
def percentage_settings(request):
    settings, created = PercentageSettings.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        form = PercentageSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            settings = form.save(commit=False)
            settings.updated_by = request.user
            settings.save()
            messages.success(request, 'Porcentajes actualizados correctamente')
            return redirect('percentage_settings')
    else:
        form = PercentageSettingsForm(instance=settings)
    
    return render(request, 'bingo_app/admin/percentage_settings.html', {
        'form': form,
        'settings': settings
    })

@staff_member_required
def transaction_history(request, user_id=None):
    transactions = Transaction.objects.all()
    
    if user_id:
        transactions = transactions.filter(user__id=user_id)
    
    return render(request, 'bingo_app/admin/transaction_history.html', {
        'transactions': transactions.order_by('-created_at')
    })


def check_raffle_progress(raffle):
    """Verifica el progreso de la rifa y actualiza el estado si es necesario"""
    sold_count = raffle.tickets.count()
    if sold_count >= raffle.total_tickets * 0.5 and raffle.status == 'WAITING':
        raffle.status = 'IN_PROGRESS'
        raffle.save()


@login_required
def draw_raffle(request, raffle_id):
    raffle = get_object_or_404(Raffle, id=raffle_id)
    percentage_settings = PercentageSettings.objects.first()
    
    # Validaciones
    if request.user != raffle.organizer:
        messages.error(request, "Solo el organizador puede sortear")
        return redirect('raffle_detail', raffle_id=raffle.id)
    
    if raffle.status == 'FINISHED':
        messages.error(request, "Esta rifa ya terminó")
        return redirect('raffle_detail', raffle_id=raffle.id)
    
    if not raffle.tickets.exists():
        messages.error(request, "No hay tickets vendidos")
        return redirect('raffle_detail', raffle_id=raffle.id)
    
    try:
        with transaction.atomic():
            # 1. Seleccionar ganador con select_for_update para bloquear el registro
            winning_ticket = Ticket.objects.select_related('owner').select_for_update().get(
                id=random.choice([t.id for t in raffle.tickets.all()])
            )
            winner = winning_ticket.owner
            
            # 2. Calcular valores
            total_tickets_income = raffle.ticket_price * raffle.tickets.count()
            # El ganador recibe el 100% del premio
            player_prize = raffle.prize
            
            # 3. Actualizar saldo del ganador de forma segura
            winner.refresh_from_db()  # Asegurarnos de tener los datos más recientes
            winner.credit_balance += player_prize
            winner.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{winner.id}",
                {
                    'type': 'win_notification',
                    'message': f"¡Felicidades! Ganaste {raffle.title}",
                }
            )

            
            # Registrar transacción
            Transaction.objects.create(
                user=winner,
                amount=player_prize,
                transaction_type='PRIZE',
                description=f"Premio completo de {raffle.title} ({raffle.prize} créditos)",
                related_game=None
            )
            
            # 4. Distribución al organizador
            # El organizador recibe los ingresos de tickets (después de la comisión si está habilitada)
            if percentage_settings.platform_commission_enabled:
                commission_rate = percentage_settings.platform_commission / 100
                commission = total_tickets_income * Decimal(commission_rate)
                organizer_total = total_tickets_income - commission
            else:
                organizer_total = total_tickets_income
            
            raffle.organizer.refresh_from_db()
            raffle.organizer.credit_balance += organizer_total
            raffle.organizer.save()
            
            Transaction.objects.create(
                user=raffle.organizer,
                amount=organizer_total,
                transaction_type='RAFFLE_INCOME',
                description=f"Ingresos de tickets de {raffle.title}",
                related_game=None
            )
            
            # 5. Distribución al admin (solo si hay comisión)
            admin = User.objects.filter(is_admin=True).first()
            if admin and percentage_settings.platform_commission_enabled:
                commission_rate = percentage_settings.platform_commission / 100
                admin_commission = total_tickets_income * Decimal(commission_rate)
                
                admin.refresh_from_db()
                admin.credit_balance += admin_commission
                admin.save()
                
                Transaction.objects.create(
                    user=admin,
                    amount=admin_commission,
                    transaction_type='ADMIN_ADD',
                    description=f"Comisión de plataforma de {raffle.title} ({percentage_settings.platform_commission}%)",
                    related_game=None
                )
            
            # 6. Actualizar rifa
            raffle.winning_number = winning_ticket.number
            raffle.winner = winner
            raffle.status = 'FINISHED'
            raffle.final_prize = player_prize
            raffle.tickets_income = total_tickets_income
            raffle.save()

            request.session['show_win_notification'] = {
                    'message': f"¡GANASTE LA RIFA! Premio: {raffle.prize} créditos",
                    'prize': float(raffle.prize),
                    'game': raffle.title
                }
            messages.success(request, 
                f'¡Sorteo completado! Ganador: {winner.username} '
                f'con ticket #{winning_ticket.number}. '
                f'Premio: {player_prize} créditos. '
                f'Saldo actual del ganador: {winner.credit_balance} créditos.'
            )

            return redirect('raffle_detail', raffle_id=raffle.id)
            
    except Exception as e:
        messages.error(request, f'Error en sorteo: {str(e)}')
        logger.error(f"Error en draw_raffle: {str(e)}", exc_info=True)
    
    return redirect('raffle_detail', raffle_id=raffle.id)


@login_required
def request_withdrawal(request):
    # Verificar si el sistema de retiro de créditos está habilitado
    settings_obj = PercentageSettings.objects.first()
    if not settings_obj or not settings_obj.credits_withdrawal_enabled:
        messages.error(request, 'El sistema de retiro de créditos está temporalmente deshabilitado.')
        return redirect('profile')
    
    if request.method == 'POST':
        form = UserWithdrawalRequestForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            if request.user.credit_balance < amount:
                messages.error(request, 'Saldo insuficiente para este retiro')
                return render(request, 'bingo_app/request_withdrawal.html', {'form': form})
            
            try:
                with transaction.atomic():
                    withdrawal = form.save(commit=False)
                    withdrawal.user = request.user
                    withdrawal.status = 'PENDING'
                    # Asignar la franquicia del usuario a la solicitud
                    franchise = getattr(request, 'franchise', None)
                    if franchise:
                        withdrawal.franchise = franchise
                    withdrawal.save()

                    # --- INICIO DE LA CORRECCIÓN ---
                    # 1. Crear notificaciones en la base de datos
                    # Si la solicitud pertenece a una franquicia, notificar al propietario de la franquicia
                    # Si no, notificar a los superusuarios
                    if withdrawal.franchise and withdrawal.franchise.owner:
                        # Notificar al propietario de la franquicia
                        franchise_owner = withdrawal.franchise.owner
                        WithdrawalRequestNotification.objects.create(
                            user=franchise_owner,
                            withdrawal_request=withdrawal
                        )
                        notification_url = reverse('franchise_owner_withdrawal_requests')
                        logger.info(f"DEBUG: Notificación para propietario de franquicia: {franchise_owner.username}")
                    else:
                        # Notificar a superusuarios (solicitudes sin franquicia)
                        admins_and_organizers = User.objects.filter(is_superuser=True)
                        for user in admins_and_organizers:
                            WithdrawalRequestNotification.objects.create(
                                user=user,
                                withdrawal_request=withdrawal
                            )
                        notification_url = reverse('withdrawal_requests')
                        logger.info("DEBUG: Notificación para superusuarios")

                    # 2. Notificar a los administradores via WebSocket
                    try:
                        logger.info(f"DEBUG: Intentando enviar admin_notification para solicitud de retiro de {withdrawal.user.username}")
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            'admin_notifications',
                            {
                                'type': 'admin_notification',
                                'notification_type': 'new_withdrawal_request',
                                'message': f'Nueva solicitud de retiro de {withdrawal.user.username} por ${withdrawal.amount}.',
                                'url': notification_url,
                                'sound_type': 'withdrawal_request'
                            }
                        )
                        logger.info("DEBUG: admin_notification para solicitud de retiro enviada al channel layer.")
                    except Exception as e:
                        logger.error(f"Error sending WebSocket notification: {e}")
                    # --- FIN DE LA CORRECCIÓN ---
                    
                    # NO descontar créditos aquí - se descontarán solo cuando se apruebe
                    
                    messages.success(request, 'Solicitud de retiro enviada. Los créditos se descontarán cuando sea aprobada.')
                    return redirect('profile')
                    
            except Exception as e:
                messages.error(request, f'Error al procesar la solicitud: {str(e)}')
    else:
        form = UserWithdrawalRequestForm(initial={
            'account_holder_name': request.user.get_full_name() or request.user.username
        })
    
    return render(request, 'bingo_app/request_withdrawal.html', {
        'form': form,
        'current_balance': request.user.credit_balance
    })

@staff_member_required
def withdrawal_requests(request):
    requests = WithdrawalRequest.objects.filter(status='PENDING').order_by('created_at')
    return render(request, 'bingo_app/admin/withdrawal_requests.html', {
        'requests': requests,
        'section': 'pending'
    })

@staff_member_required
def all_withdrawal_requests(request):
    requests = WithdrawalRequest.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status')
    
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    return render(request, 'bingo_app/admin/withdrawal_requests.html', {
        'requests': requests,
        'section': 'all'
    })

@staff_member_required
def process_withdrawal(request, request_id):
    withdrawal = get_object_or_404(WithdrawalRequest, id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('admin_notes', '')
        
        try:
            with transaction.atomic():
                if action == 'approve':
                    # Verificar que el usuario tenga suficientes créditos
                    if withdrawal.user.credit_balance < withdrawal.amount:
                        messages.error(request, 'El usuario no tiene suficientes créditos para este retiro.')
                        return redirect('process_withdrawal', request_id=request_id)
                    
                    # Descontar los créditos del usuario
                    withdrawal.user.credit_balance -= withdrawal.amount
                    withdrawal.user.save()
                    
                    # Crear transacción de retiro
                    Transaction.objects.create(
                        user=withdrawal.user,
                        amount=-withdrawal.amount,
                        transaction_type='WITHDRAWAL',
                        description=f"Retiro aprobado #{withdrawal.id}",
                        related_game=None
                    )
                    
                    # Marcar como aprobado (el admin debe hacer la transferencia manualmente)
                    withdrawal.status = 'APPROVED'
                    withdrawal.admin_notes = notes
                    withdrawal.save()
                    
                    # Enviar notificación al usuario
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{withdrawal.user.id}",
                        {
                            'type': 'withdrawal_approved_notification',
                            'amount': float(withdrawal.amount),
                            'message': f'¡Retiro aprobado! Se procesará la transferencia de ${withdrawal.amount}.'
                        }
                    )
                    
                    messages.success(request, 'Retiro aprobado y créditos descontados. Ahora puedes proceder con la transferencia bancaria.')
                
                elif action == 'complete':
                    # Marcar como completado (después de hacer la transferencia)
                    withdrawal.status = 'COMPLETED'
                    withdrawal.transaction_reference = request.POST.get('transaction_reference', '')
                    withdrawal.admin_notes = notes
                    withdrawal.save()
                    
                    # Enviar notificación al usuario
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{withdrawal.user.id}",
                        {
                            'type': 'withdrawal_completed_notification',
                            'amount': float(withdrawal.amount),
                            'message': f'¡Retiro completado! Se ha transferido ${withdrawal.amount} a tu cuenta bancaria.'
                        }
                    )
                    
                    messages.success(request, 'Retiro marcado como completado.')
                
                elif action == 'reject':
                    # Rechazar solicitud, devolver créditos y revertir la transacción
                    withdrawal.status = 'REJECTED'
                    withdrawal.admin_notes = notes
                    withdrawal.save()
                    
                    # Devolver los créditos al usuario
                    withdrawal.user.credit_balance += withdrawal.amount
                    withdrawal.user.save()
                    
                    # Crear transacción de reversión para cancelar el retiro en el dashboard
                    Transaction.objects.create(
                        user=withdrawal.user,
                        amount=withdrawal.amount,  # Positivo para cancelar la salida negativa
                        transaction_type='WITHDRAWAL_REFUND',
                        description=f"Rechazo de retiro #{withdrawal.id}",
                        related_game=None
                    )
                    
                    # Enviar notificación al usuario
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"user_{withdrawal.user.id}",
                        {
                            'type': 'withdrawal_rejected_notification',
                            'amount': float(withdrawal.amount),
                            'message': f'Retiro rechazado por ${withdrawal.amount}. Los créditos han sido devueltos a tu cuenta.'
                        }
                    )
                    
                    messages.success(request, 'Solicitud de retiro rechazada, créditos devueltos y transacción revertida.')
                
                return redirect('withdrawal_requests')
                
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
    
    return render(request, 'bingo_app/admin/process_withdrawal.html', {
        'withdrawal': withdrawal
    })

@login_required
@require_http_methods(["POST"])
def call_number(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    if request.user != game.organizer:
        return JsonResponse({'success': False, 'error': 'Solo el organizador puede llamar números'}, status=403)
    
    try:
        data = json.loads(request.body)
        number = int(data['number'])
        
        if number < 1 or number > 90:
            return JsonResponse({'success': False, 'error': 'Número fuera de rango'}, status=400)
            
        if number in game.called_numbers:
            return JsonResponse({'success': False, 'error': 'Número ya llamado'}, status=400)
            
        game.current_number = number
        game.called_numbers.append(number)
        game.save()
        
        # Verificar si algún jugador ha ganado - buscar TODOS los ganadores
        winners = []
        for player in game.player_set.all():
            if player.check_bingo():
                winners.append(player.user)
        
        # Notificar via WebSocket
        channel_layer = get_channel_layer()
        winner = winners[0] if winners else None
        async_to_sync(channel_layer.group_send)(
            f'game_{game.id}',
            {
                'type': 'number_called',
                'number': number,
                'called_numbers': game.called_numbers,
                'is_manual': True,
                'has_winner': winner is not None,
                'winner': winner.username if winner else None
            }
        )
        
        # Si hay ganadores, finalizar el juego (esto activará la distribución de premios entre TODOS los ganadores)
        if winners:
            winners_usernames = [w.username for w in winners]
            print(f"Ganadores detectados: {', '.join(winners_usernames)}")
            try:
                with transaction.atomic():
                    success = game.end_game_manual(winners)
                    if not success:
                        print("Error en end_game")
                        return JsonResponse({
                            'success': False, 
                            'error': 'Error al distribuir premios',
                            'has_winner': True
                        }, status=500)
                    
                    # Verificar distribución (refrescar todos los ganadores)
                    for w in winners:
                        w.refresh_from_db()
                        print(f"Nuevo balance de {w.username}: {w.credit_balance}")
                    
                    return JsonResponse({
                        'success': True,
                        'has_winner': True,
                        'winner': winner.username,
                        'winners': winners_usernames,
                        'num_winners': len(winners),
                        'new_balance': float(winner.credit_balance)
                    })
            except Exception as e:
                print(f"Error en transacción: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': str(e),
                    'has_winner': True
                }, status=500)
        
        return JsonResponse({
            'success': True, 
            'has_winner': False
        })
        
    except Exception as e:
        print(f"Error general: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@staff_member_required
def payment_methods_list(request):
    methods = BankAccount.objects.all().order_by('-order', 'title')
    return render(request, 'bingo_app/admin/payment_methods/list.html', {
        'payment_methods': methods
    })

@staff_member_required
def create_payment_method(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Método de pago creado exitosamente')
            return redirect('payment_methods_list')
    else:
        form = PaymentMethodForm()
    
    return render(request, 'bingo_app/admin/payment_methods/create.html', {
        'form': form,
        'title': 'Crear nuevo método de pago'
    })

@staff_member_required
def edit_payment_method(request, method_id):
    method = get_object_or_404(BankAccount, id=method_id)
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=method)
        if form.is_valid():
            form.save()
            messages.success(request, 'Método de pago actualizado')
            return redirect('payment_methods_list')
    else:
        form = PaymentMethodForm(instance=method)
    
    return render(request, 'bingo_app/admin/payment_methods/create.html', {
        'form': form,
        'title': f'Editar {method.title}'
    })

@staff_member_required
def delete_payment_method(request, method_id):
    method = get_object_or_404(BankAccount, id=method_id)
    if request.method == 'POST':
        method.delete()
        messages.success(request, 'Método de pago eliminado')
    return redirect('payment_methods_list')

@staff_member_required
def toggle_payment_method(request, method_id):
    method = get_object_or_404(BankAccount, id=method_id)
    method.is_active = not method.is_active
    method.save()
    messages.success(request, f'Método {"activado" if method.is_active else "desactivado"}')
    return redirect('payment_methods_list')


# views.py
@login_required
def notifications(request):

    request.user.credit_notifications.filter(is_read=False).update(is_read=True)

    unread_notifications = request.user.credit_notifications.filter(is_read=False)
    read_notifications = request.user.credit_notifications.filter(is_read=True)[:10]
    
    return render(request, 'bingo_app/notifications.html', {
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications
    })

# views.py
@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(CreditRequestNotification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('process_request', notification.credit_request.id)


@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(
        CreditRequestNotification,
        id=notification_id,
        user=request.user
    )
    notification.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'remaining': request.user.credit_notifications.count()})
    
    return redirect('notifications')

# En views.py, añade estas nuevas vistas

@staff_member_required
def block_user(request, user_id):
    user_to_block = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        block_type = request.POST.get('block_type')
        reason = request.POST.get('reason', '')
        duration = request.POST.get('duration')
        
        try:
            with transaction.atomic():
                blocked_until = None
                if duration and duration != 'permanent':
                    days = int(duration)
                    blocked_until = timezone.now() + timezone.timedelta(days=days)
                
                user_to_block.is_blocked = True
                user_to_block.block_reason = reason
                user_to_block.blocked_until = blocked_until
                user_to_block.blocked_at = timezone.now()
                user_to_block.blocked_by = request.user
                user_to_block.save()
                
                UserBlockHistory.objects.create(
                    user=user_to_block,
                    blocked_by=request.user,
                    block_type=block_type,
                    reason=reason,
                    blocked_until=blocked_until
                )
                
                messages.success(request, f'Usuario {user_to_block.username} bloqueado exitosamente')
                return redirect('user_management')
                
        except Exception as e:
            messages.error(request, f'Error al bloquear usuario: {str(e)}')
    
    return render(request, 'bingo_app/admin/block_user.html', {
        'user': user_to_block
    })

@staff_member_required
def unblock_user(request, user_id):
    user_to_unblock = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                user_to_unblock.is_blocked = False
                user_to_unblock.block_reason = ''
                user_to_unblock.blocked_until = None
                user_to_unblock.save()
                
                UserBlockHistory.objects.filter(
                    user=user_to_unblock,
                    is_active=True
                ).update(is_active=False)
                
                messages.success(request, f'Usuario {user_to_unblock.username} desbloqueado exitosamente')
                return redirect('user_management')
                
        except Exception as e:
            messages.error(request, f'Error al desbloquear usuario: {str(e)}')
    
    return render(request, 'bingo_app/admin/unblock_user.html', {
        'user': user_to_unblock
    })

@staff_member_required
def user_management(request):
    users = User.objects.all().order_by('-date_joined')
    blocked_users = User.objects.filter(is_blocked=True)
    
    return render(request, 'bingo_app/admin/user_management.html', {
        'users': users,
        'blocked_users': blocked_users
    })

@login_required
@require_http_methods(["POST"])
def mark_as_read(request):
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        notification_type = data.get('notification_type')

        if not notification_id or not notification_type:
            return JsonResponse({'status': 'error', 'message': 'ID or type missing'}, status=400)

        redirect_url = None

        if notification_type == 'message':
            notification = get_object_or_404(Message, id=notification_id, recipient=request.user)
            notification.is_read = True
            notification.save()
            redirect_url = reverse('messaging') + f'?user_id={notification.sender.id}'
        
        elif notification_type == 'credit_request_notification':
            notification = get_object_or_404(CreditRequestNotification, id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            # Verificar si el usuario es propietario de una franquicia
            if hasattr(request.user, 'owned_franchise') and request.user.owned_franchise:
                redirect_url = reverse('franchise_owner_credit_requests')
            else:
                redirect_url = reverse('credit_requests_list')

        elif notification_type == 'withdrawal_request_notification':
            notification = get_object_or_404(WithdrawalRequestNotification, id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            # Verificar si el usuario es propietario de una franquicia
            if hasattr(request.user, 'owned_franchise') and request.user.owned_franchise:
                redirect_url = reverse('franchise_owner_withdrawal_requests')
            else:
                redirect_url = reverse('withdrawal_requests')
        
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid notification type'}, status=400)

        return JsonResponse({'status': 'success', 'redirect_url': redirect_url})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def buy_multiple_tickets(request, raffle_id):
    raffle = get_object_or_404(Raffle, id=raffle_id)

    if raffle.status not in ['WAITING', 'IN_PROGRESS']:
        return JsonResponse({'success': False, 'error': 'Esta rifa no está activa.'})

    try:
        data = json.loads(request.body)
        numbers_to_buy = data.get('numbers', [])
        if not isinstance(numbers_to_buy, list) or not numbers_to_buy:
            return JsonResponse({'success': False, 'error': 'No se seleccionaron números.'})
        
        numbers_to_buy = [int(n) for n in numbers_to_buy]

    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Solicitud inválida.'}, status=400)

    sold_numbers = set(raffle.tickets.values_list('number', flat=True))
    errors = []
    for number in numbers_to_buy:
        if not (raffle.start_number <= number <= raffle.end_number):
            errors.append(f'El número {number} está fuera de rango.')
        if number in sold_numbers:
            errors.append(f'El número {number} ya fue vendido.')
    
    if errors:
        return JsonResponse({'success': False, 'error': ' '.join(errors)})

    total_cost = raffle.ticket_price * len(numbers_to_buy)
    if request.user.credit_balance < total_cost:
        return JsonResponse({'success': False, 'error': f'Saldo insuficiente. Necesitas {total_cost} créditos.'})

    try:
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=request.user.pk)
            
            if user.credit_balance < total_cost:
                raise ValueError("Saldo insuficiente.")

            user.credit_balance -= total_cost
            user.save()

            for number in numbers_to_buy:
                Ticket.objects.create(
                    raffle=raffle,
                    number=number,
                    owner=user
                )
                Transaction.objects.create(
                    user=user,
                    amount=-raffle.ticket_price,
                    transaction_type='PURCHASE',
                    description=f"Ticket #{number} para rifa: {raffle.title}"
                )
            
            raffle.held_balance += total_cost
            raffle.save() # Save raffle to update held_balance

            check_raffle_progress(raffle)

            channel_layer = get_channel_layer()
            sold_count = raffle.tickets.count()
            progress_percentage = (sold_count / raffle.total_tickets) * 100 if raffle.total_tickets else 0
            buyer_username = user.username
            purchased_numbers = tuple(numbers_to_buy)

            def notify_raffle_purchase():
                async_to_sync(channel_layer.group_send)(
                    f"raffle_{raffle.id}",
                    {
                        'type': 'ticket_purchased',
                        'numbers': list(purchased_numbers),
                        'buyer': buyer_username,
                        'progress_percentage': progress_percentage,
                        'total_tickets_sold': sold_count
                    }
                )

            transaction.on_commit(notify_raffle_purchase)

        return JsonResponse({'success': True, 'tickets_bought': len(numbers_to_buy)})

    except ValueError as e:
         return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        logger.error(f"Error en compra múltiple de rifa: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Ocurrió un error inesperado al procesar la compra.'})

@login_required
def set_manual_raffle_winner(request, raffle_id):
    raffle = get_object_or_404(Raffle, id=raffle_id)

    if request.user != raffle.organizer:
        messages.error(request, "Solo el organizador puede establecer un ganador manual.")
        return redirect('raffle_detail', raffle_id=raffle.id)

    if raffle.status == 'FINISHED':
        messages.error(request, "Esta rifa ya ha terminado.")
        return redirect('raffle_detail', raffle_id=raffle.id)

    if request.method == 'POST':
        winning_number = request.POST.get('winning_number')
        if not winning_number:
            messages.error(request, "Debes proporcionar un número ganador.")
            return render(request, 'bingo_app/set_manual_raffle_winner.html', {'raffle': raffle})

        try:
            winning_number = int(winning_number)
            if not (raffle.start_number <= winning_number <= raffle.end_number):
                messages.error(request, f"El número ganador debe estar entre {raffle.start_number} y {raffle.end_number}.")
                return render(request, 'bingo_app/set_manual_raffle_winner.html', {'raffle': raffle})
        except ValueError:
            messages.error(request, "El número ganador debe ser un número válido.")
            return render(request, 'bingo_app/set_manual_raffle_winner.html', {'raffle': raffle})

        raffle.manual_winning_number = winning_number
        raffle.save()
        winning_ticket = raffle.draw_winner()

        if winning_ticket:
            messages.success(request, f"¡El ganador ha sido establecido! El ganador es {winning_ticket.owner.username} con el ticket #{winning_ticket.number}.")
        else:
            messages.error(request, f"No se pudo establecer el ganador. El ticket #{winning_number} no ha sido vendido.")
        
        return redirect('raffle_detail', raffle_id=raffle.id)

    return render(request, 'bingo_app/set_manual_raffle_winner.html', {'raffle': raffle})


@login_required
def set_manual_multiple_winners(request, raffle_id):
    raffle = get_object_or_404(Raffle, id=raffle_id)

    if request.user != raffle.organizer:
        messages.error(request, "Solo el organizador puede establecer ganadores manuales.")
        return redirect('raffle_detail', raffle_id=raffle.id)

    if raffle.status == 'FINISHED':
        messages.error(request, "Esta rifa ya ha terminado.")
        return redirect('raffle_detail', raffle_id=raffle.id)

    if not raffle.multiple_winners_enabled or not raffle.prize_structure:
        messages.error(request, "Esta rifa no tiene múltiples ganadores habilitados.")
        return redirect('raffle_detail', raffle_id=raffle.id)

    if request.method == 'POST':
        # Get winning numbers from form
        winning_numbers_json = request.POST.get('winning_numbers_json')
        if not winning_numbers_json:
            messages.error(request, "Debes proporcionar los números ganadores.")
            return render(request, 'bingo_app/set_manual_multiple_winners.html', {'raffle': raffle})

        try:
            winning_numbers = json.loads(winning_numbers_json)
            if not isinstance(winning_numbers, list):
                raise ValueError("Los números ganadores deben ser una lista")
            
            # Validate numbers
            sorted_prizes = sorted(raffle.prize_structure, key=lambda x: x.get('position', 0))
            if len(winning_numbers) < len(sorted_prizes):
                messages.error(request, f"Debes proporcionar al menos {len(sorted_prizes)} números ganadores.")
                return render(request, 'bingo_app/set_manual_multiple_winners.html', {'raffle': raffle})
            
            # Validate each number is in range
            for num in winning_numbers:
                try:
                    num_int = int(num)
                    if not (raffle.start_number <= num_int <= raffle.end_number):
                        messages.error(request, f"El número {num_int} debe estar entre {raffle.start_number} y {raffle.end_number}.")
                        return render(request, 'bingo_app/set_manual_multiple_winners.html', {'raffle': raffle})
                except ValueError:
                    messages.error(request, f"El número {num} no es válido.")
                    return render(request, 'bingo_app/set_manual_multiple_winners.html', {'raffle': raffle})
            
            # Store manual winning numbers
            raffle.manual_winning_numbers = winning_numbers[:len(sorted_prizes)]  # Only use as many as prizes
            raffle.save()
            
            # Draw winners using manual numbers
            winning_ticket = raffle.draw_winner()
            
            if winning_ticket or raffle.winners:
                messages.success(request, f"¡Los ganadores han sido establecidos correctamente!")
            else:
                messages.error(request, "No se pudieron establecer los ganadores. Verifica que todos los tickets hayan sido vendidos.")
            
            return redirect('raffle_detail', raffle_id=raffle.id)
            
        except json.JSONDecodeError:
            messages.error(request, "Formato de números ganadores inválido.")
        except Exception as e:
            messages.error(request, f"Error al establecer ganadores: {str(e)}")

    return render(request, 'bingo_app/set_manual_multiple_winners.html', {'raffle': raffle})


@staff_member_required
def manage_printable_cards(request):
    cards = PrintableCard.objects.all().order_by('-created_at')
    return render(request, 'bingo_app/admin/printable_cards_management.html', {'cards': cards})

@staff_member_required
def generate_printable_cards(request):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', '10'))
            if not (1 <= quantity <= 1000): # Basic validation
                messages.error(request, "La cantidad debe estar entre 1 y 1000.")
                return redirect('manage_printable_cards')

            new_cards = []
            for _ in range(quantity):
                card_data = generate_bingo_card() # Re-use the existing function
                unique_id = f"P-{uuid.uuid4().hex[:8].upper()}"
                new_cards.append(
                    PrintableCard(unique_id=unique_id, card_data=card_data)
                )
            
            PrintableCard.objects.bulk_create(new_cards)
            
            messages.success(request, f"Se generaron {quantity} nuevos cartones imprimibles.")
        except (ValueError, TypeError):
            messages.error(request, "Cantidad inválida.")
        
        return redirect('manage_printable_cards')
    
    # If GET request, just redirect to the management page
    return redirect('manage_printable_cards')

@staff_member_required
def assign_printable_card(request, card_id):
    card = get_object_or_404(PrintableCard, unique_id=card_id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            user = get_object_or_404(User, id=user_id)
            card.owner = user
            card.save()
            messages.success(request, f"El cartón {card.unique_id} ha sido asignado a {user.username}.")
        else:
            card.owner = None
            card.save()
            messages.success(request, f"El cartón {card.unique_id} ha sido desasignado.")
        return redirect('manage_printable_cards')

    users = User.objects.filter(is_staff=False, is_superuser=False).order_by('username')
    return render(request, 'bingo_app/admin/assign_card.html', {'card': card, 'users': users})

@login_required
def activate_printable_card(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    if not game.allows_printable_cards:
        messages.error(request, "Este juego no permite la activación de cartones imprimibles.")
        return redirect('game_room', game_id=game.id)

    if request.user != game.organizer:
        messages.error(request, "Solo el organizador puede activar cartones.")
        return redirect('game_room', game_id=game.id)

    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        user_id = request.POST.get('user_id')

        try:
            card = PrintableCard.objects.get(unique_id=card_id)
            user = User.objects.get(id=user_id)
            player, created = Player.objects.get_or_create(user=user, game=game)

            if card.owner != user:
                messages.error(request, f"El cartón {card_id} no pertenece a {user.username}.")
                return redirect('game_room', game_id=game.id)

            if len(player.cards) >= game.max_cards_per_player:
                messages.error(request, f"{user.username} ha alcanzado el límite de cartones.")
                return redirect('game_room', game_id=game.id)

            if user.credit_balance < game.card_price:
                messages.error(request, f"Saldo insuficiente para {user.username}.")
                return redirect('game_room', game_id=game.id)

            with transaction.atomic():
                # Get percentage settings for distribution
                percentage_settings = PercentageSettings.objects.first()
                if not percentage_settings:
                    messages.error(request, "Configuración del sistema no encontrada.")
                    return redirect('game_room', game_id=game.id)

                player.cards.append(card.card_data)
                player.save()

                # Charge for card
                user.credit_balance -= game.card_price
                user.save()

                # Record transaction
                Transaction.objects.create(
                    user=user,
                    amount=-game.card_price,
                    transaction_type='PURCHASE',
                    description=f"Activación de cartón imprimible {card.unique_id} en {game.name}",
                    related_game=game
                )

                # Distribute purchase (gives money to organizer and updates held_balance)
                distribute_purchase(game, game.card_price, percentage_settings)

                # Update game stats
                game.total_cards_sold += 1
                game.held_balance += game.card_price
                game.save()

                # Check for progressive prize and block credits if prize increases
                prize_increase = game.check_progressive_prize()
                
                # If prize increased, block additional credits from organizer
                if prize_increase > 0:
                    organizer = game.organizer
                    # Refresh organizer from DB to get latest balance
                    organizer.refresh_from_db()
                    
                    # Check if organizer has enough balance to block
                    if organizer.credit_balance >= prize_increase:
                        organizer.credit_balance -= prize_increase
                        organizer.blocked_credits += prize_increase
                        organizer.save()
                        
                        # Record transaction
                        Transaction.objects.create(
                            user=organizer,
                            amount=-prize_increase,
                            transaction_type='PRIZE_LOCK',
                            description=f"Bloqueo de premio progresivo (+{prize_increase}) en {game.name}",
                            related_game=game
                        )
                    else:
                        # If not enough balance, block what's available
                        available = organizer.credit_balance
                        if available > 0:
                            organizer.credit_balance = Decimal('0.00')
                            organizer.blocked_credits += available
                            organizer.save()
                            
                            Transaction.objects.create(
                                user=organizer,
                                amount=-available,
                                transaction_type='PRIZE_LOCK',
                                description=f"Bloqueo parcial de premio progresivo ({available} de {prize_increase}) en {game.name}",
                                related_game=game
                            )

                # Notify via channels
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'game_{game.id}',
                    {
                        'type': 'card_purchased',
                        'user': user.username,
                        'new_balance': float(user.credit_balance),
                        'player_cards_count': len(player.cards),
                        'new_cards': [card.card_data],
                        'nueva_tarjeta': [card.card_data], # Fix for deployment key error
                        'prize_increased': prize_increase > 0,
                        'new_prize': float(game.prize),
                        'total_cards_sold': game.total_cards_sold,
                        'next_prize_target': game.next_prize_target,
                        'progress_percentage': game.progress_percentage
                    }
                )

                messages.success(request, f"Cartón {card.unique_id} activado para {user.username}.")

        except PrintableCard.DoesNotExist:
            messages.error(request, f"El cartón con ID {card_id} no existe.")
        except User.DoesNotExist:
            messages.error(request, "El usuario seleccionado no existe.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return redirect('game_room', game_id=game.id)

from django.http import Http404

@login_required
def print_printable_card(request, card_id):
    card = get_object_or_404(PrintableCard, unique_id=card_id)
    
    # Ensure only the owner of the card or an admin can print it
    if card.owner != request.user and not request.user.is_staff:
        messages.error(request, "No tienes permiso para imprimir este cartón.")
        return redirect('lobby') # Or some other appropriate redirect

    context = {
        'card': card,
    }
    return render(request, 'bingo_app/print_card.html', context)

@login_required
def organizer_printable_cards(request):
    if request.user.is_organizer or request.user.is_admin:
        # Mostrar solo los cartones que el usuario posee o que no están asignados
        printable_cards = PrintableCard.objects.filter(Q(owner=request.user) | Q(owner__isnull=True)).order_by('-created_at')
    else:
        messages.error(request, "No tienes permiso para ver esta página.")
        return redirect('lobby')

    context = {
        'printable_cards': printable_cards,
    }
    return render(request, 'bingo_app/organizer_printable_cards.html', context)

@login_required
def print_selected_cards(request):
    if not (request.user.is_organizer or request.user.is_admin):
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('lobby')

    if request.method == 'POST':
        selected_card_ids = request.POST.getlist('selected_cards')
        if not selected_card_ids:
            messages.error(request, "No se seleccionaron cartones para imprimir.")
            return redirect('organizer_printable_cards')

        # Filtrar los cartones para asegurar que el usuario tiene permiso para imprimirlos
        # (es el propietario o el cartón no está asignado)
        cards_to_print = PrintableCard.objects.filter(
            unique_id__in=selected_card_ids
        ).filter(
            Q(owner=request.user) | Q(owner__isnull=True)
        ).order_by('unique_id')

        if not cards_to_print.exists():
            messages.error(request, "Ninguno de los cartones seleccionados es válido o tienes permiso para imprimir.")
            return redirect('organizer_printable_cards')

        context = {
            'cards': cards_to_print,
        }
        return render(request, 'bingo_app/print_multiple_cards.html', context)
    
    return redirect('organizer_printable_cards') # Redirect if not a POST request

@staff_member_required
def bulk_assign_printable_cards(request):
    users = User.objects.filter(is_staff=False, is_superuser=False).order_by('username')
    printable_cards = PrintableCard.objects.filter(owner__isnull=True).order_by('-created_at')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        selected_card_ids = request.POST.getlist('selected_cards') # Get list of unique_ids

        if not user_id or not selected_card_ids:
            messages.error(request, "Debes seleccionar un usuario y al menos un cartón.")
            return redirect('bulk_assign_printable_cards')

        try:
            target_user = get_object_or_404(User, id=user_id)
            
            with transaction.atomic():
                assigned_count = 0
                for card_unique_id in selected_card_ids:
                    card = get_object_or_404(PrintableCard, unique_id=card_unique_id, owner__isnull=True)
                    card.owner = target_user
                    card.save()
                    assigned_count += 1
                
                messages.success(request, f"Se asignaron {assigned_count} cartones a {target_user.username} exitosamente.")
                return redirect('manage_printable_cards') # Redirect to admin management page
        except Exception as e:
            messages.error(request, f"Error al asignar cartones: {str(e)}")
            
    context = {
        'users': users,
        'printable_cards': printable_cards,
    }
    return render(request, 'bingo_app/admin/bulk_assign_printable_cards.html', context)


@login_required
def create_promotion(request):
    if not request.user.is_organizer:
        messages.error(request, "Solo los organizadores pueden promocionar eventos.")
        return redirect('lobby')

    # Obtener la configuración de precios de promoción
    percentage_settings = PercentageSettings.objects.first()
    if not percentage_settings:
        messages.error(request, "La configuración de precios de promoción no está disponible. Contacta al administrador.")
        return redirect('lobby')

    # Definir los costos de promoción basados en la configuración
    PROMOTION_COSTS = {
        'image': {
            1: percentage_settings.image_promotion_price,  # 1 día
            3: percentage_settings.image_promotion_price * Decimal('2.5'), # Ejemplo: 3 días con descuento
            7: percentage_settings.image_promotion_price * Decimal('4'),   # Ejemplo: 7 días con más descuento
        },
        'video': {
            1: percentage_settings.video_promotion_price,  # 1 día
            3: percentage_settings.video_promotion_price * Decimal('2.5'), # Ejemplo: 3 días con descuento
            7: percentage_settings.video_promotion_price * Decimal('4'),   # Ejemplo: 7 días con más descuento
        }
    }

    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES, user=request.user)
        duration = int(request.POST.get('duration', 0)) # Obtener la duración directamente del POST

        if form.is_valid():
            image_uploaded = form.cleaned_data.get('image')
            video_url_provided = form.cleaned_data.get('video_url')

            promotion_type = None
            if image_uploaded:
                promotion_type = 'image'
            elif video_url_provided:
                promotion_type = 'video'
            
            cost = Decimal('0.00')
            if promotion_type and duration in PROMOTION_COSTS[promotion_type]:
                cost = PROMOTION_COSTS[promotion_type][duration]
            else:
                messages.error(request, "Selección de duración o tipo de promoción inválida.")
                return render(request, 'bingo_app/create_promotion.html', {
                    'form': form,
                    'costs': PROMOTION_COSTS,
                    'selected_duration': duration # Para mantener la selección en el formulario
                })

            if request.user.credit_balance < cost:
                messages.error(request, f"No tienes suficientes créditos. Necesitas {cost} créditos.")
            else:
                try:
                    with transaction.atomic():
                        # Cobrar al organizador
                        request.user.credit_balance -= cost
                        request.user.save()

                        # Crear la transacción
                        Transaction.objects.create(
                            user=request.user,
                            amount=-cost,
                            transaction_type='OTHER',
                            description=f'Costo de promoción de evento por {duration} día(s) ({promotion_type})'
                        )

                        # Crear el anuncio
                        announcement = form.save(commit=False)
                        announcement.announcement_type = 'PROMOTION'
                        announcement.promoted_by = request.user
                        announcement.expires_at = timezone.now() + timezone.timedelta(days=duration)
                        announcement.is_active = True
                        announcement.save()

                        messages.success(request, "¡Tu evento ha sido promocionado exitosamente!")
                        return redirect('lobby')
                except Exception as e:
                    sentry_sdk.capture_exception(e)
                    messages.error(request, "Hubo un error al procesar la promoción. El equipo técnico ha sido notificado.")

    else:
        form = PromotionForm(user=request.user)
        duration = 1 # Default selected duration for GET request

    return render(request, 'bingo_app/create_promotion.html', {
        'form': form,
        'costs': PROMOTION_COSTS,
        'selected_duration': duration # Para que JavaScript pueda leer la duración inicial
    })


@staff_member_required
def manage_announcements(request):
    announcements = Announcement.objects.all().order_by('order', '-created_at')
    
    # Formularios para crear nuevos anuncios
    general_form = GeneralAnnouncementForm(prefix='general')
    external_form = ExternalAdForm(prefix='external')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'general':
            form = GeneralAnnouncementForm(request.POST, prefix='general')
            if form.is_valid():
                announcement = form.save(commit=False)
                announcement.announcement_type = 'GENERAL'
                announcement.save()
                messages.success(request, 'Anuncio general creado.')
                return redirect('manage_announcements')

        elif form_type == 'external':
            form = ExternalAdForm(request.POST, request.FILES, prefix='external')
            if form.is_valid():
                announcement = form.save(commit=False)
                announcement.announcement_type = 'EXTERNAL'
                announcement.save()
                messages.success(request, 'Anuncio externo creado.')
                return redirect('manage_announcements')

    context = {
        'announcements': announcements,
        'general_form': general_form,
        'external_form': external_form,
    }
    return render(request, 'bingo_app/admin/manage_announcements.html', context)

@staff_member_required
def edit_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if announcement.announcement_type == 'GENERAL':
        FormClass = GeneralAnnouncementForm
    elif announcement.announcement_type == 'EXTERNAL':
        FormClass = ExternalAdForm
    else: # 'PROMOTION'
        # Las promociones no se editan desde aquí, sino que se gestionan (activan/desactivan)
        messages.info(request, "Las promociones de eventos no se pueden editar directamente.")
        return redirect('manage_announcements')

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anuncio actualizado.')
            return redirect('manage_announcements')
    else:
        form = FormClass(instance=announcement)

    return render(request, 'bingo_app/admin/edit_announcement.html', {
        'form': form,
        'announcement': announcement
    })

@staff_member_required
def delete_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Anuncio eliminado.')
        return redirect('manage_announcements')
    return render(request, 'bingo_app/admin/delete_announcement.html', {'announcement': announcement})


# INICIO DE FUNCIONES DE CONTEXTO MEJORADAS

def _get_admin_dashboard_context_mejorado(start_date=None, end_date=None):
    """
    Función mejorada para obtener el contexto del dashboard de administrador
    con cálculos financieros corregidos y métricas adicionales.
    """
    # Filtros de fecha - por defecto últimos 30 días
    date_filter = Q()
    if start_date:
        date_filter &= Q(created_at__gte=start_date)
    else:
        # Si no hay fecha de inicio, usar últimos 30 días por defecto
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        date_filter &= Q(created_at__gte=thirty_days_ago)
    
    if end_date:
        end_date_plus_one = end_date + timezone.timedelta(days=1)
        date_filter &= Q(created_at__lt=end_date_plus_one)

    # ===== MÉTRICAS FINANCIERAS CORREGIDAS =====
    
    # 1. Ingresos Totales de la Plataforma (CORREGIDO)
    platform_revenue = Transaction.objects.filter(
        transaction_type__in=[
            'PLATFORM_COMMISSION',
            'GAME_CREATION_FEE', 
            'RAFFLE_CREATION_FEE'
        ],
        amount__gt=0
    ).filter(date_filter).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Agregar ingresos por promociones/anuncios (transacciones OTHER negativas del usuario = ingresos para la plataforma)
    promotion_revenue = Transaction.objects.filter(
        transaction_type='OTHER',
        amount__lt=0,  # Negativas para el usuario = positivas para la plataforma
        description__icontains='promoción'
    ).filter(date_filter).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    promotion_revenue = abs(promotion_revenue)  # Convertir a positivo
    
    platform_revenue += promotion_revenue

    # 2. Créditos Asignados por Administradores
    credits_added = Transaction.objects.filter(
        transaction_type='ADMIN_ADD',
        amount__gt=0
    ).filter(date_filter).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # 3. Premios Pagados (mantener cálculo actual)
    prizes_paid = Transaction.objects.filter(
        transaction_type='PRIZE',
        amount__gt=0
    ).filter(date_filter).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # 4. Retiros Procesados
    withdrawals_processed = Transaction.objects.filter(
        transaction_type='WITHDRAWAL',
        amount__lt=0  # Los retiros son negativos
    ).filter(date_filter).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    withdrawals_processed = abs(withdrawals_processed)  # Convertir a positivo para mostrar

    # 5. Ganancia Neta de la Plataforma (CORREGIDO)
    # Ingresos de la plataforma menos costos operativos
    net_profit = platform_revenue

    # ===== MÉTRICAS DE LIQUIDEZ =====
    
    # Saldo Total en Circulación
    total_balance = User.objects.aggregate(Sum('credit_balance'))['credit_balance__sum'] or Decimal('0.00')
    
    # Saldo Total Bloqueado
    total_blocked = User.objects.aggregate(Sum('blocked_credits'))['blocked_credits__sum'] or Decimal('0.00')
    
    # Saldo en Escrow (juegos activos)
    total_escrow = Game.objects.filter(
        is_active=True, 
        is_finished=False
    ).aggregate(Sum('held_balance'))['held_balance__sum'] or Decimal('0.00')
    
    # Ratio de Liquidez
    total_system_credits = total_balance + total_blocked + total_escrow
    liquidity_ratio = (total_balance / total_system_credits * 100) if total_system_credits > 0 else 0

    # ===== MÉTRICAS DE ACTIVIDAD =====
    
    # Juegos y Rifas Activos
    active_games = Game.objects.filter(is_active=True, is_finished=False).count()
    active_raffles = Raffle.objects.filter(status__in=['WAITING', 'IN_PROGRESS']).count()
    
    # Usuarios Registrados
    registered_users = User.objects.count()
    
    # Usuarios Activos (con transacciones en los últimos 7 días)
    week_ago = timezone.now() - timezone.timedelta(days=7)
    active_users = User.objects.filter(
        transactions__created_at__gte=week_ago
    ).distinct().count()

    # ===== MÉTRICAS DE RENDIMIENTO =====
    
    # Comisión Promedio por Juego
    avg_commission = Transaction.objects.filter(
        transaction_type='PLATFORM_COMMISSION'
    ).filter(date_filter).aggregate(
        avg_amount=Avg('amount')
    )['avg_amount'] or Decimal('0.00')
    
    # Juegos Completados
    completed_games = Game.objects.filter(
        is_finished=True
    ).filter(date_filter).count()
    
    # Rifas Completadas
    completed_raffles = Raffle.objects.filter(
        status='FINISHED'
    ).filter(date_filter).count()

    # ===== CONTROL DE RETIROS =====
    
    # Retiros Pendientes
    pending_withdrawals = WithdrawalRequest.objects.filter(
        status='PENDING'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Número de Retiros Pendientes
    pending_withdrawals_count = WithdrawalRequest.objects.filter(
        status='PENDING'
    ).count()
    
    # Retiros Aprobados vs Rechazados
    approved_withdrawals = WithdrawalRequest.objects.filter(
        status__in=['APPROVED', 'COMPLETED']
    ).filter(date_filter).count()
    
    rejected_withdrawals = WithdrawalRequest.objects.filter(
        status='REJECTED'
    ).filter(date_filter).count()
    
    total_withdrawal_requests = approved_withdrawals + rejected_withdrawals
    approval_ratio = (approved_withdrawals / total_withdrawal_requests * 100) if total_withdrawal_requests > 0 else 0

    # ===== MÉTRICAS FINANCIERAS AVANZADAS =====
    
    # Calcular ingresos del sistema (transacciones negativas = ingresos) - optimizado
    income_total = Transaction.objects.filter(
        amount__lt=0
    ).filter(date_filter).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Entradas vs Salidas por día
    # Las compras aparecen como negativas, pero son ingresos para el sistema
    daily_income = abs(income_total)
    
    daily_expenses = Transaction.objects.filter(
        transaction_type__in=['PRIZE', 'WITHDRAWAL', 'REFUND'],
        amount__lt=0
    ).filter(date_filter).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    daily_expenses = abs(daily_expenses)  # Convertir a positivo
    
    # Balance del sistema
    system_balance = daily_income - daily_expenses
    
    # Usuarios con saldos altos (>$1000)
    high_balance_users = User.objects.filter(credit_balance__gt=1000).count()
    
    # Usuarios bloqueados
    blocked_users = User.objects.filter(blocked_at__isnull=False).count()
    
    # Usuarios nuevos (últimos 7 días)
    week_ago = timezone.now() - timezone.timedelta(days=7)
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    
    # Juegos con problemas (sin actividad en 24h pero activos)
    day_ago = timezone.now() - timezone.timedelta(days=1)
    problematic_games = Game.objects.filter(
        is_active=True,
        is_finished=False,
        created_at__lt=day_ago
    ).count()
    
    # Transacciones sospechosas (monto > $500)
    suspicious_transactions = Transaction.objects.filter(
        amount__gt=500,
        created_at__gte=week_ago
    ).count()
    
    # Tiempo promedio de procesamiento de retiros (en horas)
    avg_withdrawal_time = WithdrawalRequest.objects.filter(
        status__in=['APPROVED', 'REJECTED'],
        created_at__gte=week_ago
    ).aggregate(
        avg_time=Avg(
            F('processed_at') - F('created_at')
        )
    )['avg_time']
    
    if avg_withdrawal_time:
        avg_withdrawal_hours = avg_withdrawal_time.total_seconds() / 3600
    else:
        avg_withdrawal_hours = 0

    # ===== DATOS PARA GRÁFICOS =====
    
    chart_start_date = start_date
    if not chart_start_date:
        chart_start_date = timezone.now().date() - timezone.timedelta(days=30)
    
    chart_date_filter = Q(created_at__gte=chart_start_date)
    if end_date:
        chart_date_filter &= Q(created_at__lt=end_date + timezone.timedelta(days=1))

    # Ingresos de la plataforma por día
    revenue_by_day = (
        Transaction.objects.filter(
            transaction_type__in=[
                'PLATFORM_COMMISSION',
                'GAME_CREATION_FEE', 
                'RAFFLE_CREATION_FEE'
            ]
        )
        .filter(chart_date_filter)
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )

    # Usuarios registrados por día
    users_by_day = (
        User.objects.filter(date_joined__gte=chart_start_date)
        .annotate(day=TruncDay('date_joined'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )

    # Transacciones por tipo
    transactions_by_type = (
        Transaction.objects.filter(date_filter)
        .values('transaction_type')
        .annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        .order_by('-total_amount')
    )

    # Convertir a listas de forma eficiente (evaluar querysets una sola vez)
    revenue_by_day_list = list(revenue_by_day)
    users_by_day_list = list(users_by_day)
    
    revenue_labels = [r['day'].strftime('%Y-%m-%d') for r in revenue_by_day_list]
    revenue_data = [float(r['total']) for r in revenue_by_day_list]
    user_labels = [u['day'].strftime('%Y-%m-%d') for u in users_by_day_list]
    user_data = [u['total'] for u in users_by_day_list]

    # ===== TABLAS DE DATOS =====
    
    # Top Jugadores por Ganancias (optimizado con prefetch_related)
    top_players = User.objects.annotate(
        total_winnings=Sum(
            'transactions__amount',
            filter=Q(transactions__transaction_type='PRIZE', transactions__amount__gt=0)
        )
    ).filter(total_winnings__gt=0).order_by('-total_winnings')[:10]
    
    # Top Organizadores por Juegos Creados (optimizado)
    top_organizers = User.objects.filter(is_organizer=True).annotate(
        games_created=Count('organized_games'),
        total_revenue=Sum(
            'transactions__amount',
            filter=Q(transactions__transaction_type='ORGANIZER_REVENUE')
        )
    ).order_by('-games_created')[:10]
    
    # Últimas Transacciones (optimizado con select_related y solo campos necesarios)
    latest_transactions = Transaction.objects.filter(
        date_filter
    ).select_related('user', 'related_game').only(
        'id', 'user__username', 'user__email', 'amount', 'transaction_type', 
        'description', 'created_at', 'related_game__name'
    ).order_by('-created_at')[:20]

    # ===== ALERTAS DEL SISTEMA =====
    
    alerts = []
    
    # Alerta de liquidez baja
    if liquidity_ratio < 50:
        alerts.append({
            'type': 'warning',
            'message': f'Ratio de liquidez bajo: {liquidity_ratio:.1f}%',
            'action': 'Revisar saldos bloqueados y en escrow'
        })
    
    # Alerta de retiros pendientes altos
    if pending_withdrawals > 5000:
        alerts.append({
            'type': 'danger',
            'message': f'Retiros pendientes altos: ${pending_withdrawals:.2f}',
            'action': 'Procesar retiros urgentemente'
        })
    
    # Alerta de usuarios con saldos altos
    if high_balance_users > 5:
        alerts.append({
            'type': 'info',
            'message': f'{high_balance_users} usuarios con saldos > $1000',
            'action': 'Revisar actividad de usuarios con saldos altos'
        })
    
    # Alerta de transacciones sospechosas
    if suspicious_transactions > 0:
        alerts.append({
            'type': 'warning',
            'message': f'{suspicious_transactions} transacciones > $500 en la semana',
            'action': 'Revisar transacciones grandes por posible fraude'
        })
    
    # Alerta de juegos con problemas
    if problematic_games > 0:
        alerts.append({
            'type': 'warning',
            'message': f'{problematic_games} juegos sin actividad en 24h',
            'action': 'Revisar y finalizar juegos abandonados'
        })
    
    # Alerta de balance negativo
    if system_balance < 0:
        alerts.append({
            'type': 'danger',
            'message': f'Balance del sistema negativo: ${system_balance:.2f}',
            'action': 'URGENTE: Revisar ingresos y gastos del sistema'
        })
    
    # Alerta de tiempo de procesamiento alto
    if avg_withdrawal_hours > 24:
        alerts.append({
            'type': 'warning',
            'message': f'Tiempo promedio de retiros: {avg_withdrawal_hours:.1f}h',
            'action': 'Mejorar tiempo de procesamiento de retiros'
        })
    
    # Alerta de retiros pendientes
    if pending_withdrawals_count > 10:
        alerts.append({
            'type': 'info',
            'message': f'{pending_withdrawals_count} retiros pendientes de procesamiento',
            'action': 'Revisar solicitudes de retiro'
        })
    
    # Alerta de saldo alto en escrow
    if total_escrow > total_balance * Decimal('0.3'):
        alerts.append({
            'type': 'warning',
            'message': 'Alto saldo retenido en juegos activos',
            'action': 'Revisar juegos que no han finalizado'
        })

    return {
        # Métricas Financieras Principales
        'platform_revenue': platform_revenue,
        'credits_added': credits_added,
        'prizes_paid': prizes_paid,
        'withdrawals_processed': withdrawals_processed,
        'net_profit': net_profit,
        
        # Métricas de Liquidez
        'total_balance': total_balance,
        'total_blocked': total_blocked,
        'total_escrow': total_escrow,
        'total_system_credits': total_system_credits,
        'liquidity_ratio': liquidity_ratio,
        
        # Métricas de Actividad
        'active_games': active_games,
        'active_raffles': active_raffles,
        'registered_users': registered_users,
        'active_users': active_users,
        
        # Métricas de Rendimiento
        'avg_commission': avg_commission,
        'completed_games': completed_games,
        'completed_raffles': completed_raffles,
        
        # Control de Retiros
        'pending_withdrawals': pending_withdrawals,
        'pending_withdrawals_count': pending_withdrawals_count,
        'approval_ratio': approval_ratio,
        
        # Métricas Financieras Avanzadas
        'daily_income': daily_income,
        'daily_expenses': daily_expenses,
        'system_balance': system_balance,
        'high_balance_users': high_balance_users,
        'blocked_users': blocked_users,
        'new_users_week': new_users_week,
        'problematic_games': problematic_games,
        'suspicious_transactions': suspicious_transactions,
        'avg_withdrawal_hours': avg_withdrawal_hours,
        
        # Datos para Gráficos
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),
        'user_labels': json.dumps(user_labels),
        'user_data': json.dumps(user_data),
        'transactions_by_type': list(transactions_by_type),
        
        # Tablas de Datos
        'top_players': top_players,
        'top_organizers': top_organizers,
        'latest_transactions': latest_transactions,
        
        # Alertas del Sistema
        'alerts': alerts,
        
        # Filtros de Fecha
        'start_date': start_date,
        'end_date': end_date,
        'title': 'Dashboard de Administrador Mejorado',
    }

def _get_organizer_dashboard_context_mejorado(request):
    """
    Función mejorada para obtener el contexto del dashboard de organizadores
    con métricas específicas para organizadores.
    """
    organizer = request.user
    
    # ===== MÉTRICAS DE RENDIMIENTO PERSONAL =====
    
    # Juegos y Rifas Creados
    total_games = Game.objects.filter(organizer=organizer).count()
    total_raffles = Raffle.objects.filter(organizer=organizer).count()
    
    # Juegos y Rifas Activos
    active_games = Game.objects.filter(
        organizer=organizer, 
        is_active=True, 
        is_finished=False
    ).count()
    active_raffles = Raffle.objects.filter(
        organizer=organizer,
        status__in=['WAITING', 'IN_PROGRESS']
    ).count()
    
    # Juegos y Rifas Completados
    completed_games = Game.objects.filter(
        organizer=organizer,
        is_finished=True
    ).count()
    completed_raffles = Raffle.objects.filter(
        organizer=organizer,
        status='FINISHED'
    ).count()

    # ===== MÉTRICAS FINANCIERAS =====
    
    # Ingresos Netos de Eventos (después de comisiones)
    total_net_revenue_from_events = Transaction.objects.filter(
        user=organizer,
        transaction_type='ORGANIZER_REVENUE',
        amount__gt=0
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Comisiones Pagadas a la Plataforma
    total_commissions = Transaction.objects.filter(
        related_game__organizer=organizer,
        transaction_type='PLATFORM_COMMISSION'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Costos de Creación (tarifas de entrada)
    creation_fees = Transaction.objects.filter(
        user=organizer,
        transaction_type__in=['GAME_CREATION_FEE', 'RAFFLE_CREATION_FEE'],
        amount__lt=0
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    creation_fees = abs(creation_fees)  # Convertir a positivo
    
    # Premios Pagados por el organizador
    prizes_paid_by_organizer = Transaction.objects.filter(
        related_game__organizer=organizer,
        transaction_type='PRIZE'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Ganancia Neta del Organizador
    net_profit = total_net_revenue_from_events - creation_fees
    
    # Saldo Actual
    current_balance = organizer.credit_balance
    blocked_balance = organizer.blocked_credits

    # ===== MÉTRICAS DE PARTICIPACIÓN =====
    
    # Participación Promedio en Juegos
    games_with_players = Game.objects.filter(
        organizer=organizer,
        is_finished=True
    ).annotate(
        player_count=Count('player')
    )
    
    avg_game_participation = games_with_players.aggregate(
        avg_players=Avg('player_count')
    )['avg_players'] or 0
    
    # Participación Promedio en Rifas
    raffles_with_tickets = Raffle.objects.filter(
        organizer=organizer,
        status='FINISHED'
    ).annotate(
        ticket_count=Count('tickets')
    )
    
    avg_raffle_participation = raffles_with_tickets.aggregate(
        avg_tickets=Avg('ticket_count')
    )['avg_tickets'] or 0
    
    # Ingresos Promedio por Evento
    total_events = completed_games + completed_raffles
    avg_revenue_per_event = total_net_revenue_from_events / total_events if total_events > 0 else Decimal('0.00')

    # ===== EVENTOS RECIENTES =====
    
    # Últimos Juegos
    recent_games = Game.objects.filter(
        organizer=organizer
    ).order_by('-created_at')[:5]
    
    # Últimas Rifas
    recent_raffles = Raffle.objects.filter(
        organizer=organizer
    ).order_by('-created_at')[:5]
    
    # Últimas Transacciones
    recent_transactions = Transaction.objects.filter(
        user=organizer
    ).order_by('-created_at')[:10]

    # ===== ANÁLISIS DE RENDIMIENTO =====
    
    # Tasa de Finalización de Juegos
    total_games_created = Game.objects.filter(organizer=organizer).count()
    completion_rate = (completed_games / total_games_created * 100) if total_games_created > 0 else 0
    
    # ROI (Return on Investment)
    total_investment = creation_fees + prizes_paid_by_organizer
    roi = ((net_profit / total_investment) * 100) if total_investment > 0 else 0

    # ===== PROYECCIONES =====
    
    # Ingresos Potenciales de Eventos Activos
    potential_revenue_games = Game.objects.filter(
        organizer=organizer,
        is_active=True,
        is_finished=False
    ).aggregate(
        total_held=Sum('held_balance')
    )['total_held'] or Decimal('0.00')
    
    potential_revenue_raffles = Raffle.objects.filter(
        organizer=organizer,
        status__in=['WAITING', 'IN_PROGRESS']
    ).aggregate(
        total_held=Sum('held_balance')
    )['total_held'] or Decimal('0.00')
    
    total_potential_revenue = potential_revenue_games + potential_revenue_raffles
    
    # Estimación de comisiones a pagar
    percentage_settings = PercentageSettings.objects.first()
    commission_rate = percentage_settings.platform_commission if percentage_settings else Decimal('10.00')
    estimated_commissions = total_potential_revenue * (commission_rate / 100)
    estimated_net_revenue = total_potential_revenue - estimated_commissions

    # ===== ALERTAS Y RECOMENDACIONES =====
    
    alerts = []
    recommendations = []
    
    # Alerta de saldo bajo
    if current_balance < 100:
        alerts.append({
            'type': 'warning',
            'message': 'Saldo bajo para crear nuevos eventos',
            'action': 'Considera solicitar más créditos'
        })
    
    # Recomendación basada en rendimiento
    if completion_rate < 80:
        recommendations.append({
            'type': 'improvement',
            'message': f'Tasa de finalización: {completion_rate:.1f}%',
            'action': 'Revisa la configuración de tus eventos para mejorar la participación'
        })
    
    # Recomendación de diversificación
    if total_games > 0 and total_raffles == 0:
        recommendations.append({
            'type': 'opportunity',
            'message': 'Solo has creado juegos de bingo',
            'action': 'Considera crear rifas para diversificar tus ingresos'
        })

    return {
        # Métricas de Rendimiento Personal
        'total_games': total_games,
        'total_raffles': total_raffles,
        'active_games': active_games,
        'active_raffles': active_raffles,
        'completed_games': completed_games,
        'completed_raffles': completed_raffles,
        
        # Métricas Financieras
        'total_revenue': total_net_revenue_from_events, # Renamed for clarity in template if needed
        'total_commissions': total_commissions,
        'creation_fees': creation_fees,
        'prizes_paid': prizes_paid_by_organizer, # new context variable
        'net_profit': net_profit,
        'current_balance': current_balance,
        'blocked_balance': blocked_balance,
        
        # Métricas de Participación
        'avg_game_participation': avg_game_participation,
        'avg_raffle_participation': avg_raffle_participation,
        'avg_revenue_per_event': avg_revenue_per_event,
        
        # Eventos Recientes
        'recent_games': recent_games,
        'recent_raffles': recent_raffles,
        'recent_transactions': recent_transactions,
        
        # Análisis de Rendimiento
        'completion_rate': completion_rate,
        'roi': roi,
        
        # Proyecciones
        'total_potential_revenue': total_potential_revenue,
        'estimated_commissions': estimated_commissions,
        'estimated_net_revenue': estimated_net_revenue,
        
        # Alertas y Recomendaciones
        'alerts': alerts,
        'recommendations': recommendations,
        
        'title': 'Dashboard de Organizador Mejorado',
    }

# FIN DE FUNCIONES DE CONTEXTO MEJORADAS

# MODIFICAR FUNCIONES EXISTENTES PARA USAR LAS MEJORADAS

# Modificar admin_dashboard
@staff_member_required
def admin_dashboard(request):
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha de inicio inválido.")

    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha de fin inválido.")

    context = _get_admin_dashboard_context_mejorado(start_date, end_date)
    
    # Usar asistente local (siempre funciona, sin APIs externas)
    # Solo usar Gemini si está explícitamente configurado y funcionando
    try:
        # Verificar si Gemini está realmente disponible y funcionando
        gemini_available = False
        if ai_assistant.is_available():
            try:
                # Intentar una llamada rápida para verificar que funciona
                test_context = {'test': True}
                test_result = ai_assistant.analyze_dashboard_metrics(test_context)
                if test_result and test_result.get('source') != 'quota_error':
                    gemini_available = True
            except:
                gemini_available = False
        
        if gemini_available:
            # Usar IA real (Gemini) solo si está funcionando
            try:
                ai_analysis = ai_assistant.analyze_dashboard_metrics(context)
                context['ai_analysis'] = ai_analysis
                context['ai_available'] = True
                context['ai_type'] = 'gemini'
            except:
                # Si falla, usar asistente local
                ai_analysis = smart_assistant.analyze_dashboard_metrics(context)
                context['ai_analysis'] = ai_analysis
                context['ai_available'] = True
                context['ai_type'] = 'local'
        else:
            # Usar asistente local (siempre funciona)
            ai_analysis = smart_assistant.analyze_dashboard_metrics(context)
            context['ai_analysis'] = ai_analysis
            context['ai_available'] = True
            context['ai_type'] = 'local'
    except Exception as e:
        logger.error(f"Error en análisis de IA: {str(e)}")
        # Fallback final al asistente local
        try:
            ai_analysis = smart_assistant.analyze_dashboard_metrics(context)
            context['ai_analysis'] = ai_analysis
            context['ai_available'] = True
            context['ai_type'] = 'local'
        except Exception as e2:
            logger.error(f"Error en asistente local: {str(e2)}")
            context['ai_available'] = False
    
    return render(request, 'bingo_app/admin/dashboard.html', context)


@staff_member_required
@require_POST
def reset_dashboards(request):
    """
    Reinicia los dashboards limpiando datos históricos.
    Usa el comando de gestión `limpiar_dashboards` en modo seguro (sin confirmación interactiva).
    """
    try:
        # Ejecutar limpieza completa sin pedir confirmación.
        # Mantiene usuarios y configuraciones, y resetea saldos para arrancar de cero.
        call_command(
            "limpiar_dashboards",
            completo=True,
            reset_saldos=True,
            sin_confirmacion=True,
            solo_vista_previa=False,
        )
        messages.success(
            request,
            "Se ha reiniciado el dashboard y limpiado los datos históricos correctamente.",
        )
    except Exception as e:
        messages.error(request, f"Error al reiniciar dashboards: {str(e)}")

    return redirect("admin_dashboard")

# Modificar organizer_dashboard
@login_required
def organizer_dashboard(request):
    context = _get_organizer_dashboard_context_mejorado(request)
    return render(request, 'bingo_app/organizer_dashboard.html', context)

def privacy_policy(request):
    return render(request, 'bingo_app/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'bingo_app/terms_of_service.html')

def data_deletion(request):
    return render(request, 'bingo_app/data_deletion.html')

def handler404(request, exception):
    return render(request, 'bingo_app/404.html', status=404)

def user_manual(request):
    """Manual de usuario para el sistema de Bingo y Rifas"""
    return render(request, 'bingo_app/user_manual.html')

@login_required
def launch_promotions(request):
    """Página de promociones de lanzamiento"""
    from .models import LaunchPromotion, UserPromotion, LaunchAchievement, UserAchievement
    
    # Verificar si el sistema de promociones está habilitado
    settings_obj = PercentageSettings.objects.first()
    if not settings_obj or not settings_obj.promotions_enabled:
        messages.error(request, 'El sistema de promociones está temporalmente deshabilitado.')
        return redirect('profile')
    
    # Obtener promociones disponibles
    available_promotions = LaunchPromotion.objects.filter(is_active=True)
    
    # Verificar cuáles puede reclamar el usuario
    user_promotions = []
    for promotion in available_promotions:
        if promotion.can_user_claim(request.user):
            user_promotions.append(promotion)
    
    # Obtener logros del usuario
    user_achievements = UserAchievement.objects.filter(user=request.user)
    
    # Obtener logros disponibles
    available_achievements = LaunchAchievement.objects.filter(is_active=True)
    
    context = {
        'available_promotions': user_promotions,
        'user_achievements': user_achievements,
        'available_achievements': available_achievements,
    }
    
    return render(request, 'bingo_app/launch_promotions.html', context)

@login_required
def claim_promotion(request, promotion_id):
    """Reclamar una promoción"""
    from .models import LaunchPromotion, UserPromotion
    from django.contrib import messages
    
    # Verificar si el sistema de promociones está habilitado
    settings_obj = PercentageSettings.objects.first()
    if not settings_obj or not settings_obj.promotions_enabled:
        messages.error(request, 'El sistema de promociones está temporalmente deshabilitado.')
        return redirect('profile')
    
    try:
        promotion = LaunchPromotion.objects.get(id=promotion_id)
        
        if not promotion.can_user_claim(request.user):
            messages.error(request, "No puedes reclamar esta promoción.")
            return redirect('launch_promotions')
        
        # Crear el registro de promoción reclamada
        user_promotion = UserPromotion.objects.create(
            user=request.user,
            promotion=promotion,
            bonus_amount=promotion.bonus_amount
        )
        
        # Agregar créditos al usuario
        request.user.credits += promotion.bonus_amount
        request.user.save()
        
        # Incrementar contador de usos
        promotion.current_uses += 1
        promotion.save()
        
        # Marcar como procesado
        user_promotion.is_processed = True
        user_promotion.save()
        
        messages.success(request, f"¡Promoción reclamada! Has recibido ${promotion.bonus_amount} en créditos.")
        
    except LaunchPromotion.DoesNotExist:
        messages.error(request, "Promoción no encontrada.")
    
    return redirect('launch_promotions')

@login_required
def referral_system(request):
    """Sistema de referidos"""
    from .models import ReferralProgram
    from django.contrib import messages
    
    # Verificar si el sistema de referidos está habilitado
    settings_obj = PercentageSettings.objects.first()
    if not settings_obj or not settings_obj.referral_system_enabled:
        messages.error(request, 'El sistema de referidos está temporalmente deshabilitado.')
        return redirect('profile')
    
    # El código de referido es el username del usuario
    referral_code = request.user.username.upper()
    
    # Obtener referidos del usuario
    referrals = ReferralProgram.objects.filter(referrer=request.user)
    
    # Generar enlace de referido
    base_url = request.build_absolute_uri('/register/')
    referral_link = f"{base_url}?referral_code={referral_code}"
    
    context = {
        'referral_code': referral_code,
        'referral_link': referral_link,
        'referrals': referrals,
        'referral_bonus': 5.00,  # Bonus por referido
    }
    
    return render(request, 'bingo_app/referral_system.html', context)

@login_required
def system_health_dashboard(request):
    """Dashboard de salud del sistema para administradores"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('lobby')
    
    try:
        # Obtener resumen de errores de Facebook
        facebook_errors = get_facebook_error_summary()
        
        # Estadísticas del sistema
        total_users = User.objects.count()
        active_users_today = User.objects.filter(last_login__date=timezone.now().date()).count()
        total_games = Game.objects.count()
        
        # Juegos activos: iniciados pero no finalizados
        active_games = Game.objects.filter(is_started=True, is_finished=False).count()
        
        # Debug: verificar diferentes estados de juegos
        started_games = Game.objects.filter(is_started=True).count()
        finished_games = Game.objects.filter(is_finished=True).count()
        pending_games = Game.objects.filter(is_started=False, is_finished=False).count()
        
        # Log para debugging
        logger.info(f"Dashboard Debug - Total games: {total_games}, Active: {active_games}, Started: {started_games}, Finished: {finished_games}, Pending: {pending_games}")
        
        # Estadísticas de rifas
        from .models import Raffle
        total_raffles = Raffle.objects.count()
        active_raffles = Raffle.objects.filter(status='ACTIVE').count()
        finished_raffles = Raffle.objects.filter(status='FINISHED').count()
        pending_raffles = Raffle.objects.filter(status='PENDING').count()
        
        # Estadísticas de login social
        social_accounts = SocialAccount.objects.count()
        facebook_accounts = SocialAccount.objects.filter(provider='facebook').count()
        google_accounts = SocialAccount.objects.filter(provider='google').count()
        
        context = {
            'facebook_errors': facebook_errors,
            'total_users': total_users,
            'active_users_today': active_users_today,
            'total_games': total_games,
            'active_games': active_games,
            'started_games': started_games,
            'finished_games': finished_games,
            'pending_games': pending_games,
            'total_raffles': total_raffles,
            'active_raffles': active_raffles,
            'finished_raffles': finished_raffles,
            'pending_raffles': pending_raffles,
            'social_accounts': social_accounts,
            'facebook_accounts': facebook_accounts,
            'google_accounts': google_accounts,
            'system_uptime': 'Sistema operativo desde enero 2024',
        }
        
        return render(request, 'bingo_app/system_health_dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Error al cargar el dashboard: {str(e)}")
        return redirect('admin_dashboard')

@login_required
def reset_error_counters(request):
    """Reinicia los contadores de errores"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('lobby')
    
    try:
        reset_facebook_error_counters()
        messages.success(request, "Contadores de errores reiniciados correctamente.")
    except Exception as e:
        messages.error(request, f"Error al reiniciar contadores: {str(e)}")
    
    return redirect('system_health_dashboard')

@login_required
@require_http_methods(["GET", "POST"])
def get_agora_token(request):
    try:
        appId = settings.AGORA_APP_ID
        appCertificate = getattr(settings, 'AGORA_APP_CERTIFICATE', None)
        
        # Aceptar tanto GET como POST
        if request.method == 'POST':
            data = json.loads(request.body)
            channelName = data.get('channel_name')
            uid = data.get('uid', request.user.id)
        else:
            channelName = request.GET.get('channelName') or request.GET.get('channel_name')
            uid = request.user.id
        
        expirationTimeInSeconds = 3600 * 24
        currentTimeStamp = int(time.time())
        privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
        role = 1

        if not appId:
            return JsonResponse({'error': 'Agora App ID not configured on server.'}, status=500)

        if not channelName:
            return JsonResponse({'error': 'Channel name is required.'}, status=400)

        # Si no hay certificado, retornar null para token (modo de prueba)
        if not appCertificate:
            print("WARNING: AGORA_APP_CERTIFICATE not configured. Using null token (test mode).")
            return JsonResponse({'token': None, 'appId': appId})

        # Generar token con el certificado
        token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)

        return JsonResponse({'token': token, 'appId': appId})
    except Exception as e:
        # Log the full error to the server console for debugging
        print(f"AGORA TOKEN ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return a specific JSON error to the frontend
        return JsonResponse({'error': f'An unexpected error occurred on the server: {str(e)}'}, status=500)

@login_required
def get_token(request):
    appId = settings.AGORA_APP_ID
    appCertificate = settings.AGORA_APP_CERTIFICATE
    channelName = request.GET.get('channel')
    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600 * 24
    currentTimeStamp = int(time.time())
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    try:
        token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)
        return JsonResponse({'token': token, 'uid': uid})
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def video_lobby(request):
    # Obtener todas las salas, ordenadas por fecha de creación
    groups = VideoCallGroup.objects.all().order_by('-created_at')
    
    # Obtener juegos activos para el formulario de creación
    games = Game.objects.filter(is_started=True, is_finished=False)
    
    return render(request, 'bingo_app/video_lobby.html', {
        'groups': groups, 
        'games': games,
        'AGORA_APP_ID': settings.AGORA_APP_ID
    })


@login_required
@require_http_methods(["GET", "POST"])
def video_groups_api(request):
    if request.method == 'GET':
        groups = VideoCallGroup.objects.all()
        serializer = VideoCallGroupSerializer(groups, many=True)
        return JsonResponse({'groups': serializer.data})

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            if not name:
                return JsonResponse({'error': 'El nombre del grupo es requerido.'}, status=400)

            game_id = data.get('game_id')
            raffle_id = data.get('raffle_id')
            is_public = data.get('is_public', True)
            password = data.get('password', '')
            
            channel_name = f"videocall-group-{uuid.uuid4().hex[:12]}"
            
            group = VideoCallGroup.objects.create(
                name=name,
                created_by=request.user,
                agora_channel_name=channel_name,
                is_public=is_public,
                password=password if not is_public else '',
                game_id=game_id if game_id else None,
                raffle_id=raffle_id if raffle_id else None,
                is_persistent=True  # La sala persiste incluso después de que termine el juego/rifa
            )
            group.participants.add(request.user)
            
            serializer = VideoCallGroupSerializer(group)
            
            # WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'video_lobby',
                {
                    'type': 'video_group_created',
                    'group': serializer.data
                }
            )
            
            return JsonResponse(serializer.data, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Cuerpo de la solicitud inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def verify_video_room_password(request, group_id):
    """API para verificar la contraseña de una sala privada"""
    try:
        group = VideoCallGroup.objects.get(id=group_id)
        
        # Si es pública o el usuario es el creador, no necesita contraseña
        if group.is_public or request.user == group.created_by:
            return JsonResponse({'valid': True})
        
        # Si no tiene contraseña, permitir acceso
        if not group.password:
            return JsonResponse({'valid': True})
        
        # Verificar contraseña
        data = json.loads(request.body)
        password = data.get('password', '')
        
        if password == group.password:
            # Agregar usuario a participantes si la contraseña es correcta
            if request.user not in group.participants.all():
                group.participants.add(request.user)
            return JsonResponse({'valid': True})
        else:
            return JsonResponse({'valid': False, 'error': 'Contraseña incorrecta'}, status=401)
            
    except VideoCallGroup.DoesNotExist:
        return JsonResponse({'valid': False, 'error': 'Sala no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'valid': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["DELETE"])
def delete_video_group(request, group_id):
    """API para eliminar un grupo de videollamada"""
    try:
        group = VideoCallGroup.objects.get(id=group_id)
        
        # Verificar que el usuario sea el creador
        if group.created_by != request.user:
            return JsonResponse({'error': 'Solo el creador puede eliminar esta sala.'}, status=403)
        
        # Notificar a todos los participantes antes de eliminar
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'video_lobby',
            {
                'type': 'video_group_deleted',
                'group_id': group_id
            }
        )
        
        # Eliminar el grupo
        group.delete()
        
        return JsonResponse({'success': True, 'message': 'Sala eliminada correctamente'})
    except VideoCallGroup.DoesNotExist:
        return JsonResponse({'error': 'Sala no encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def videocall_room(request, group_id):
    """Vista para la sala de videollamada con controles completos"""
    try:
        group = VideoCallGroup.objects.get(id=group_id)
        
        # Verificar si es sala privada y requiere contraseña
        if not group.is_public and group.password:
            # Si viene de POST, verificar contraseña
            if request.method == 'POST':
                password = request.POST.get('password', '')
                if password != group.password:
                    messages.error(request, 'Contraseña incorrecta')
                    return redirect('video_lobby')
            # Si es GET y no es el creador, pedir contraseña
            elif request.user != group.created_by:
                return render(request, 'bingo_app/videocall_password.html', {'group': group})
        
        # Agregar usuario a participantes
        if request.user not in group.participants.all():
            group.participants.add(request.user)
        
        context = {
            'group': group,
            'channel_name': group.agora_channel_name,
            'AGORA_APP_ID': settings.AGORA_APP_ID,
        }
        
        return render(request, 'bingo_app/videocall_room.html', context)
    
    except VideoCallGroup.DoesNotExist:
        messages.error(request, 'Sala de videollamada no encontrada')
        return redirect('video_lobby')

@login_required
def create_videocall(request):
    """Vista para crear una nueva sala de videollamada"""
    if request.method == 'POST':
        name = request.POST.get('name')
        is_public = request.POST.get('is_public') == 'on'
        password = request.POST.get('password', '')
        game_id = request.POST.get('game_id')
        
        if not name:
            messages.error(request, 'El nombre de la sala es requerido')
            return redirect('video_lobby')
        
        # Generar nombre de canal único
        channel_name = f"videocall-{uuid.uuid4().hex[:12]}"
        
        # Crear grupo
        group = VideoCallGroup.objects.create(
            name=name,
            created_by=request.user,
            agora_channel_name=channel_name,
            is_public=is_public,
            password=password if not is_public else '',
            game_id=game_id if game_id else None,
            is_persistent=True  # La sala persiste incluso después de que termine el juego
        )
        
        group.participants.add(request.user)
        
        messages.success(request, f'Sala "{name}" creada exitosamente')
        return redirect('videocall_room', group_id=group.id)
    
    # GET: Mostrar formulario
    games = Game.objects.filter(is_started=True, is_finished=False)
    return render(request, 'bingo_app/create_videocall.html', {'games': games})

@login_required
def videocall_popup(request):
    return render(request, 'bingo_app/videocall_popup.html', {
        'agora_app_id': settings.AGORA_APP_ID,
    })


# ===== VISTAS PARA SISTEMA DE TICKETS DE BINGO =====

@login_required
def my_bingo_tickets(request):
    """Vista para mostrar los tickets de bingo del usuario"""
    # Verificar si el sistema de tickets está habilitado
    ticket_settings = BingoTicketSettings.get_settings()
    if not ticket_settings.is_system_active:
        messages.error(request, 'El sistema de tickets de bingo está temporalmente deshabilitado.')
        return redirect('profile')
    
    tickets = BingoTicket.objects.filter(user=request.user).order_by('-created_at')
    
    # Separar tickets por estado
    available_tickets = tickets.filter(is_used=False, expires_at__gt=timezone.now())
    used_tickets = tickets.filter(is_used=True)
    expired_tickets = tickets.filter(is_used=False, expires_at__lte=timezone.now())
    
    context = {
        'available_tickets': available_tickets,
        'used_tickets': used_tickets,
        'expired_tickets': expired_tickets,
        'total_tickets': tickets.count(),
        'available_count': available_tickets.count(),
    }
    
    return render(request, 'bingo_app/my_tickets.html', context)


@login_required
def daily_bingo_schedule(request):
    """Vista para mostrar el horario de bingos diarios"""
    # Verificar si el sistema de tickets está habilitado
    ticket_settings = BingoTicketSettings.get_settings()
    if not ticket_settings.is_system_active:
        messages.error(request, 'El sistema de bingos diarios está temporalmente deshabilitado.')
        return redirect('profile')
    
    schedules = DailyBingoSchedule.objects.all().order_by('time_slot')
    
    # Obtener tickets disponibles del usuario para cada horario
    user_tickets = BingoTicket.objects.filter(
        user=request.user,
        is_used=False,
        expires_at__gt=timezone.now()
    )
    
    context = {
        'schedules': schedules,
        'ticket_settings': ticket_settings,
        'user_tickets': user_tickets,
        'available_tickets_count': user_tickets.count(),
    }
    
    return render(request, 'bingo_app/daily_bingo_schedule.html', context)


@login_required
def join_daily_bingo(request, schedule_id):
    """Vista para unirse a un bingo diario usando un ticket"""
    schedule = get_object_or_404(DailyBingoSchedule, id=schedule_id)
    ticket_settings = BingoTicketSettings.get_settings()
    
    if not ticket_settings.is_system_active:
        messages.error(request, "El sistema de tickets está desactivado.")
        return redirect('daily_bingo_schedule')
    
    if not schedule.is_active:
        messages.error(request, "Este horario de bingo está desactivado.")
        return redirect('daily_bingo_schedule')
    
    # Verificar si el usuario tiene tickets disponibles
    available_ticket = BingoTicket.objects.filter(
        user=request.user,
        is_used=False,
        expires_at__gt=timezone.now()
    ).first()
    
    if not available_ticket:
        messages.error(request, "No tienes tickets disponibles para unirte al bingo.")
        return redirect('daily_bingo_schedule')
    
    # Verificar si ya hay un juego activo para este horario
    now = timezone.now()
    today = now.date()
    
    # Buscar si ya existe un juego para este horario hoy
    existing_game = Game.objects.filter(
        organizer__is_admin=True,  # Los bingos diarios son organizados por admin
        created_at__date=today,
        name__icontains=schedule.get_time_slot_display()
    ).first()
    
    if existing_game and existing_game.is_started and not existing_game.is_finished:
        messages.info(request, f"Ya hay un bingo activo para este horario. Únete al juego: {existing_game.name}")
        return redirect('game_room', game_id=existing_game.id)
    
    # Crear un nuevo juego para este horario si no existe
    if not existing_game:
        try:
            with transaction.atomic():
                # Crear el juego
                game = Game.objects.create(
                    name=f"Bingo {schedule.get_time_slot_display()} - {today.strftime('%d/%m/%Y')}",
                    organizer=User.objects.filter(is_admin=True).first(),  # Admin organiza los bingos diarios
                    base_prize=schedule.prize_amount,
                    prize=schedule.prize_amount,
                    card_price=0.00,  # Gratis con ticket
                    entry_price=0.00,  # Gratis con ticket
                    max_cards_sold=schedule.max_players,
                    description=f"Bingo diario gratuito - {schedule.description or 'Usa tu ticket para participar'}",
                    is_started=False,
                    is_finished=False,
                    allows_printable_cards=True
                )
                
                # Usar el ticket
                available_ticket.is_used = True
                available_ticket.used_in_game = game
                available_ticket.used_at = timezone.now()
                available_ticket.save()
                
                # Crear el jugador
                player, created = Player.objects.get_or_create(user=request.user, game=game)
                
                messages.success(request, f"¡Te has unido al bingo {schedule.get_time_slot_display()}! Tu ticket ha sido usado.")
                return redirect('game_room', game_id=game.id)
                
        except Exception as e:
            messages.error(request, f"Error al crear el juego: {str(e)}")
            return redirect('daily_bingo_schedule')
    else:
        # Usar el ticket para unirse al juego existente
        try:
            with transaction.atomic():
                available_ticket.is_used = True
                available_ticket.used_in_game = existing_game
                available_ticket.used_at = timezone.now()
                available_ticket.save()
                
                # Crear el jugador si no existe
                player, created = Player.objects.get_or_create(user=request.user, game=existing_game)
                
                messages.success(request, f"¡Te has unido al bingo {schedule.get_time_slot_display()}! Tu ticket ha sido usado.")
                return redirect('game_room', game_id=existing_game.id)
                
        except Exception as e:
            messages.error(request, f"Error al unirse al juego: {str(e)}")
            return redirect('daily_bingo_schedule')


@staff_member_required
def admin_ticket_settings(request):
    """Vista de administración para configurar el sistema de tickets"""
    ticket_settings = BingoTicketSettings.get_settings()
    
    if request.method == 'POST':
        ticket_settings.is_system_active = request.POST.get('is_system_active') == 'on'
        ticket_settings.referral_ticket_bonus = int(request.POST.get('referral_ticket_bonus', 1))
        ticket_settings.referred_ticket_bonus = int(request.POST.get('referred_ticket_bonus', 1))
        ticket_settings.ticket_expiration_days = int(request.POST.get('ticket_expiration_days', 7))
        ticket_settings.save()
        
        messages.success(request, "Configuración de tickets actualizada correctamente.")
        return redirect('admin_ticket_settings')
    
    context = {
        'ticket_settings': ticket_settings,
    }
    
    return render(request, 'bingo_app/admin/ticket_settings.html', context)


@staff_member_required
def admin_daily_schedule(request):
    """Vista de administración para gestionar horarios de bingo diario"""
    schedules = DailyBingoSchedule.objects.all().order_by('time_slot')
    
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        action = request.POST.get('action')
        
        if schedule_id and action:
            schedule = get_object_or_404(DailyBingoSchedule, id=schedule_id)
            
            if action == 'toggle_active':
                schedule.is_active = not schedule.is_active
                schedule.save()
                messages.success(request, f"Horario {schedule.get_time_slot_display()} {'activado' if schedule.is_active else 'desactivado'}.")
            
            elif action == 'update_settings':
                schedule.max_players = int(request.POST.get('max_players', 50))
                schedule.prize_amount = Decimal(request.POST.get('prize_amount', 10.00))
                schedule.description = request.POST.get('description', '')
                schedule.save()
                messages.success(request, f"Configuración del horario {schedule.get_time_slot_display()} actualizada.")
        
        return redirect('admin_daily_schedule')
    
    context = {
        'schedules': schedules,
    }
    
    return render(request, 'bingo_app/admin/daily_schedule.html', context)


@staff_member_required
@require_http_methods(["POST"])
def ai_chatbot_api(request):
    """API endpoint para el chatbot de IA"""
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        
        if not question:
            return JsonResponse({'error': 'La pregunta no puede estar vacía'}, status=400)
        
        # Obtener contexto del dashboard
        context = _get_admin_dashboard_context_mejorado(None, None)
        
        # Usar asistente local por defecto (siempre funciona)
        # Solo intentar Gemini si está explícitamente configurado
        use_gemini = False
        if ai_assistant.is_available():
            try:
                # Verificar que Gemini funciona realmente
                test_response = ai_assistant.answer_question("test", {})
                if test_response and 'quota_error' not in str(test_response).lower():
                    use_gemini = True
            except:
                use_gemini = False
        
        if use_gemini:
            try:
                response = ai_assistant.answer_question(question, context)
                if 'quota_error' in str(response).lower() or 'cuota' in str(response).lower():
                    raise Exception("Gemini quota error")
                response['ai_type'] = 'gemini'
                return JsonResponse({
                    'success': True,
                    'response': response
                })
            except Exception as e:
                logger.warning(f"Error con Gemini, usando asistente local: {str(e)}")
                # Fallback a asistente local
                response = smart_assistant.answer_question(question, context)
                response['ai_type'] = 'local'
                return JsonResponse({
                    'success': True,
                    'response': response
                })
        else:
            # Usar asistente local (basado en reglas, siempre funciona)
            response = smart_assistant.answer_question(question, context)
            response['ai_type'] = 'local'
            return JsonResponse({
                'success': True,
                'response': response
            })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Error en chatbot de IA: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
def ai_generate_report(request):
    """Genera un reporte automático usando IA"""
    report_type = request.GET.get('type', 'daily')
    
    if report_type not in ['daily', 'weekly', 'monthly']:
        report_type = 'daily'
    
    try:
        context = _get_admin_dashboard_context_mejorado(None, None)
        
        # Intentar usar IA real (Gemini) primero
        if ai_assistant.is_available():
            try:
                report = ai_assistant.generate_report(context, report_type)
                return JsonResponse({
                    'success': True,
                    'report': report,
                    'type': report_type,
                    'ai_type': 'gemini'
                })
            except Exception as e:
                logger.warning(f"Error con Gemini, usando asistente local: {str(e)}")
                # Fallback a asistente local
                report = smart_assistant.generate_report(context, report_type)
                return JsonResponse({
                    'success': True,
                    'report': report,
                    'type': report_type,
                    'ai_type': 'local'
                })
        else:
            # Usar asistente local
            report = smart_assistant.generate_report(context, report_type)
            return JsonResponse({
                'success': True,
                'report': report,
                'type': report_type,
                'ai_type': 'local'
            })
    except Exception as e:
        logger.error(f"Error generando reporte: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
def ai_analysis_api(request):
    """API endpoint para obtener análisis de IA"""
    try:
        context = _get_admin_dashboard_context_mejorado(None, None)
        
        # Intentar usar IA real (Gemini) primero
        if ai_assistant.is_available():
            try:
                analysis = ai_assistant.analyze_dashboard_metrics(context)
                return JsonResponse({
                    'success': True,
                    'analysis': analysis,
                    'available': True,
                    'ai_type': 'gemini'
                })
            except Exception as e:
                logger.warning(f"Error con Gemini, usando asistente local: {str(e)}")
                # Fallback a asistente local
                analysis = smart_assistant.analyze_dashboard_metrics(context)
                return JsonResponse({
                    'success': True,
                    'analysis': analysis,
                    'available': True,
                    'ai_type': 'local'
                })
        else:
            # Usar asistente local
            analysis = smart_assistant.analyze_dashboard_metrics(context)
            return JsonResponse({
                'success': True,
                'analysis': analysis,
                'available': True,
                'ai_type': 'local'
            })
    except Exception as e:
        logger.error(f"Error en análisis de IA: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'available': False
        }, status=500)


def admin_ticket_stats(request):
    """Vista de estadísticas de tickets para administradores"""
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Estadísticas generales
    total_tickets = BingoTicket.objects.count()
    used_tickets = BingoTicket.objects.filter(is_used=True).count()
    available_tickets = BingoTicket.objects.filter(is_used=False, expires_at__gt=timezone.now()).count()
    expired_tickets = BingoTicket.objects.filter(is_used=False, expires_at__lte=timezone.now()).count()
    
    # Tickets por tipo
    tickets_by_type = BingoTicket.objects.values('ticket_type').annotate(count=Count('id')).order_by('-count')
    
    # Tickets por usuario (top 10)
    top_users = BingoTicket.objects.values('user__username').annotate(
        total=Count('id'),
        used=Count('id', filter=Q(is_used=True)),
        available=Count('id', filter=Q(is_used=False, expires_at__gt=timezone.now()))
    ).order_by('-total')[:10]
    
    # Tickets creados en los últimos 30 días
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_tickets = BingoTicket.objects.filter(created_at__gte=thirty_days_ago).count()
    
    context = {
        'total_tickets': total_tickets,
        'used_tickets': used_tickets,
        'available_tickets': available_tickets,
        'expired_tickets': expired_tickets,
        'tickets_by_type': tickets_by_type,
        'top_users': top_users,
        'recent_tickets': recent_tickets,
    }
    
    return render(request, 'bingo_app/admin/ticket_stats.html', context)

@staff_member_required
def test_email_view(request):
    """Vista para probar el envío de emails con SendGrid"""
    from django.core.mail import send_mail
    from django.conf import settings
    from datetime import datetime
    
    result_message = None
    error_message = None
    
    if request.method == 'POST':
        email_destino = request.POST.get('email', settings.DEFAULT_FROM_EMAIL)
        
        try:
            subject = '🧪 Prueba de Email - Bingo JyM'
            fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            message = f'''
Hola,

Este es un email de prueba para verificar que SendGrid está funcionando correctamente.

Si recibes este mensaje, significa que:
✅ SendGrid está configurado correctamente
✅ La API key es válida
✅ Los emails se pueden enviar desde el sistema

Fecha: {fecha}
Sistema: Bingo JyM - Producción
            '''
            
            from_email = settings.DEFAULT_FROM_EMAIL
            
            result = send_mail(
                subject,
                message,
                from_email,
                [email_destino],
                fail_silently=False,
            )
            
            if result == 1:
                result_message = f'✅ Email enviado exitosamente a {email_destino}! Revisa tu bandeja de entrada (y spam).'
            else:
                error_message = f'⚠️ Email no se envió (resultado: {result})'
                
        except Exception as e:
            error_message = f'❌ Error al enviar email: {str(e)}'
    
    context = {
        'result_message': result_message,
        'error_message': error_message,
        'default_email': settings.DEFAULT_FROM_EMAIL,
    }
    
    return render(request, 'bingo_app/admin/test_email.html', context)


# ========== VISTAS DE CUENTAS POR COBRAR ==========

@staff_member_required
def admin_accounts_receivable(request):
    """Vista para administradores: listar todas las cuentas por cobrar y gestionar toggle"""
    settings_obj = PercentageSettings.objects.first()
    if not settings_obj:
        settings_obj = PercentageSettings.objects.create()
    
    # Listar todas las cuentas por cobrar con annotations para evitar consultas N+1
    from django.db.models import Sum, F
    accounts = AccountsReceivable.objects.all().select_related('debtor', 'organizer').annotate(
        total_paid_calculated=Sum('payments__amount')
    ).prefetch_related('payments')
    
    # Calcular totales usando agregaciones (más eficiente)
    total_amount = AccountsReceivable.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_paid = AccountsReceivablePayment.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_remaining = total_amount - total_paid
    
    # Manejar activación/desactivación del toggle
    if request.method == 'POST' and 'toggle_enabled' in request.POST:
        settings_obj.accounts_receivable_enabled = not settings_obj.accounts_receivable_enabled
        settings_obj.save()
        messages.success(
            request, 
            f'Cuentas por Cobrar {"activado" if settings_obj.accounts_receivable_enabled else "desactivado"} para organizadores.'
        )
        return redirect('admin_accounts_receivable')
    
    context = {
        'accounts': accounts,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'is_enabled': settings_obj.accounts_receivable_enabled,
    }
    
    return render(request, 'bingo_app/admin/accounts_receivable.html', context)


@login_required
def organizer_accounts_receivable(request):
    """Vista para organizadores: listar sus cuentas por cobrar"""
    # Verificar si el usuario es organizador
    if not request.user.is_organizer:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('lobby')
    
    # Verificar si el módulo está activado
    settings_obj = PercentageSettings.objects.first()
    if not settings_obj or not settings_obj.accounts_receivable_enabled:
        messages.error(request, 'El módulo de Cuentas por Cobrar está desactivado.')
        return redirect('organizer_dashboard')
    
    organizer = request.user
    
    # Listar cuentas por cobrar del organizador con annotations para evitar consultas N+1
    accounts = AccountsReceivable.objects.filter(organizer=organizer).select_related('debtor').annotate(
        total_paid_calculated=Sum('payments__amount')
    ).prefetch_related('payments')
    
    # Calcular totales usando agregaciones (más eficiente)
    total_amount = AccountsReceivable.objects.filter(organizer=organizer).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    # Obtener IDs de cuentas del organizador para calcular pagos
    account_ids = list(accounts.values_list('id', flat=True))
    total_paid = AccountsReceivablePayment.objects.filter(account_receivable_id__in=account_ids).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_remaining = total_amount - total_paid
    
    # Obtener usuarios para el select (excluyendo al organizador)
    users = User.objects.exclude(id=organizer.id).order_by('username')
    
    # Obtener métodos de pago activos
    payment_methods = BankAccount.objects.filter(is_active=True)
    
    context = {
        'accounts': accounts,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'users': users,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'bingo_app/organizer/accounts_receivable.html', context)


@login_required
@require_POST
def create_account_receivable(request):
    """Vista para crear una nueva cuenta por cobrar (AJAX)"""
    if not request.user.is_organizer:
        return JsonResponse({'success': False, 'error': 'No tienes permisos para realizar esta acción.'}, status=403)
    
    # Verificar si el módulo está activado
    settings_obj = PercentageSettings.objects.first()
    if not settings_obj or not settings_obj.accounts_receivable_enabled:
        return JsonResponse({'success': False, 'error': 'El módulo está desactivado.'}, status=403)
    
    form = AccountsReceivableForm(request.POST, organizer=request.user)
    
    if form.is_valid():
        account = form.save(commit=False)
        account.organizer = request.user
        account.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cuenta por cobrar creada exitosamente.',
            'account_id': account.id
        })
    else:
        errors = form.errors.as_json()
        return JsonResponse({'success': False, 'errors': errors}, status=400)


@login_required
def account_receivable_detail(request, account_id):
    """Vista para ver el detalle de una cuenta por cobrar"""
    account = get_object_or_404(AccountsReceivable, id=account_id)
    
    # Verificar permisos
    if not request.user.is_organizer and not request.user.is_admin:
        messages.error(request, 'No tienes permisos para ver esta cuenta.')
        return redirect('lobby')
    
    if request.user.is_organizer and account.organizer != request.user:
        messages.error(request, 'No tienes permisos para ver esta cuenta.')
        return redirect('organizer_accounts_receivable')
    
    # Obtener pagos
    payments = account.payments.all().select_related('payment_method')
    
    # Obtener métodos de pago activos
    payment_methods = BankAccount.objects.filter(is_active=True)
    
    context = {
        'account': account,
        'payments': payments,
        'total_paid': account.total_paid,
        'remaining_balance': account.remaining_balance,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'bingo_app/organizer/account_receivable_detail.html', context)


@login_required
@require_POST
def add_payment_to_account(request, account_id):
    """Vista para agregar un pago/abono a una cuenta por cobrar"""
    account = get_object_or_404(AccountsReceivable, id=account_id)
    
    # Verificar permisos
    if not request.user.is_organizer and not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'No tienes permisos.'}, status=403)
    
    if request.user.is_organizer and account.organizer != request.user:
        return JsonResponse({'success': False, 'error': 'No tienes permisos.'}, status=403)
    
    form = AccountsReceivablePaymentForm(
        request.POST, 
        request.FILES, 
        account_receivable=account
    )
    
    if form.is_valid():
        # Validar que el monto no exceda el saldo pendiente
        payment_amount = form.cleaned_data['amount']
        if payment_amount > account.remaining_balance:
            return JsonResponse({
                'success': False,
                'error': f'El monto del abono (${payment_amount}) no puede exceder el saldo pendiente (${account.remaining_balance})'
            }, status=400)
        
        payment = form.save(commit=False)
        payment.account_receivable = account
        payment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Pago registrado exitosamente.',
            'payment_id': payment.id,
            'remaining_balance': float(account.remaining_balance)
        })
    else:
        errors = form.errors.as_json()
        return JsonResponse({'success': False, 'errors': errors}, status=400)


@staff_member_required
def edit_package_prices(request):
    """
    Vista para editar precios de los paquetes preconfigurados
    """
    templates = PackageTemplate.objects.all().order_by('package_type')
    
    if request.method == 'POST':
        for template in templates:
            price_key = f'price_{template.package_type}'
            commission_key = f'commission_{template.package_type}'
            
            if price_key in request.POST:
                try:
                    new_price = Decimal(request.POST[price_key])
                    if new_price < 0:
                        messages.error(request, f'El precio no puede ser negativo para {template.name}')
                        continue
                    template.current_monthly_price = new_price
                except (ValueError, Exception) as e:
                    messages.error(request, f'Precio inválido para {template.name}: {str(e)}')
            
            if commission_key in request.POST:
                try:
                    new_commission = Decimal(request.POST[commission_key])
                    if new_commission < 0 or new_commission > 100:
                        messages.error(request, f'La comisión debe estar entre 0 y 100 para {template.name}')
                        continue
                    template.current_commission_rate = new_commission
                except (ValueError, Exception) as e:
                    messages.error(request, f'Comisión inválida para {template.name}: {str(e)}')
            
            template.save()
        
        messages.success(request, 'Precios actualizados correctamente')
        return redirect('edit_package_prices')
    
    return render(request, 'bingo_app/admin/edit_package_prices.html', {
        'templates': templates
    })


@staff_member_required
@require_POST
def reset_package_prices(request):
    """
    Restaura los precios a los valores por defecto
    """
    templates = PackageTemplate.objects.all()
    for template in templates:
        template.current_monthly_price = template.default_monthly_price
        template.current_commission_rate = template.default_commission_rate
        template.save()
    
    messages.success(request, 'Precios restaurados a los valores por defecto')
    return redirect('edit_package_prices')


# ============================================================================
# VISTAS DE GESTIÓN DE FRANQUICIAS (SUPER ADMIN)
# ============================================================================

@staff_member_required
def franchise_list(request):
    """
    Lista todas las franquicias (solo super admin)
    """
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para ver esta página')
        return redirect('home')
    
    franchises = Franchise.objects.all().select_related('owner', 'package_template').order_by('-created_at')
    
    # Estadísticas
    total_franchises = franchises.count()
    active_franchises = franchises.filter(is_active=True).count()
    
    return render(request, 'bingo_app/admin/franchise_list.html', {
        'franchises': franchises,
        'total_franchises': total_franchises,
        'active_franchises': active_franchises,
    })


@staff_member_required
def franchise_create(request):
    """
    Crear una nueva franquicia (solo super admin)
    """
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para crear franquicias')
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        owner_username = request.POST.get('owner_username')
        package_template_id = request.POST.get('package_template')
        
        # Validaciones
        if not all([name, slug, owner_username, package_template_id]):
            messages.error(request, 'Todos los campos son obligatorios')
            return redirect('franchise_create')
        
        # Verificar que el slug no exista
        if Franchise.objects.filter(slug=slug).exists():
            messages.error(request, 'Este slug ya está en uso')
            return redirect('franchise_create')
        
        # Buscar el usuario propietario
        try:
            owner = User.objects.get(username=owner_username)
        except User.DoesNotExist:
            messages.error(request, f'Usuario "{owner_username}" no encontrado')
            return redirect('franchise_create')
        
        # Verificar que el usuario no tenga ya una franquicia
        if hasattr(owner, 'owned_franchise'):
            messages.error(request, f'El usuario "{owner_username}" ya tiene una franquicia asignada')
            return redirect('franchise_create')
        
        # Obtener el paquete
        try:
            package_template = PackageTemplate.objects.get(id=package_template_id)
        except PackageTemplate.DoesNotExist:
            messages.error(request, 'Paquete no encontrado')
            return redirect('franchise_create')
        
        # Crear la franquicia
        try:
            franchise = Franchise.objects.create(
                name=name,
                slug=slug,
                owner=owner,
                package_template=package_template,
                monthly_price=package_template.current_monthly_price,
                commission_rate=package_template.current_commission_rate,
                created_by=request.user,
                is_active=True
            )
            
            # Asignar la franquicia al usuario
            owner.franchise = franchise
            owner.is_organizer = True
            owner.save()
            
            # Crear el manual vacío
            FranchiseManual.objects.create(
                franchise=franchise,
                content='',
                updated_by=request.user
            )
            
            messages.success(request, f'Franquicia "{name}" creada exitosamente')
            return redirect('franchise_detail', franchise_id=franchise.id)
        except Exception as e:
            messages.error(request, f'Error al crear la franquicia: {str(e)}')
            return redirect('franchise_create')
    
    # GET: Mostrar formulario
    packages = PackageTemplate.objects.filter(is_active=True).order_by('package_type')
    return render(request, 'bingo_app/admin/franchise_create.html', {
        'packages': packages
    })


@staff_member_required
def franchise_detail(request, franchise_id):
    """
    Ver detalles de una franquicia (solo super admin)
    """
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para ver esta página')
        return redirect('home')
    
    franchise = get_object_or_404(Franchise, id=franchise_id)
    
    # Estadísticas de la franquicia
    total_games = Game.objects.filter(franchise=franchise).count()
    total_raffles = Raffle.objects.filter(franchise=franchise).count()
    total_users = User.objects.filter(franchise=franchise).count()
    total_credit_requests = CreditRequest.objects.filter(franchise=franchise).count()
    total_withdrawal_requests = WithdrawalRequest.objects.filter(franchise=franchise).count()
    
    return render(request, 'bingo_app/admin/franchise_detail.html', {
        'franchise': franchise,
        'total_games': total_games,
        'total_raffles': total_raffles,
        'total_users': total_users,
        'total_credit_requests': total_credit_requests,
        'total_withdrawal_requests': total_withdrawal_requests,
    })


@staff_member_required
def franchise_edit(request, franchise_id):
    """
    Editar una franquicia (solo super admin)
    """
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para editar franquicias')
        return redirect('home')
    
    franchise = get_object_or_404(Franchise, id=franchise_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validaciones
        if not name or not slug:
            messages.error(request, 'Nombre y slug son obligatorios')
            return redirect('franchise_edit', franchise_id=franchise_id)
        
        # Verificar que el slug no esté en uso por otra franquicia
        if Franchise.objects.filter(slug=slug).exclude(id=franchise_id).exists():
            messages.error(request, 'Este slug ya está en uso por otra franquicia')
            return redirect('franchise_edit', franchise_id=franchise_id)
        
        # Actualizar
        franchise.name = name
        franchise.slug = slug
        franchise.is_active = is_active
        franchise.save()
        
        messages.success(request, f'Franquicia "{name}" actualizada exitosamente')
        return redirect('franchise_detail', franchise_id=franchise_id)
    
    # GET: Mostrar formulario
    return render(request, 'bingo_app/admin/franchise_edit.html', {
        'franchise': franchise
    })


@staff_member_required
def franchise_change_image(request, franchise_id):
    """
    Cambiar logo o imagen de una franquicia (solo super admin)
    """
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para cambiar imágenes')
        return redirect('home')
    
    franchise = get_object_or_404(Franchise, id=franchise_id)
    
    if request.method == 'POST':
        if 'logo' in request.FILES:
            franchise.logo = request.FILES['logo']
            franchise.save()
            messages.success(request, 'Logo actualizado exitosamente')
        
        if 'image' in request.FILES:
            franchise.image = request.FILES['image']
            franchise.save()
            messages.success(request, 'Imagen actualizada exitosamente')
        
        return redirect('franchise_detail', franchise_id=franchise_id)
    
    return render(request, 'bingo_app/admin/franchise_change_image.html', {
        'franchise': franchise
    })


# ============================================================================
# PANEL PARA FRANQUICIADO (PROPIETARIO DE FRANQUICIA)
# ============================================================================

@login_required
def franchise_owner_dashboard(request):
    """
    Dashboard para el propietario de una franquicia
    Solo puede ver y gestionar los datos de su propia franquicia
    """
    # Verificar que el usuario es propietario de una franquicia
    if not hasattr(request.user, 'owned_franchise'):
        messages.error(request, 'No eres propietario de ninguna franquicia')
        return redirect('home')
    
    franchise = request.user.owned_franchise
    
    # Verificar que la franquicia esté activa
    if not franchise.is_active:
        messages.warning(request, 'Tu franquicia está inactiva. Contacta al administrador.')
    
    # Estadísticas de la franquicia
    total_games = Game.objects.filter(franchise=franchise).count()
    active_games = Game.objects.filter(franchise=franchise, is_active=True, is_started=False).count()
    total_raffles = Raffle.objects.filter(franchise=franchise).count()
    active_raffles = Raffle.objects.filter(franchise=franchise, status__in=['WAITING', 'IN_PROGRESS']).count()
    total_users = User.objects.filter(franchise=franchise).count()
    
    # Solicitudes pendientes de crédito de usuarios de esta franquicia
    pending_credit_requests = CreditRequest.objects.filter(
        franchise=franchise,
        status='pending'
    ).select_related('user').order_by('-created_at')[:10]
    
    # Solicitudes pendientes de retiro de usuarios de esta franquicia
    pending_withdrawal_requests = WithdrawalRequest.objects.filter(
        franchise=franchise,
        status='PENDING'
    ).select_related('user').order_by('-created_at')[:10]
    
    # Total de créditos en la franquicia (suma de balances de usuarios)
    total_credits = User.objects.filter(franchise=franchise).aggregate(
        total=Sum('credit_balance')
    )['total'] or Decimal('0.00')
    
    # Lista de usuarios registrados (últimos 20)
    recent_users = User.objects.filter(franchise=franchise).order_by('-date_joined')[:20]
    
    # Estadísticas de solicitudes
    total_credit_requests = CreditRequest.objects.filter(franchise=franchise).count()
    approved_credit_requests = CreditRequest.objects.filter(franchise=franchise, status='approved').count()
    total_withdrawal_requests = WithdrawalRequest.objects.filter(franchise=franchise).count()
    completed_withdrawal_requests = WithdrawalRequest.objects.filter(franchise=franchise, status='COMPLETED').count()
    
    return render(request, 'bingo_app/franchise_owner/dashboard.html', {
        'franchise': franchise,
        'total_games': total_games,
        'active_games': active_games,
        'total_raffles': total_raffles,
        'active_raffles': active_raffles,
        'total_users': total_users,
        'pending_credit_requests': pending_credit_requests,
        'pending_withdrawal_requests': pending_withdrawal_requests,
        'total_credits': total_credits,
        'recent_users': recent_users,
        'total_credit_requests': total_credit_requests,
        'approved_credit_requests': approved_credit_requests,
        'total_withdrawal_requests': total_withdrawal_requests,
        'completed_withdrawal_requests': completed_withdrawal_requests,
    })


@login_required
def franchise_owner_credit_requests(request):
    """
    Lista de solicitudes de crédito de usuarios de la franquicia
    """
    if not hasattr(request.user, 'owned_franchise'):
        messages.error(request, 'No eres propietario de ninguna franquicia')
        return redirect('home')
    
    franchise = request.user.owned_franchise
    
    credit_requests = CreditRequest.objects.filter(
        franchise=franchise
    ).select_related('user', 'payment_method').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        credit_requests = credit_requests.filter(status=status_filter)
    
    return render(request, 'bingo_app/franchise_owner/credit_requests.html', {
        'franchise': franchise,
        'credit_requests': credit_requests,
        'status_filter': status_filter,
    })


@login_required
def franchise_owner_process_credit(request, request_id):
    """
    Procesar (aprobar/rechazar) una solicitud de crédito de un usuario de la franquicia
    """
    if not hasattr(request.user, 'owned_franchise'):
        messages.error(request, 'No eres propietario de ninguna franquicia')
        return redirect('home')
    
    franchise = request.user.owned_franchise
    credit_request = get_object_or_404(
        CreditRequest,
        id=request_id,
        franchise=franchise
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            try:
                with transaction.atomic():
                    user = credit_request.user
                    user.credit_balance += credit_request.amount
                    user.save()
                    
                    Transaction.objects.create(
                        user=user,
                        amount=credit_request.amount,
                        transaction_type='ADMIN_ADD',
                        description=f"Recarga aprobada por franquiciado: {request.user.username}"
                    )
                    
                    credit_request.status = 'approved'
                    credit_request.processed_at = timezone.now()
                    credit_request.admin_notes = f"Aprobado por franquiciado {request.user.username}"
                    credit_request.save()
                
                messages.success(request, f'Solicitud de crédito aprobada. ${credit_request.amount} agregados a {user.username}')
            except Exception as e:
                messages.error(request, f'Error al aprobar la solicitud: {str(e)}')
        
        elif action == 'reject':
            credit_request.status = 'rejected'
            credit_request.processed_at = timezone.now()
            credit_request.admin_notes = f"Rechazado por franquiciado {request.user.username}. Razón: {request.POST.get('rejection_reason', 'Sin razón especificada')}"
            credit_request.save()
            messages.success(request, 'Solicitud de crédito rechazada')
        
        return redirect('franchise_owner_credit_requests')
    
    return render(request, 'bingo_app/franchise_owner/process_credit.html', {
        'franchise': franchise,
        'credit_request': credit_request,
    })


@login_required
def franchise_owner_withdrawal_requests(request):
    """
    Lista de solicitudes de retiro de usuarios de la franquicia
    """
    if not hasattr(request.user, 'owned_franchise'):
        messages.error(request, 'No eres propietario de ninguna franquicia')
        return redirect('home')
    
    franchise = request.user.owned_franchise
    
    withdrawal_requests = WithdrawalRequest.objects.filter(
        franchise=franchise
    ).select_related('user').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        withdrawal_requests = withdrawal_requests.filter(status=status_filter)
    
    return render(request, 'bingo_app/franchise_owner/withdrawal_requests.html', {
        'franchise': franchise,
        'withdrawal_requests': withdrawal_requests,
        'status_filter': status_filter,
    })


@login_required
def franchise_owner_process_withdrawal(request, request_id):
    """
    Procesar (aprobar/rechazar) una solicitud de retiro de un usuario de la franquicia
    """
    if not hasattr(request.user, 'owned_franchise'):
        messages.error(request, 'No eres propietario de ninguna franquicia')
        return redirect('home')
    
    franchise = request.user.owned_franchise
    withdrawal_request = get_object_or_404(
        WithdrawalRequest,
        id=request_id,
        franchise=franchise
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            if withdrawal_request.user.credit_balance >= withdrawal_request.amount:
                try:
                    with transaction.atomic():
                        withdrawal_request.user.credit_balance -= withdrawal_request.amount
                        withdrawal_request.user.save()
                        
                        Transaction.objects.create(
                            user=withdrawal_request.user,
                            amount=-withdrawal_request.amount,
                            transaction_type='WITHDRAWAL',
                            description=f"Retiro aprobado por franquiciado: {request.user.username}"
                        )
                        
                        withdrawal_request.status = 'COMPLETED'
                        withdrawal_request.processed_at = timezone.now()
                        withdrawal_request.admin_notes = f"Procesado por franquiciado {request.user.username}"
                        withdrawal_request.save()
                    
                    messages.success(request, f'Retiro aprobado. ${withdrawal_request.amount} descontados de {withdrawal_request.user.username}')
                except Exception as e:
                    messages.error(request, f'Error al procesar el retiro: {str(e)}')
            else:
                messages.error(request, f'El usuario {withdrawal_request.user.username} no tiene suficiente saldo')
        
        elif action == 'reject':
            withdrawal_request.status = 'REJECTED'
            withdrawal_request.processed_at = timezone.now()
            withdrawal_request.admin_notes = f"Rechazado por franquiciado {request.user.username}. Razón: {request.POST.get('rejection_reason', 'Sin razón especificada')}"
            withdrawal_request.save()
            messages.success(request, 'Solicitud de retiro rechazada')
        
        return redirect('franchise_owner_withdrawal_requests')
    
    return render(request, 'bingo_app/franchise_owner/process_withdrawal.html', {
        'franchise': franchise,
        'withdrawal_request': withdrawal_request,
    })


# ============================================================================
# VISTAS DE GESTIÓN DE CUENTAS BANCARIAS PARA PROPIETARIOS DE FRANQUICIA
# ============================================================================

@login_required
def franchise_owner_bank_accounts(request):
    """
    Lista las cuentas bancarias de la franquicia del propietario
    """
    if not hasattr(request.user, 'owned_franchise'):
        messages.error(request, 'No eres propietario de ninguna franquicia')
        return redirect('home')
    
    franchise = request.user.owned_franchise
    bank_accounts = BankAccount.objects.filter(franchise=franchise).order_by('-order', 'title')
    
    return render(request, 'bingo_app/franchise_owner/bank_accounts/list.html', {
        'franchise': franchise,
        'bank_accounts': bank_accounts,
    })


@login_required
def franchise_owner_create_bank_account(request):
    """
    Crear una nueva cuenta bancaria para la franquicia
    """
    if not hasattr(request.user, 'owned_franchise'):
        messages.error(request, 'No eres propietario de ninguna franquicia')
        return redirect('home')
    
    franchise = request.user.owned_franchise
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            bank_account = form.save(commit=False)
            bank_account.franchise = franchise
            bank_account.save()
            messages.success(request, f'Cuenta bancaria "{bank_account.title}" creada exitosamente')
            return redirect('franchise_owner_bank_accounts')
    else:
        form = PaymentMethodForm()
    
    return render(request, 'bingo_app/franchise_owner/bank_accounts/create.html', {
        'franchise': franchise,
        'form': form,
    })


@login_required
def franchise_owner_edit_bank_account(request, account_id):
    """
    Editar una cuenta bancaria de la franquicia
    """
    if not hasattr(request.user, 'owned_franchise'):
        messages.error(request, 'No eres propietario de ninguna franquicia')
        return redirect('home')
    
    franchise = request.user.owned_franchise
    bank_account = get_object_or_404(
        BankAccount,
        id=account_id,
        franchise=franchise
    )
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=bank_account)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cuenta bancaria "{bank_account.title}" actualizada exitosamente')
            return redirect('franchise_owner_bank_accounts')
    else:
        form = PaymentMethodForm(instance=bank_account)
    
    return render(request, 'bingo_app/franchise_owner/bank_accounts/edit.html', {
        'franchise': franchise,
        'form': form,
        'bank_account': bank_account,
    })


@login_required
@require_POST
def franchise_owner_delete_bank_account(request, account_id):
    """
    Eliminar una cuenta bancaria de la franquicia
    """
    if not hasattr(request.user, 'owned_franchise'):
        messages.error(request, 'No eres propietario de ninguna franquicia')
        return redirect('home')
    
    franchise = request.user.owned_franchise
    bank_account = get_object_or_404(
        BankAccount,
        id=account_id,
        franchise=franchise
    )
    
    title = bank_account.title
    bank_account.delete()
    messages.success(request, f'Cuenta bancaria "{title}" eliminada exitosamente')
    
    return redirect('franchise_owner_bank_accounts')


@login_required
@require_POST
def franchise_owner_toggle_bank_account(request, account_id):
    """
    Activar/desactivar una cuenta bancaria de la franquicia
    """
    if not hasattr(request.user, 'owned_franchise'):
        messages.error(request, 'No eres propietario de ninguna franquicia')
        return redirect('home')
    
    franchise = request.user.owned_franchise
    bank_account = get_object_or_404(
        BankAccount,
        id=account_id,
        franchise=franchise
    )
    
    bank_account.is_active = not bank_account.is_active
    bank_account.save()
    
    status = 'activada' if bank_account.is_active else 'desactivada'
    messages.success(request, f'Cuenta bancaria "{bank_account.title}" {status} exitosamente')
    
    return redirect('franchise_owner_bank_accounts')


# MÓDULO DE DADOS PREMIUM - VISTAS
# ============================================================================

from .decorators import dice_module_required, super_admin_required
from .utils.dice_module import is_dice_module_enabled, can_user_access_dice_module
from datetime import timedelta


@login_required
@dice_module_required
def dice_lobby(request):
    """
    Lobby principal del módulo de dados.
    Muestra partidas disponibles y permite crear/unirse a partidas.
    """
    settings = DiceModuleSettings.get_settings()
    
    # Verificar si el usuario tiene una partida activa/en curso PRIMERO
    active_game = DiceGame.objects.filter(
        dice_players__user=request.user,
        status__in=['WAITING', 'SPINNING', 'PLAYING']
    ).order_by('-created_at').first()
    
    # Si tiene una partida activa, limpiar cualquier entrada en cola y redirigir
    if active_game:
        # Limpiar entradas en cola del usuario
        DiceMatchmakingQueue.objects.filter(
            user=request.user,
            status__in=['WAITING', 'MATCHED']
        ).update(status='TIMEOUT')
        
        messages.info(request, f'Volviendo a tu partida activa: {active_game.room_code}')
        return redirect('dice_game_room', room_code=active_game.room_code)
    
    # Limpiar entradas antiguas en cola (más de 10 minutos)
    from django.utils import timezone
    from datetime import timedelta
    DiceMatchmakingQueue.objects.filter(
        user=request.user,
        status='WAITING',
        joined_at__lt=timezone.now() - timedelta(minutes=10)
    ).update(status='TIMEOUT')
    
    # Partidas esperando jugadores
    waiting_games = DiceGame.objects.filter(
        status='WAITING'
    ).annotate(
        player_count=Count('dice_players')
    ).filter(
        player_count__lt=3
    ).order_by('-created_at')[:10]
    
    # Verificar si el usuario está en cola (solo entradas recientes)
    user_queue_entry = DiceMatchmakingQueue.objects.filter(
        user=request.user,
        status='WAITING',
        joined_at__gte=timezone.now() - timedelta(minutes=10)
    ).first()
    
    context = {
        'settings': settings,
        'waiting_games': waiting_games,
        'entry_price': settings.base_entry_price,
        'min_price': Decimal('0.10'),
        'max_price': settings.max_entry_price,
        'user_in_queue': user_queue_entry is not None,
        'active_game': None,  # Ya verificamos arriba
    }
    
    return render(request, 'bingo_app/dice_lobby.html', context)


@login_required
@dice_module_required
@require_POST
def join_dice_queue(request):
    """
    Agrega al usuario a la cola de matchmaking.
    """
    try:
        entry_price = Decimal(request.POST.get('entry_price', '0.10'))
        
        # Validar precio mínimo
        if entry_price < Decimal('0.10'):
            return JsonResponse({
                'success': False,
                'error': 'El precio mínimo es $0.10 (10 centavos)'
            }, status=400)
        
        # Validar saldo
        if request.user.credit_balance < entry_price:
            return JsonResponse({
                'success': False,
                'error': 'Saldo insuficiente'
            }, status=400)
        
        # Verificar si el usuario tiene una partida activa (usar DicePlayer directamente)
        from .models import DicePlayer
        active_player = DicePlayer.objects.filter(
            user=request.user,
            game__status__in=['WAITING', 'SPINNING', 'PLAYING']
        ).select_related('game').first()
        
        if active_player:
            return JsonResponse({
                'success': False,
                'error': 'Ya tienes una partida activa',
                'status': 'matched',
                'room_code': active_player.game.room_code
            }, status=400)
        
        # Limpiar entradas antiguas en cola del usuario
        from django.utils import timezone
        from datetime import timedelta
        DiceMatchmakingQueue.objects.filter(
            user=request.user,
            status='WAITING',
            joined_at__lt=timezone.now() - timedelta(minutes=10)
        ).update(status='TIMEOUT')
        
        # Verificar si ya está en cola (cualquier entrada WAITING, sin importar el tiempo)
        existing_queue = DiceMatchmakingQueue.objects.filter(
            user=request.user,
            status='WAITING'
        ).first()
        
        if existing_queue:
            print(f"ℹ️ [JOIN_QUEUE] Usuario {request.user.username} ya está en cola (ID: {existing_queue.id}), continuando búsqueda...")
            # En lugar de devolver error, devolver éxito para que el frontend continúe verificando
            return JsonResponse({
                'success': True,
                'status': 'waiting',
                'message': 'Ya estás en la cola, buscando oponentes...'
            })
        
        # Crear entrada en cola
        queue_entry = DiceMatchmakingQueue.objects.create(
            user=request.user,
            entry_price=entry_price,
            status='WAITING'
        )
        
        # Procesar matchmaking (intentar encontrar partida)
        from .tasks import process_matchmaking_queue
        result = process_matchmaking_queue()
        
        if result:
            # Partida encontrada - verificar que el usuario esté en la partida usando DicePlayer
            from .models import DicePlayer
            result.refresh_from_db()  # Asegurar que la partida esté actualizada
            
            player = DicePlayer.objects.filter(
                user=request.user,
                game=result
            ).first()
            
            if player:
                print(f"✅ [JOIN_QUEUE] Usuario {request.user.username} está en partida {result.room_code}")
                return JsonResponse({
                    'success': True,
                    'status': 'matched',
                    'room_code': result.room_code,
                    'message': '¡Partida encontrada!'
                })
            else:
                # El usuario no está en la partida (puede ser un problema de timing)
                print(f"⚠️ [JOIN_QUEUE] Usuario {request.user.username} NO está en partida {result.room_code}")
                print(f"   Jugadores en partida: {[p.user.username for p in result.dice_players.all()]}")
                
                # Esperar un momento y verificar de nuevo
                import time
                time.sleep(0.5)
                player = DicePlayer.objects.filter(
                    user=request.user,
                    game=result
                ).first()
                
                if player:
                    print(f"✅ [JOIN_QUEUE] Usuario encontrado después de esperar")
                    return JsonResponse({
                        'success': True,
                        'status': 'matched',
                        'room_code': result.room_code,
                        'message': '¡Partida encontrada!'
                    })
                else:
                    print(f"❌ [JOIN_QUEUE] Usuario aún no está en partida después de esperar")
        
        # Esperando más jugadores
        return JsonResponse({
            'success': True,
            'status': 'waiting',
            'message': 'Buscando oponentes...'
        })
            
    except Exception as e:
        import traceback
        print(f"Error en join_dice_queue: {e}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'status': 'error',
            'error': str(e)
        }, status=400)


@login_required
@dice_module_required
@require_POST
def leave_dice_queue(request):
    """
    Remueve al usuario de la cola de matchmaking.
    """
    try:
        queue_entry = DiceMatchmakingQueue.objects.filter(
            user=request.user,
            status='WAITING'
        ).first()
        
        if queue_entry:
            queue_entry.status = 'TIMEOUT'
            queue_entry.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Has salido de la cola'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@dice_module_required
def dice_queue_status(request):
    """
    Verifica el estado de la cola del usuario y partidas activas.
    También ejecuta el proceso de matchmaking para encontrar partidas.
    """
    try:
        # PRIMERO: Verificar si el usuario tiene una partida activa/en curso
        # Usar DicePlayer directamente es más confiable
        from .models import DicePlayer
        active_player = DicePlayer.objects.filter(
            user=request.user,
            game__status__in=['SPINNING', 'PLAYING', 'WAITING']
        ).select_related('game').order_by('-game__created_at').first()
        
        if active_player:
            print(f"✅ [QUEUE_STATUS] Usuario {request.user.username} tiene partida activa: {active_player.game.room_code}")
            return JsonResponse({
                'status': 'matched',
                'room_code': active_player.game.room_code,
                'message': 'Tienes una partida activa'
            })
        
        # SEGUNDO: Verificar si está en cola (necesario antes de ejecutar matchmaking)
        queue_entry = DiceMatchmakingQueue.objects.filter(
            user=request.user,
            status='WAITING'
        ).first()
        
        # TERCERO: Ejecutar proceso de matchmaking para intentar encontrar partida
        # Esto es importante porque puede haber 3 usuarios esperando
        from .tasks import process_matchmaking_queue
        
        # Verificar cuántos jugadores hay esperando antes de ejecutar matchmaking
        # IMPORTANTE: Usar la misma lógica de exclusión que el matchmaking
        from django.db.models import Exists, OuterRef
        active_games_pre = DiceGame.objects.filter(
            dice_players__user=OuterRef('user'),
            status__in=['WAITING', 'SPINNING', 'PLAYING']
        ).exclude(status='FINISHED')
        
        waiting_count = DiceMatchmakingQueue.objects.filter(status='WAITING').exclude(
            Exists(active_games_pre)
        ).count()
        
        same_price_count_pre = 0
        if queue_entry:
            same_price_count_pre = DiceMatchmakingQueue.objects.filter(
                status='WAITING',
                entry_price=queue_entry.entry_price
            ).exclude(
                Exists(active_games_pre)
            ).count()
        
        print(f"🔄 [QUEUE_STATUS] Ejecutando matchmaking... Total válidos en cola: {waiting_count}, Mismo precio válidos: {same_price_count_pre}")
        
        try:
            matchmaking_result = process_matchmaking_queue()
        except Exception as e:
            print(f"❌ [QUEUE_STATUS] Error ejecutando matchmaking: {e}")
            import traceback
            traceback.print_exc()
            matchmaking_result = None
        
        # Si se creó una partida, verificar si el usuario está en ella
        if matchmaking_result:
            print(f"✅ [QUEUE_STATUS] Matchmaking creó partida: {matchmaking_result.room_code}")
            
            # Refrescar desde la base de datos para asegurar que los jugadores estén guardados
            matchmaking_result.refresh_from_db()
            
            # Verificar directamente con DicePlayer
            player = DicePlayer.objects.filter(
                user=request.user,
                game=matchmaking_result
            ).first()
            
            if player:
                print(f"✅ [QUEUE_STATUS] Usuario {request.user.username} está en partida {matchmaking_result.room_code}")
                return JsonResponse({
                    'status': 'matched',
                    'room_code': matchmaking_result.room_code,
                    'message': '¡Partida encontrada!'
                })
            else:
                print(f"⚠️ [QUEUE_STATUS] Usuario {request.user.username} NO está en partida {matchmaking_result.room_code}")
                print(f"   Jugadores en partida: {[p.user.username for p in matchmaking_result.dice_players.all()]}")
                
                # Esperar un momento y verificar de nuevo (problema de timing)
                import time
                time.sleep(0.5)
                player = DicePlayer.objects.filter(
                    user=request.user,
                    game=matchmaking_result
                ).first()
                
                if player:
                    print(f"✅ [QUEUE_STATUS] Usuario encontrado después de esperar")
                    return JsonResponse({
                        'status': 'matched',
                        'room_code': matchmaking_result.room_code,
                        'message': '¡Partida encontrada!'
                    })
        else:
            print(f"⏳ [QUEUE_STATUS] Matchmaking no creó partida (puede que no haya suficientes jugadores válidos)")
        
        # CUARTO: Verificar si está en cola (ya se verificó arriba, pero verificar de nuevo por si cambió)
        if not queue_entry:
            queue_entry = DiceMatchmakingQueue.objects.filter(
                user=request.user,
                status='WAITING'
            ).first()
        
        if not queue_entry:
            # Verificar si tiene una entrada MATCHED (partida recién creada)
            matched_entry = DiceMatchmakingQueue.objects.filter(
                user=request.user,
                status='MATCHED'
            ).order_by('-matched_at').first()
            
            if matched_entry:
                # Buscar la partida más reciente
                dice_game = DiceGame.objects.filter(
                    dice_players__user=request.user,
                    status__in=['SPINNING', 'PLAYING', 'WAITING']
                ).order_by('-created_at').first()
                
                if dice_game:
                    print(f"✅ [QUEUE_STATUS] Usuario {request.user.username} tiene entrada MATCHED, partida: {dice_game.room_code}")
                    return JsonResponse({
                        'status': 'matched',
                        'room_code': dice_game.room_code
                    })
            
            print(f"ℹ️ [QUEUE_STATUS] Usuario {request.user.username} no está en cola")
            return JsonResponse({
                'status': 'not_in_queue'
            })
        
        print(f"⏳ [QUEUE_STATUS] Usuario {request.user.username} en cola, estado: WAITING")
        
        # IMPORTANTE: Usar la MISMA consulta que process_matchmaking_queue para contar
        # Esto asegura que el conteo sea consistente con lo que el matchmaking puede usar
        from django.db.models import Exists, OuterRef
        
        # Usar exactamente la misma lógica que process_matchmaking_queue
        active_games = DiceGame.objects.filter(
            dice_players__user=OuterRef('user'),
            status__in=['WAITING', 'SPINNING', 'PLAYING']
        ).exclude(status='FINISHED')
        
        # Contar usando la misma consulta que el matchmaking
        valid_waiting_query = DiceMatchmakingQueue.objects.filter(
            status='WAITING',
            entry_price=queue_entry.entry_price
        ).exclude(
            Exists(active_games)
        )
        
        same_price_count = valid_waiting_query.count()
        
        # Logging detallado para debugging
        all_waiting_same_price = DiceMatchmakingQueue.objects.filter(
            status='WAITING',
            entry_price=queue_entry.entry_price
        )
        all_count = all_waiting_same_price.count()
        excluded_count = all_count - same_price_count
        
        print(f"📊 [QUEUE_STATUS] Precio ${queue_entry.entry_price}:")
        print(f"   - Total en WAITING: {all_count}")
        print(f"   - Con partida activa (excluidos): {excluded_count}")
        print(f"   - Válidos para matchmaking: {same_price_count}")
        
        # Mostrar detalles de los jugadores válidos
        valid_list = list(valid_waiting_query[:5])
        for entry in valid_list:
            print(f"   ✓ {entry.user.username} (ID: {entry.id})")
        
        # Mostrar detalles de los jugadores excluidos
        if excluded_count > 0:
            excluded_entries = all_waiting_same_price.filter(Exists(active_games))
            for entry in excluded_entries[:5]:
                active_game = DiceGame.objects.filter(
                    dice_players__user=entry.user,
                    status__in=['WAITING', 'SPINNING', 'PLAYING']
                ).exclude(status='FINISHED').first()
                if active_game:
                    print(f"   ⚠️ {entry.user.username} excluido - tiene partida activa: {active_game.room_code} (estado: {active_game.status})")
        
        return JsonResponse({
            'status': 'waiting',
            'entry_price': float(queue_entry.entry_price),
            'players_waiting': same_price_count,
            'message': f'Buscando oponentes... ({same_price_count}/3 jugadores con precio ${queue_entry.entry_price})'
        })
    except Exception as e:
        import traceback
        print(f"❌ [QUEUE_STATUS] Error en dice_queue_status: {e}")
        print(traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)  # Cambiar a 500 para errores del servidor, no 400


@login_required
@dice_module_required
def dice_game_room(request, room_code):
    """
    Sala de juego de dados.
    """
    try:
        dice_game = DiceGame.objects.get(room_code=room_code)
        
        # Verificar que el usuario es parte de la partida
        player = DicePlayer.objects.filter(
            game=dice_game,
            user=request.user
        ).first()
        
        if not player:
            messages.error(request, 'No eres parte de esta partida')
            return redirect('dice_lobby')
        
        # LIMPIAR cualquier entrada en cola del usuario (por si hay entradas antiguas)
        DiceMatchmakingQueue.objects.filter(
            user=request.user,
            status__in=['WAITING', 'MATCHED']
        ).update(status='TIMEOUT')
        
        # Obtener todos los jugadores
        players = dice_game.dice_players.all()
        
        context = {
            'dice_game': dice_game,
            'player': player,
            'players': players,
            'room_code': room_code,
        }
        
        return render(request, 'bingo_app/dice_game_room.html', context)
        
    except DiceGame.DoesNotExist:
        messages.error(request, 'Partida no encontrada')
        return redirect('dice_lobby')


@login_required
@super_admin_required
def admin_dice_module_settings(request):
    """
    Panel de administración del módulo de dados.
    Solo accesible por super administradores.
    """
    settings = DiceModuleSettings.get_settings()
    
    if request.method == 'POST':
        settings.is_module_enabled = request.POST.get('is_module_enabled') == 'on'
        settings.base_entry_price = Decimal(request.POST.get('base_entry_price', '0.10'))
        settings.platform_commission_percentage = Decimal(request.POST.get('platform_commission_percentage', '5.00'))
        settings.show_in_lobby = request.POST.get('show_in_lobby') == 'on'
        settings.power_ups_enabled = request.POST.get('power_ups_enabled') == 'on'
        settings.allow_custom_entry_price = request.POST.get('allow_custom_entry_price') == 'on'
        
        max_price = request.POST.get('max_entry_price', '').strip()
        if max_price:
            settings.max_entry_price = Decimal(max_price)
        else:
            settings.max_entry_price = None
        
        settings.updated_by = request.user
        settings.save()
        
        messages.success(request, "Configuración del módulo de dados actualizada")
        return redirect('admin_dice_module_settings')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'bingo_app/admin_dice_module_settings.html', context)