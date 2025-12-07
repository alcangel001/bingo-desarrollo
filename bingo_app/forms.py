from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator, validate_email
from django.core.exceptions import ValidationError
import json
from .models import BankAccount, User, Game, CreditRequest, Raffle, PercentageSettings, WithdrawalRequest, Announcement, AccountsReceivable, AccountsReceivablePayment

class RegistrationForm(UserCreationForm):
    is_organizer = forms.BooleanField(
        required=False,
        label='¿Eres un organizador? (Puedes crear juegos)'
    )
    franchise_code = forms.CharField(
        required=False,
        max_length=100,
        label='Código de Franquicia (Opcional)',
        help_text='Si tienes un código de franquicia, ingrésalo aquí'
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError('Por favor ingresa un correo electrónico válido.')
            # Verificar si el correo ya existe (case-insensitive)
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError('Este correo electrónico ya está registrado. Por favor utiliza otro.')
        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar validación de email como campo requerido
        self.fields['email'] = forms.EmailField(
            required=True,
            label='Correo electrónico',
            widget=forms.EmailInput(attrs={'autocomplete': 'email'})
        )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_organizer')
    
    # El campo franchise_code no se guarda en el modelo, solo se usa para asignar la franquicia

class GameForm(forms.ModelForm):
    auto_call_interval = forms.IntegerField(
        initial=5,
        min_value=1,
        max_value=60,
        help_text="Segundos entre llamadas automáticas"
    )
    
    # Campos para sala de video
    create_video_room = forms.BooleanField(
        required=False,
        initial=True,
        label="Crear sala de videollamada",
        help_text="Crea automáticamente una sala de video para este juego"
    )
    
    video_room_type = forms.ChoiceField(
        required=False,
        choices=[('public', 'Pública - Todos pueden unirse'), ('private', 'Privada - Solo invitados')],
        initial='public',
        label="Tipo de sala de video",
        help_text="Las salas públicas son ideales para jugar con toda la comunidad. Usa salas privadas para videollamadas con amigos y familia."
    )
    
    video_room_password = forms.CharField(
        required=False,
        max_length=50,
        label="Contraseña de sala de video (opcional)",
        help_text="Solo para salas privadas. Deja en blanco para acceso sin contraseña.",
        widget=forms.PasswordInput(attrs={'placeholder': 'Opcional para salas privadas'})
    )
    
    class Meta:
        model = Game
        fields = ['name', 'password', 'card_price', 
                 'max_cards_per_player', 'winning_pattern',
                'base_prize', 'auto_call_interval', 'progressive_prizes','custom_pattern', 'allows_printable_cards', 'entry_price']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['progressive_prizes'].required = False
        self.fields['progressive_prizes'].widget = forms.HiddenInput()  # Ocultar campo raw

        self.fields['custom_pattern'].required = False

        # Configurar validaciones y apariencia del precio por cartón
        card_price_field = self.fields.get('card_price')
        if card_price_field:
            card_price_field.widget = forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.10',
                'step': '0.01',
                'placeholder': 'Ej: 0.10'
            })
            if not card_price_field.initial:
                card_price_field.initial = '0.10'
        
        # Añadir campo para subir un archivo JSON con el patrón
        self.fields['pattern_file'] = forms.FileField(
            required=False,
            help_text="Sube un archivo JSON con el patrón personalizado"
        )
        
        # Campo para la interfaz de usuario (si usas JavaScript para manejar los premios)
        self.fields['progressive_prizes_json'] = forms.CharField(
            required=False,
            widget=forms.HiddenInput()
        )
    
    def clean(self):
        cleaned_data = super().clean()
        winning_pattern = cleaned_data.get('winning_pattern')
        custom_pattern = cleaned_data.get('custom_pattern')
        pattern_file = cleaned_data.get('pattern_file')

        if winning_pattern == 'CUSTOM':
            if not custom_pattern and not pattern_file:
                raise forms.ValidationError("Debes proporcionar un patrón personalizado o subir un archivo")
            
            if pattern_file:
                try:
                    pattern_data = json.load(pattern_file)
                    cleaned_data['custom_pattern'] = pattern_data
                except json.JSONDecodeError:
                    raise forms.ValidationError("El archivo debe ser un JSON válido")
        
        # Procesar premios progresivos
        progressive_prizes_json = self.data.get('progressive_prizes_json')
        if progressive_prizes_json:
            try:
                prizes = json.loads(progressive_prizes_json)
                # Validar estructura
                for prize in prizes:
                    if not all(key in prize for key in ['target', 'prize']):
                        raise forms.ValidationError("Formato de premios progresivos inválido")
                cleaned_data['progressive_prizes'] = prizes
            except (json.JSONDecodeError, TypeError):
                raise forms.ValidationError("Formato de premios progresivos inválido")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Establecer valores por defecto
        if not instance.prize:
            instance.prize = instance.base_prize
        
        if commit:
            instance.save()
            self.save_m2m()  # Importante para relaciones ManyToMany si las hay
        
        return instance
        
