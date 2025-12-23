from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import transaction
from django.contrib import messages
from django.utils import timezone

from .models import (
    User, Game, Player, ChatMessage, PercentageSettings, Raffle,
    FlashMessage, Message, CreditRequest, WithdrawalRequest, Transaction,
    BankAccount, PrintableCard, Announcement, BingoTicket, DailyBingoSchedule, BingoTicketSettings,
    AccountsReceivable, AccountsReceivablePayment, PackageTemplate, Franchise, FranchiseManual,
    DiceModuleSettings, DiceGame, DicePlayer, DiceRound, DiceMatchmakingQueue
)

# --- Admin para el Modelo de Usuario ---
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'credit_balance', 'reputation_level', 'manual_reputation', 'is_organizer', 'is_staff', 'is_blocked')
    list_filter = ('is_staff', 'is_organizer', 'is_blocked', 'manual_reputation')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Económica', {'fields': ('credit_balance',)}),
        ('Roles y Estado', {'fields': ('is_organizer', 'manual_reputation', 'is_blocked', 'block_reason', 'blocked_until')}),
    )
    readonly_fields = ('blocked_at', 'blocked_by')

# --- Admin para Solicitudes de Crédito ---
@admin.register(CreditRequest)
class CreditRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'processed_at')
    actions = ['approve_requests']

    @admin.action(description='Aprobar solicitudes seleccionadas')
    def approve_requests(self, request, queryset):
        for credit_request in queryset.filter(status='pending'):
            try:
                with transaction.atomic():
                    user = credit_request.user
                    user.credit_balance += credit_request.amount
                    user.save()

                    Transaction.objects.create(
                        user=user,
                        amount=credit_request.amount,
                        transaction_type='ADMIN_ADD',
                        description=f"Recarga aprobada por admin: {request.user.username}"
                    )

                    credit_request.status = 'approved'
                    credit_request.processed_at = timezone.now()
                    credit_request.admin_notes = f"Aprobado por {request.user.username}"
                    credit_request.save()
                
                self.message_user(request, f"Solicitud de {user.username} por ${credit_request.amount} aprobada.", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"Error al procesar la solicitud de {credit_request.user.username}: {e}", messages.ERROR)

# --- Admin para Solicitudes de Retiro ---
@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at', 'processed_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'account_holder_name')
    readonly_fields = ('created_at', 'processed_at')
    actions = ['approve_and_process_withdrawals', 'reject_withdrawals']

    @admin.action(description='Aprobar y procesar retiros seleccionados')
    def approve_and_process_withdrawals(self, request, queryset):
        for withdrawal in queryset.filter(status='PENDING'):
            if withdrawal.user.credit_balance >= withdrawal.amount:
                try:
                    with transaction.atomic():
                        withdrawal.user.credit_balance -= withdrawal.amount
                        withdrawal.user.save()

                        Transaction.objects.create(
                            user=withdrawal.user,
                            amount=-withdrawal.amount,
                            transaction_type='WITHDRAWAL',
                            description=f"Retiro aprobado por admin: {request.user.username}"
                        )
                        
                        withdrawal.status = 'COMPLETED'
                        withdrawal.processed_at = timezone.now()
                        withdrawal.admin_notes = f"Procesado por {request.user.username}"
                        withdrawal.save()

                    self.message_user(request, f"Retiro de {withdrawal.user.username} por ${withdrawal.amount} procesado.", messages.SUCCESS)
                except Exception as e:
                    self.message_user(request, f"Error al procesar el retiro de {withdrawal.user.username}: {e}", messages.ERROR)
            else:
                self.message_user(request, f"El retiro de {withdrawal.user.username} no puede ser procesado: Saldo insuficiente.", messages.WARNING)

    @admin.action(description='Rechazar retiros seleccionados')
    def reject_withdrawals(self, request, queryset):
        queryset.update(status='REJECTED', processed_at=timezone.now(), admin_notes=f"Rechazado por {request.user.username}")
        self.message_user(request, "Retiros seleccionados han sido rechazados.", messages.INFO)