class GameEditForm(forms.ModelForm):
    """
    Formulario para editar juegos NO iniciados.
    Permite editar solo ciertos campos que no afectan al premio base ya bloqueado.
    """
    new_base_prize = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        label="Nuevo Premio Base (créditos)",
        help_text="Ajustar el premio base del juego. Se bloquearán/desbloquearán créditos automáticamente.",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '1',
            'min': '0'
        })
    )
    
    class Meta:
        model = Game
        fields = ['progressive_prizes', 'name', 'password', 'auto_call_interval', 'allows_printable_cards']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['progressive_prizes'].required = False
        self.fields['progressive_prizes'].widget = forms.HiddenInput()
        
        # Campo para la interfaz de usuario (JavaScript maneja los premios)
        self.fields['progressive_prizes_json'] = forms.CharField(
            required=False,
            widget=forms.HiddenInput()
        )
        
        # Hacer campos opcionales
        self.fields['password'].required = False
        self.fields['auto_call_interval'].help_text = "Segundos entre llamadas automáticas"
        
        # Pre-llenar valores actuales si existen
        if self.instance and self.instance.progressive_prizes:
            initial_json = json.dumps(self.instance.progressive_prizes)
            self.fields['progressive_prizes_json'].initial = initial_json
        
        # Pre-llenar el premio base actual
        if self.instance:
            self.fields['new_base_prize'].initial = self.instance.base_prize
    
    def clean_new_base_prize(self):
        new_prize = self.cleaned_data.get('new_base_prize')
        if new_prize is not None and self.instance:
            current_prize = self.instance.base_prize
            diferencia = new_prize - current_prize
            
            # Validar que tenga suficiente saldo si aumenta
            if diferencia > 0:
                organizer = self.instance.organizer
                if organizer.credit_balance < diferencia:
                    raise forms.ValidationError(
                        f"No tienes suficiente saldo. Necesitas {diferencia} créditos adicionales. "
                        f"Tu saldo disponible es {organizer.credit_balance} créditos."
                    )
            
            # Validar que haya suficientes créditos bloqueados si reduce
            elif diferencia < 0:
                organizer = self.instance.organizer
                diferencia_abs = abs(diferencia)
                if organizer.blocked_credits < diferencia_abs:
                    raise forms.ValidationError(
                        f"No hay suficientes créditos bloqueados. Tienes {organizer.blocked_credits} bloqueados, "
                        f"pero necesitas {diferencia_abs} para reducir el premio."
                    )
        
        return new_prize
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Procesar premios progresivos
        progressive_prizes_json = self.data.get('progressive_prizes_json')
        if progressive_prizes_json:
            try:
                prizes = json.loads(progressive_prizes_json)
                # Validar estructura
                for prize in prizes:
                    if not all(key in prize for key in ['target', 'prize']):
                        raise forms.ValidationError("Formato de premios progresivos inválido")
                    # Validar que el target sea mayor que los cartones ya vendidos
                    if self.instance and self.instance.total_cards_sold > 0:
                        if prize['target'] <= self.instance.total_cards_sold:
                            raise forms.ValidationError(
                                f"El nivel de {prize['target']} cartones debe ser mayor a los cartones ya vendidos ({self.instance.total_cards_sold})"
                            )
                cleaned_data['progressive_prizes'] = prizes
            except (json.JSONDecodeError, TypeError):
                raise forms.ValidationError("Formato de premios progresivos inválido")
        else:
            # Si no hay JSON, mantener los premios existentes o dejarlos vacíos
            if not cleaned_data.get('progressive_prizes'):
                cleaned_data['progressive_prizes'] = []
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Recalcular el premio con los nuevos niveles progresivos
        if commit:
            instance.save()
            # Actualizar el premio según los nuevos niveles
            instance.prize = instance.calculate_prize()
            instance.save()
        
        return instance

class CreditRequestForm(forms.ModelForm):
    payment_method = forms.ModelChoiceField(
        queryset=BankAccount.objects.filter(is_active=True),
        empty_label="Selecciona un método de pago",
        label="Método de Pago",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CreditRequest
        fields = ['amount', 'payment_method', 'proof']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '0.01'
            }),
            'proof': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf'
            })
        }

class RaffleForm(forms.ModelForm):
    is_manual_winner = forms.BooleanField(required=False, label="Selección manual de ganador")

    class Meta:
        model = Raffle
        fields = ['title', 'description', 'ticket_price', 'prize', 
                 'start_number', 'end_number', 'draw_date', 'is_manual_winner']
        widgets = {
            'draw_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'ticket_price': forms.NumberInput(attrs={
                'min': '0.50',
                'step': '0.50'
            }),
            'prize': forms.NumberInput(attrs={
                'min': '1',
                'step': '1'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_number')
        end = cleaned_data.get('end_number')
        
        if start and end and start >= end:
            raise forms.ValidationError("El número final debe ser mayor que el inicial")
        
        return cleaned_data

class BuyTicketForm(forms.Form):
    number = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de ticket'
        })
    )

class PercentageSettingsForm(forms.ModelForm):
    class Meta:
        model = PercentageSettings
        fields = [
            'platform_commission', 'image_promotion_price', 'video_promotion_price',
            'game_creation_fee', 'game_creation_fee_enabled', 'platform_commission_enabled',
            'credits_purchase_enabled', 'credits_withdrawal_enabled',
            'referral_system_enabled', 'promotions_enabled'
        ]
        widgets = {
            'platform_commission': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'image_promotion_price': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
            'video_promotion_price': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
            'game_creation_fee': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
            'game_creation_fee_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'platform_commission_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'credits_purchase_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'credits_withdrawal_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'referral_system_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'promotions_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'platform_commission': 'Comisión de la plataforma (%)',
            'image_promotion_price': 'Precio de promoción con imagen ($)',
            'video_promotion_price': 'Precio de promoción con video ($)',
            'game_creation_fee': 'Tarifa de creación de juego ($)',
            'game_creation_fee_enabled': 'Activar tarifa de creación',
            'platform_commission_enabled': 'Activar comisión por cartón',
        }
    

class UserWithdrawalRequestForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['amount', 'bank_name', 'account_number', 'account_holder_name']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 0.01, 'step': 0.01}),
        }
        labels = {
            'amount': 'Monto a retirar',
            'bank_name': 'Nombre del banco',
            'account_number': 'Número de cuenta',
            'account_holder_name': 'Nombre del titular',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class AdminWithdrawalProcessForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['status', 'admin_notes', 'transaction_reference', 'proof_screenshot']
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 3}),
            'proof_screenshot': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'status': 'Estado de la Solicitud',
            'admin_notes': 'Notas del Administrador',
            'transaction_reference': 'Referencia de Transacción',
            'proof_screenshot': 'Comprobante de Retiro (Captura de Pantalla)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['title', 'details', 'instructions', 'order', 'is_active']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 4}),
            'instructions': forms.Textarea(attrs={'rows': 2}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
        labels = {
            'title': 'Nombre del método',
            'details': 'Detalles de pago',
            'instructions': 'Instrucciones especiales',
            'order': 'Orden de visualización',
            'is_active': 'Activo',
        }

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            'announcement_type', 'message', 'image', 'video_url', 
            'external_link', 'related_game', 'related_raffle', 
            'order', 'is_active'
        ]
        widgets = {
            'announcement_type': forms.Select(attrs={'id': 'id_announcement_type'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Ocultar campos que dependen del tipo de anuncio inicialmente
        self.fields['external_link'].widget.attrs['class'] = 'form-control hidden-field'
        self.fields['related_game'].widget.attrs['class'] = 'form-select hidden-field'
        self.fields['related_raffle'].widget.attrs['class'] = 'form-select hidden-field'
        self.fields['image'].widget.attrs['class'] = 'form-control hidden-field'
        self.fields['video_url'].widget.attrs['class'] = 'form-control hidden-field'

        # Filtrar juegos y rifas por el usuario si es un organizador
        if user and not user.is_staff:
            self.fields['related_game'].queryset = Game.objects.filter(organizer=user, is_finished=False)
            self.fields['related_raffle'].queryset = Raffle.objects.filter(organizer=user, status__in=['WAITING', 'IN_PROGRESS'])


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['related_game', 'related_raffle', 'message', 'image', 'video_url']
        labels = {
            'related_game': 'Juego a Promocionar',
            'related_raffle': 'Rifa a Promocionar',
            'message': 'Mensaje del Anuncio',
        }
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        self.fields['related_game'].queryset = Game.objects.filter(organizer=user, is_finished=False)
        self.fields['related_raffle'].queryset = Raffle.objects.filter(organizer=user, status__in=['WAITING', 'IN_PROGRESS'])
        
        self.fields['related_game'].required = False
        self.fields['related_raffle'].required = False

        # Apply form-control class to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['message']: # These already have widgets defined
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        game = cleaned_data.get('related_game')
        raffle = cleaned_data.get('related_raffle')
        image = cleaned_data.get('image')
        video_url = cleaned_data.get('video_url')

        if not game and not raffle:
            raise ValidationError("Debes seleccionar un juego o una rifa para promocionar.")
        
        if game and raffle:
            raise ValidationError("Solo puedes promocionar un evento a la vez (un juego o una rifa).")
        
        if image and video_url:
            raise ValidationError("No puedes subir una imagen y un video al mismo tiempo.")
        
        if not image and not video_url:
            raise ValidationError("Debes subir una imagen o proporcionar una URL de video.")

        return cleaned_data

class GeneralAnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['message', 'image', 'video_url', 'order', 'is_active']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'message': 'Mensaje del anuncio',
            'image': 'Imagen del anuncio (opcional)',
            'video_url': 'URL de Video (opcional, ej: YouTube)',
            'order': 'Orden de visualización',
            'is_active': 'Activo'
        }

class ExternalAdForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['message', 'image', 'video_url', 'external_link', 'order', 'is_active']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'external_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'message': 'Mensaje del anuncio',
            'image': 'Imagen del anuncio (opcional)',
            'video_url': 'URL de Video (opcional, ej: YouTube)',
            'external_link': 'Enlace externo (opcional)',
            'order': 'Orden de visualización',
            'is_active': 'Activo'
        }


class AccountsReceivableForm(forms.ModelForm):
    """Formulario para crear una cuenta por cobrar"""
    debtor = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Usuario Deudor",
        help_text="Selecciona el usuario que debe el dinero"
    )
    
    class Meta:
        model = AccountsReceivable
        fields = ['debtor', 'amount', 'concept']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'concept': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el concepto de la deuda...'
            })
        }
        labels = {
            'amount': 'Monto que Debe',
            'concept': 'Concepto de la Deuda'
        }
    
    def __init__(self, *args, **kwargs):
        organizer = kwargs.pop('organizer', None)
        super().__init__(*args, **kwargs)
        if organizer:
            # Filtrar usuarios que no sean el organizador mismo
            self.fields['debtor'].queryset = User.objects.exclude(id=organizer.id)


class AccountsReceivablePaymentForm(forms.ModelForm):
    """Formulario para realizar un abono a una cuenta por cobrar"""
    
    class Meta:
        model = AccountsReceivablePayment
        fields = ['amount', 'payment_method', 'proof', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'proof': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)...'
            })
        }
        labels = {
            'amount': 'Monto del Abono',
            'payment_method': 'Método de Pago',
            'proof': 'Comprobante de Pago',
            'notes': 'Notas'
        }
    
    def __init__(self, *args, **kwargs):
        account_receivable = kwargs.pop('account_receivable', None)
        super().__init__(*args, **kwargs)
        # Solo mostrar métodos de pago activos
        self.fields['payment_method'].queryset = BankAccount.objects.filter(is_active=True)
        if account_receivable:
            # Establecer el máximo permitido como el saldo pendiente
            remaining = account_receivable.remaining_balance
            self.fields['amount'].widget.attrs['max'] = str(remaining)
            self.fields['amount'].help_text = f'Máximo permitido: ${remaining}'
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise ValidationError('El monto debe ser mayor a cero.')
        return amount
    
    def clean_proof(self):
        proof = self.cleaned_data.get('proof')
        if proof:
            # Validar tamaño (máximo 5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if proof.size > max_size:
                raise ValidationError(
                    f"El archivo no debe exceder 5MB. Tamaño actual: {proof.size / (1024*1024):.2f}MB"
                )
            
            # Validar tipo de contenido
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
            if proof.content_type not in allowed_types:
                raise ValidationError(
                    "Solo se permiten archivos JPG, PNG o PDF"
                )
            
            # Validar extensión
            valid_extensions = ['jpg', 'jpeg', 'png', 'pdf']
            ext = proof.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise ValidationError(
                    f"Extensión no permitida: {ext}. Solo se permiten: {', '.join(valid_extensions)}"
                )
        
        return proof