# --- Otros Admins ---
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'created_at', 'related_game')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizer', 'is_started', 'is_finished', 'card_price', 'prize')
    list_filter = ('is_started', 'is_finished', 'organizer')
    search_fields = ('name',)

# --- Registro de Modelos ---
# (User, CreditRequest, y WithdrawalRequest ya están registrados con sus clases personalizadas)
admin.site.register(Player)
admin.site.register(ChatMessage)
@admin.register(PercentageSettings)
class PercentageSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'platform_commission', 
        'game_creation_fee_enabled', 
        'platform_commission_enabled',
        'referral_system_enabled',
        'promotions_enabled',
        'credits_purchase_enabled',
        'credits_withdrawal_enabled',
        'last_updated'
    )
    
    fieldsets = (
        ('💰 Comisiones y Tarifas', {
            'fields': (
                'platform_commission',
                'platform_commission_enabled',
                'game_creation_fee',
                'game_creation_fee_enabled',
            ),
            'description': '⚙️ Configuración de tarifas y comisiones del sistema.'
        }),
        ('📣 Precios de Promoción', {
            'fields': (
                'image_promotion_price',
                'video_promotion_price',
            ),
            'description': '💵 Costos para promocionar eventos con multimedia.'
        }),
        ('🎮 CONTROL DE FUNCIONALIDADES DEL USUARIO ⭐', {
            'fields': (
                'credits_purchase_enabled',
                'credits_withdrawal_enabled',
                'referral_system_enabled',
                'promotions_enabled',
            ),
            'description': '🔧 ⚠️ IMPORTANTE: Activa o desactiva funcionalidades visibles para los usuarios en el lobby. '
                          'Si desactivas un sistema, el enlace DESAPARECERÁ del menú de navegación.'
        }),
        ('ℹ️ Información', {
            'fields': ('last_updated', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('last_updated', 'updated_by')

    def has_add_permission(self, request):
        # Allow only one instance of PercentageSettings
        return not PercentageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False

admin.site.register(Raffle)
admin.site.register(FlashMessage)
admin.site.register(Message)
admin.site.register(BankAccount)
admin.site.register(PrintableCard)
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('message', 'announcement_type', 'is_active', 'order', 'created_at', 'expires_at')
    list_filter = ('announcement_type', 'is_active')
    search_fields = ('message', 'external_link')
    fieldsets = (
        (None, {'fields': ('announcement_type', 'message', 'is_active', 'order')}),
        ('Contenido Multimedia', {'fields': ('image', 'video_url')}),
        ('Enlaces y Relaciones', {'fields': ('external_link', 'related_game', 'related_raffle')}),
        ('Promoción', {'fields': ('promoted_by', 'expires_at')}),
    )
    raw_id_fields = ('related_game', 'related_raffle', 'promoted_by') # For large number of games/raffles/users


# --- Admin para Sistema de Tickets de Bingo ---
@admin.register(BingoTicket)
class BingoTicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticket_type', 'is_used', 'created_at', 'expires_at', 'used_at')
    list_filter = ('ticket_type', 'is_used', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'used_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {'fields': ('user', 'ticket_type', 'is_used')}),
        ('Fechas', {'fields': ('created_at', 'expires_at', 'used_at')}),
        ('Uso', {'fields': ('used_in_game',)}),
    )


@admin.register(DailyBingoSchedule)
class DailyBingoScheduleAdmin(admin.ModelAdmin):
    list_display = ('time_slot', 'is_active', 'max_players', 'prize_amount', 'created_at')
    list_filter = ('is_active', 'time_slot')
    search_fields = ('description',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('time_slot', 'is_active', 'description')}),
        ('Configuración', {'fields': ('max_players', 'prize_amount')}),
        ('Fechas', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(BingoTicketSettings)
class BingoTicketSettingsAdmin(admin.ModelAdmin):
    list_display = ('is_system_active', 'referral_ticket_bonus', 'referred_ticket_bonus', 'ticket_expiration_days', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Configuración General', {'fields': ('is_system_active',)}),
        ('Bonificaciones por Referido', {'fields': ('referral_ticket_bonus', 'referred_ticket_bonus')}),
        ('Configuración de Tickets', {'fields': ('ticket_expiration_days',)}),
        ('Fechas', {'fields': ('created_at', 'updated_at')}),
    )
    
    def has_add_permission(self, request):
        # Solo permitir una instancia de configuración
        return not BingoTicketSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar la configuración
        return False

# --- Admin para Cuentas por Cobrar ---
@admin.register(AccountsReceivable)
class AccountsReceivableAdmin(admin.ModelAdmin):
    list_display = ('id', 'debtor', 'organizer', 'amount', 'total_paid_display', 'remaining_balance_display', 'is_paid_display', 'created_at')
    list_filter = ('created_at', 'organizer')
    search_fields = ('debtor__username', 'debtor__email', 'organizer__username', 'concept')
    readonly_fields = ('created_at', 'updated_at', 'total_paid_display', 'remaining_balance_display', 'is_paid_display')
    fieldsets = (
        ('Información Principal', {'fields': ('debtor', 'organizer', 'amount', 'concept')}),
        ('Resumen', {'fields': ('total_paid_display', 'remaining_balance_display', 'is_paid_display')}),
        ('Fechas', {'fields': ('created_at', 'updated_at')}),
    )
    
    def total_paid_display(self, obj):
        return f"${obj.total_paid:.2f}"
    total_paid_display.short_description = 'Total Abonado'
    
    def remaining_balance_display(self, obj):
        return f"${obj.remaining_balance:.2f}"
    remaining_balance_display.short_description = 'Saldo Pendiente'
    
    def is_paid_display(self, obj):
        return "Sí" if obj.is_paid else "No"
    is_paid_display.short_description = 'Pagado'

@admin.register(AccountsReceivablePayment)
class AccountsReceivablePaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_receivable', 'amount', 'payment_method', 'created_at')
    list_filter = ('created_at', 'payment_method')
    search_fields = ('account_receivable__debtor__username', 'account_receivable__organizer__username', 'notes')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Información del Pago', {'fields': ('account_receivable', 'amount', 'payment_method', 'proof', 'notes')}),
        ('Fecha', {'fields': ('created_at',)}),
    )

# --- Admin para Sistema de Franquicias ---
@admin.register(PackageTemplate)
class PackageTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'package_type', 'current_monthly_price', 'current_commission_rate', 'is_active', 'created_at')
    list_filter = ('package_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información Básica', {'fields': ('package_type', 'name', 'description', 'is_active')}),
        ('Precios', {
            'fields': (
                'default_monthly_price', 'current_monthly_price',
                'default_commission_rate', 'current_commission_rate'
            ),
            'description': 'Los precios actuales son los que se usan para nuevas franquicias. Puedes editarlos desde el panel de administración.'
        }),
        ('Funcionalidades', {
            'fields': (
                'bingos_enabled', 'raffles_enabled', 'accounts_receivable_enabled',
                'video_calls_bingos_enabled', 'video_calls_raffles_enabled',
                'custom_manual_enabled', 'notifications_push_enabled',
                'advanced_reports_enabled', 'advanced_promotions_enabled', 'banners_enabled'
            ),
            'description': 'Estas funcionalidades están preconfiguradas y no se pueden editar desde aquí.'
        }),
        ('Fechas', {'fields': ('created_at', 'updated_at')}),
    )
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar plantillas preconfiguradas
        return False

@admin.register(Franchise)
class FranchiseAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'custom_domain', 'package_template', 'monthly_price', 'commission_rate', 'is_active', 'has_active_subscription', 'created_at')
    list_filter = ('is_active', 'package_template', 'created_at')
    search_fields = ('name', 'slug', 'custom_domain', 'owner__username', 'owner__email')
    readonly_fields = ('created_at', 'updated_at', 'subscription_start_date')
    fieldsets = (
        ('Información Básica', {'fields': ('name', 'slug', 'logo', 'image', 'owner', 'is_active')}),
        ('🌐 Dominio Personalizado', {
            'fields': ('custom_domain',),
            'description': '⚠️ IMPORTANTE: Configura el dominio personalizado (ej: mi-franquicia.com). '
                          'El dominio debe estar configurado en el DNS apuntando a este servidor. '
                          'Una vez configurado, los usuarios podrán acceder a la franquicia usando este dominio. '
                          'Asegúrate de agregar el dominio a ALLOWED_HOSTS en Railway.'
        }),
        ('Contacto', {'fields': ('whatsapp_number',)}),
        ('Paquete y Precios', {'fields': ('package_template', 'monthly_price', 'commission_rate')}),
        ('Suscripción', {'fields': ('subscription_start_date', 'subscription_end_date')}),
        ('Metadata', {'fields': ('created_by', 'created_at', 'updated_at')}),
    )
    raw_id_fields = ('owner', 'created_by', 'package_template')
    
    def save_model(self, request, obj, form, change):
        """Validar y limpiar el dominio antes de guardar"""
        if obj.custom_domain:
            # Limpiar el dominio
            domain = obj.custom_domain.strip().lower()
            if domain.startswith('http://'):
                domain = domain[7:]
            if domain.startswith('https://'):
                domain = domain[8:]
            if domain.startswith('www.'):
                domain = domain[4:]
            domain = domain.rstrip('/')
            obj.custom_domain = domain
            
            # Verificar que no esté duplicado (excepto si es el mismo objeto)
            existing = Franchise.objects.filter(custom_domain=domain).exclude(pk=obj.pk).first()
            if existing:
                from django.contrib import messages
                messages.warning(request, f'⚠️ El dominio "{domain}" ya está asignado a la franquicia "{existing.name}".')
        
        super().save_model(request, obj, form, change)

@admin.register(FranchiseManual)
class FranchiseManualAdmin(admin.ModelAdmin):
    list_display = ('franchise', 'updated_at', 'updated_by')
    list_filter = ('updated_at',)
    search_fields = ('franchise__name', 'content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información', {'fields': ('franchise',)}),
        ('Contenido', {'fields': ('content',)}),
        ('Metadata', {'fields': ('updated_by', 'created_at', 'updated_at')}),
    )
    raw_id_fields = ('franchise', 'updated_by')


@admin.register(DiceModuleSettings)
class DiceModuleSettingsAdmin(admin.ModelAdmin):
    list_display = ('is_module_enabled', 'base_entry_price', 'platform_commission_percentage', 'show_in_lobby', 'last_updated')
    readonly_fields = ('last_updated', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        # Solo permitir un objeto de configuración
        return not DiceModuleSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False  # No permitir eliminar la configuración


@admin.register(DiceGame)
class DiceGameAdmin(admin.ModelAdmin):
    list_display = ('room_code', 'status', 'entry_price', 'multiplier', 'final_prize', 'winner', 'created_at')
    list_filter = ('status', 'multiplier', 'created_at')
    search_fields = ('room_code', 'winner__username')
    readonly_fields = ('room_code', 'created_at', 'started_at', 'finished_at')


@admin.register(DicePlayer)
class DicePlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'lives', 'total_score', 'is_eliminated', 'joined_at')
    list_filter = ('is_eliminated', 'game__status')
    search_fields = ('user__username', 'game__room_code')


@admin.register(DiceRound)
class DiceRoundAdmin(admin.ModelAdmin):
    list_display = ('game', 'round_number', 'eliminated_player', 'created_at')
    list_filter = ('round_number', 'created_at')
    search_fields = ('game__room_code', 'eliminated_player__username')


@admin.register(DiceMatchmakingQueue)
class DiceMatchmakingQueueAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry_price', 'status', 'joined_at', 'matched_at')
    list_filter = ('status', 'entry_price', 'joined_at')
    search_fields = ('user__username',)
    readonly_fields = ('joined_at', 'matched_at')
