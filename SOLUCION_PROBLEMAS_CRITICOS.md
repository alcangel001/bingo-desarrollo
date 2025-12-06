# 🔧 SOLUCIONES A PROBLEMAS CRÍTICOS - IMPLEMENTACIÓN

## 📋 ÍNDICE DE SOLUCIONES

1. [Solución 1: Validación de saldo negativo](#solucion-1)
2. [Solución 2: Validaciones antes de descontar](#solucion-2)
3. [Solución 3: Transacciones atómicas](#solucion-3)
4. [Solución 4: Validación de SECRET_KEY](#solucion-4)
5. [Solución 5: Rate limiting](#solucion-5)
6. [Bonus: Validación de archivos](#solucion-6)

---

<a name="solucion-1"></a>
## 🔒 SOLUCIÓN 1: Validación de Saldo Negativo

### Archivo: `bingo_app/models.py`

**BUSCA** (línea 28):
```python
credit_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
```

**REEMPLAZA CON:**
```python
credit_balance = models.DecimalField(
    max_digits=10, 
    decimal_places=2, 
    default=Decimal('0.00'),
    validators=[MinValueValidator(Decimal('0.00'))],
    help_text="Saldo de créditos del usuario. No puede ser negativo."
)
```

**También actualiza blocked_credits** (línea 29):
```python
blocked_credits = models.DecimalField(
    max_digits=10, 
    decimal_places=2, 
    default=Decimal('0.00'),
    validators=[MinValueValidator(Decimal('0.00'))],
    help_text="Créditos bloqueados por premios. No puede ser negativo."
)
```

**Después de hacer estos cambios, crea una migración:**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

<a name="solucion-2"></a>
## 💰 SOLUCIÓN 2: Validaciones Antes de Descontar

### Archivo: `bingo_app/views.py`

### 2.1 - Compra de entrada al juego (línea ~376)

**BUSCA:**
```python
if not is_organizer:
    # Charge entry fee
    request.user.credit_balance -= game.entry_price
    request.user.save()
```

**REEMPLAZA CON:**
```python
if not is_organizer:
    # Validar saldo antes de cobrar
    if request.user.credit_balance < game.entry_price:
        messages.error(request, f'Saldo insuficiente. Necesitas ${game.entry_price} créditos para entrar.')
        return redirect('lobby')
    
    # Charge entry fee
    request.user.credit_balance -= game.entry_price
    request.user.save()
```

---

### 2.2 - Compra de cartón (línea ~410)

**BUSCA:**
```python
# Charge for card
request.user.credit_balance -= game.card_price
request.user.save()
```

**REEMPLAZA CON:**
```python
# Validar saldo antes de cobrar
if request.user.credit_balance < game.card_price:
    messages.error(request, f'Saldo insuficiente. Necesitas ${game.card_price} créditos.')
    return redirect('game_room', game_id=game.id)

# Charge for card
request.user.credit_balance -= game.card_price
request.user.save()
```

---

### 2.3 - Compra múltiple de cartones (línea ~764)

**BUSCA:**
```python
# Descontar créditos
request.user.credit_balance -= total_cost
request.user.save()
```

**REEMPLAZA CON:**
```python
# Validar saldo antes de descontar
if request.user.credit_balance < total_cost:
    messages.error(request, f'Saldo insuficiente. Necesitas ${total_cost} créditos.')
    return redirect('game_room', game_id=game.id)

# Descontar créditos
request.user.credit_balance -= total_cost
request.user.save()
```

---

### 2.4 - Compra de ticket de rifa (línea ~1181)

**BUSCA:**
```python
# Descontar créditos
request.user.credit_balance -= raffle.ticket_price
request.user.save()
```

**REEMPLAZA CON:**
```python
# Validar saldo antes de descontar
if request.user.credit_balance < raffle.ticket_price:
    messages.error(request, f'Saldo insuficiente. Necesitas ${raffle.ticket_price} créditos.')
    return redirect('raffle_detail', raffle_id=raffle.id)

# Descontar créditos
request.user.credit_balance -= raffle.ticket_price
request.user.save()
```

---

### 2.5 - Creación de juego (línea ~252)

**BUSCA:**
```python
# Descontar el premio base y la tarifa del saldo del organizador
request.user.credit_balance -= total_cost
# Bloquear el premio base en blocked_credits
request.user.blocked_credits += base_prize
request.user.save()
```

**REEMPLAZA CON:**
```python
# Validar saldo antes de descontar
if request.user.credit_balance < total_cost:
    messages.error(request, f'Saldo insuficiente. Necesitas ${total_cost} créditos para crear este juego.')
    return render(request, 'bingo_app/create_game.html', {'form': form})

# Descontar el premio base y la tarifa del saldo del organizador
request.user.credit_balance -= total_cost
# Bloquear el premio base en blocked_credits
request.user.blocked_credits += base_prize
request.user.save()
```

---

### 2.6 - Creación de rifa (línea ~1081)

**BUSCA:**
```python
# Descontar el premio del saldo del organizador
request.user.credit_balance -= raffle.prize
# Bloquear el premio en blocked_credits
request.user.blocked_credits += raffle.prize
request.user.save()
```

**REEMPLAZA CON:**
```python
# Validar saldo antes de descontar
if request.user.credit_balance < raffle.prize:
    messages.error(request, f'Saldo insuficiente. Necesitas ${raffle.prize} créditos para crear esta rifa.')
    return render(request, 'bingo_app/create_raffle.html', {'form': form})

# Descontar el premio del saldo del organizador
request.user.credit_balance -= raffle.prize
# Bloquear el premio en blocked_credits
request.user.blocked_credits += raffle.prize
request.user.save()
```

---

<a name="solucion-3"></a>
## 🔐 SOLUCIÓN 3: Transacciones Atómicas

### 3.1 - Compra de cartón con transacción atómica

**BUSCA en buy_card (línea ~400):**
```python
@login_required
@require_http_methods(["POST"])
def buy_card(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # ... código existente ...
    
    # Validar saldo antes de cobrar
    if request.user.credit_balance < game.card_price:
        messages.error(request, f'Saldo insuficiente. Necesitas ${game.card_price} créditos.')
        return redirect('game_room', game_id=game.id)

    # Charge for card
    request.user.credit_balance -= game.card_price
    request.user.save()
    
    # Record transaction
    Transaction.objects.create(...)
    
    # Add card to player
    player.cards.append(card)
    player.save()
```

**REEMPLAZA CON:**
```python
@login_required
@require_http_methods(["POST"])
def buy_card(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # ... código existente ...
    
    try:
        with transaction.atomic():
            # Bloquear al usuario para evitar race conditions
            user = User.objects.select_for_update().get(id=request.user.id)
            
            # Validar saldo
            if user.credit_balance < game.card_price:
                messages.error(request, f'Saldo insuficiente. Necesitas ${game.card_price} créditos.')
                return redirect('game_room', game_id=game.id)
            
            # Charge for card
            user.credit_balance -= game.card_price
            user.save()
            
            # Record transaction
            Transaction.objects.create(
                user=user,
                amount=-game.card_price,
                transaction_type='PURCHASE',
                description=f"Compra de cartón en {game.name}",
                related_game=game
            )
            
            # Add card to player
            player = Player.objects.get(user=user, game=game)
            player.cards.append(card)
            player.save()
            
            # Actualizar total de cartones vendidos
            game.total_cards_sold += 1
            game.save()
            
            messages.success(request, 'Cartón comprado exitosamente')
    except Exception as e:
        messages.error(request, f'Error al comprar cartón: {str(e)}')
        logger.error(f"Error en buy_card: {str(e)}", exc_info=True)
        return redirect('game_room', game_id=game.id)
    
    return redirect('game_room', game_id=game.id)
```

---

### 3.2 - Compra de entrada al juego con transacción atómica

**BUSCA en game_room (línea ~370):**
```python
if not is_organizer:
    # Validar saldo antes de cobrar
    if request.user.credit_balance < game.entry_price:
        messages.error(request, f'Saldo insuficiente.')
        return redirect('lobby')
    
    # Charge entry fee
    request.user.credit_balance -= game.entry_price
    request.user.save()
    
    # Record transaction
    Transaction.objects.create(...)
```

**REEMPLAZA CON:**
```python
if not is_organizer:
    try:
        with transaction.atomic():
            # Bloquear usuario
            user = User.objects.select_for_update().get(id=request.user.id)
            
            # Validar saldo
            if user.credit_balance < game.entry_price:
                messages.error(request, f'Saldo insuficiente. Necesitas ${game.entry_price} créditos.')
                return redirect('lobby')
            
            # Charge entry fee
            user.credit_balance -= game.entry_price
            user.save()
            
            # Record transaction
            Transaction.objects.create(
                user=user,
                amount=-game.entry_price,
                transaction_type='PURCHASE',
                description=f"Entrada al juego {game.name}",
                related_game=game
            )
    except Exception as e:
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        logger.error(f"Error en game_room payment: {str(e)}", exc_info=True)
        return redirect('lobby')
```

---

<a name="solucion-4"></a>
## 🔑 SOLUCIÓN 4: Validación de SECRET_KEY

### Archivo: `bingo_project/settings.py`

**BUSCA (línea 43):**
```python
SECRET_KEY = os.environ.get("SECRET_KEY")
```

**REEMPLAZA CON:**
```python
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        # Solo para desarrollo local
        SECRET_KEY = 'django-insecure-local-dev-key-CHANGE-IN-PRODUCTION'
        print("⚠️  WARNING: Using insecure SECRET_KEY for development")
    else:
        # En producción, DEBE estar configurada
        raise ValueError(
            "SECRET_KEY no está configurada en las variables de entorno. "
            "Esta variable es REQUERIDA en producción. "
            "Configúrala en Railway con: railway variables set SECRET_KEY=<tu-clave-segura>"
        )
```

**Para generar una SECRET_KEY segura:**
```python
# Ejecuta esto en Python para generar una clave segura:
import secrets
print(secrets.token_urlsafe(50))
```

**Luego configúrala en Railway:**
```bash
railway variables set SECRET_KEY="tu-clave-generada-aqui"
```

---

<a name="solucion-5"></a>
## ⏱️ SOLUCIÓN 5: Rate Limiting

### 5.1 - Instalar django-ratelimit

```bash
pip install django-ratelimit
```

**Agregar a `requirements.txt`:**
```
django-ratelimit==4.1.0
```

---

### 5.2 - Aplicar rate limiting a vistas críticas

**Archivo: `bingo_app/views.py`**

**Agregar al inicio del archivo:**
```python
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
```

**Aplicar a login (si tienes una vista custom):**
```python
@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # Tu código de login
    ...
```

**Aplicar a registro:**
```python
@ratelimit(key='ip', rate='3/h', method='POST')
def register(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, 'Demasiados intentos de registro. Intenta de nuevo más tarde.')
        return redirect('register')
    
    # Tu código existente...
```

**Aplicar a solicitud de créditos:**
```python
@ratelimit(key='user', rate='5/h', method='POST')
@login_required
def request_credits(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, 'Demasiadas solicitudes. Espera un momento antes de intentar nuevamente.')
        return redirect('profile')
    
    # Tu código existente...
```

**Aplicar a creación de juegos:**
```python
@ratelimit(key='user', rate='10/h', method='POST')
@login_required
def create_game(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, 'Demasiados juegos creados. Espera un momento.')
        return redirect('lobby')
    
    # Tu código existente...
```

---

### 5.3 - Manejar errores de rate limiting globalmente

**Archivo: `bingo_app/middleware.py`**

**Agregar al final:**
```python
from django_ratelimit.exceptions import Ratelimited
from django.shortcuts import render

class RatelimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            return render(request, 'bingo_app/ratelimited.html', status=429)
```

**Crear template: `bingo_app/templates/bingo_app/ratelimited.html`:**
```html
{% extends "bingo_app/base.html" %}

{% block content %}
<div class="container mt-5">
    <div class="alert alert-warning">
        <h2>⏱️ Demasiadas solicitudes</h2>
        <p>Has excedido el límite de solicitudes. Por favor, espera unos minutos antes de intentar nuevamente.</p>
        <a href="{% url 'lobby' %}" class="btn btn-primary mt-3">Volver al Lobby</a>
    </div>
</div>
{% endblock %}
```

**Agregar el middleware en `settings.py`:**
```python
MIDDLEWARE = [
    # ... otros middlewares ...
    'bingo_app.middleware.RatelimitMiddleware',  # AGREGAR AL FINAL
]
```

---

<a name="solucion-6"></a>
## 📎 SOLUCIÓN 6 (BONUS): Validación de Archivos

### Archivo: `bingo_app/forms.py`

**BUSCA la clase CreditRequestForm:**
```python
class CreditRequestForm(forms.ModelForm):
    class Meta:
        model = CreditRequest
        fields = ['amount', 'proof', 'payment_method']
```

**REEMPLAZA CON:**
```python
from django.core.validators import FileExtensionValidator

class CreditRequestForm(forms.ModelForm):
    class Meta:
        model = CreditRequest
        fields = ['amount', 'proof', 'payment_method']
    
    def clean_proof(self):
        proof = self.cleaned_data.get('proof')
        
        if proof:
            # Validar tamaño (máximo 5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if proof.size > max_size:
                raise forms.ValidationError(
                    f"El archivo no debe exceder 5MB. Tamaño actual: {proof.size / (1024*1024):.2f}MB"
                )
            
            # Validar tipo de contenido
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
            if proof.content_type not in allowed_types:
                raise forms.ValidationError(
                    "Solo se permiten archivos JPG, PNG o PDF"
                )
            
            # Validar extensión
            valid_extensions = ['jpg', 'jpeg', 'png', 'pdf']
            ext = proof.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f"Extensión no permitida: {ext}. Solo se permiten: {', '.join(valid_extensions)}"
                )
        
        return proof
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        # Validar que sea positivo
        if amount <= 0:
            raise forms.ValidationError("El monto debe ser mayor a 0")
        
        # Validar monto mínimo y máximo
        min_amount = Decimal('5.00')
        max_amount = Decimal('10000.00')
        
        if amount < min_amount:
            raise forms.ValidationError(f"El monto mínimo es ${min_amount}")
        
        if amount > max_amount:
            raise forms.ValidationError(f"El monto máximo es ${max_amount}")
        
        return amount
```

---

## 🧪 TESTING DESPUÉS DE IMPLEMENTAR

### Script de prueba rápida:

```bash
# Crear un script test_validaciones.py
```

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from bingo_app.models import User
from decimal import Decimal

print("🧪 PRUEBA 1: Intentar crear usuario con saldo negativo")
try:
    user = User.objects.create_user(
        username='test_negative',
        password='test123',
        credit_balance=Decimal('-10.00')
    )
    print("❌ FALLO: Se permitió saldo negativo")
except Exception as e:
    print(f"✅ ÉXITO: Se bloqueó saldo negativo - {type(e).__name__}")

print("\n🧪 PRUEBA 2: SECRET_KEY está configurada")
from django.conf import settings
if settings.SECRET_KEY and settings.SECRET_KEY != 'django-insecure-local-dev-key-CHANGE-IN-PRODUCTION':
    print("✅ ÉXITO: SECRET_KEY está configurada")
else:
    print("⚠️  ADVERTENCIA: Usando SECRET_KEY de desarrollo")

print("\n🧪 PRUEBA 3: ALLOWED_HOSTS configurado")
if settings.ALLOWED_HOSTS:
    print(f"✅ ÉXITO: ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
else:
    print("❌ FALLO: ALLOWED_HOSTS está vacío")

print("\n✅ PRUEBAS COMPLETADAS")
```

**Ejecutar:**
```bash
python test_validaciones.py
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

Marca cada item cuando lo completes:

- [ ] **1. Validación de saldo negativo en modelos**
- [ ] **2. Migración creada y aplicada**
- [ ] **3. Validaciones en buy_card**
- [ ] **4. Validaciones en game_room**
- [ ] **5. Validaciones en buy_multiple_cards**
- [ ] **6. Validaciones en buy_ticket (raffle)**
- [ ] **7. Validaciones en create_game**
- [ ] **8. Validaciones en create_raffle**
- [ ] **9. Transacción atómica en buy_card**
- [ ] **10. Transacción atómica en game_room**
- [ ] **11. Validación de SECRET_KEY**
- [ ] **12. Rate limiting instalado**
- [ ] **13. Rate limiting en registro**
- [ ] **14. Rate limiting en request_credits**
- [ ] **15. Rate limiting en create_game**
- [ ] **16. Middleware de ratelimit agregado**
- [ ] **17. Template de ratelimited creado**
- [ ] **18. Validación de archivos implementada**
- [ ] **19. Testing de validaciones**
- [ ] **20. Commit y push a GitHub**

---

## 🔄 ORDEN DE IMPLEMENTACIÓN RECOMENDADO

### Paso 1 (30 minutos):
1. Validación de saldo negativo en modelos
2. Crear y aplicar migración

### Paso 2 (1 hora):
3. Agregar todas las validaciones de saldo antes de descontar
4. Testing manual de cada función

### Paso 3 (1 hora):
5. Implementar transacciones atómicas en las 2 funciones críticas
6. Testing de race conditions

### Paso 4 (30 minutos):
7. Validación de SECRET_KEY
8. Instalar y configurar rate limiting

### Paso 5 (30 minutos):
9. Validación de archivos
10. Testing completo
11. Commit y deploy

**TIEMPO TOTAL ESTIMADO: 3-4 horas**

---

## 🆘 SI ALGO SALE MAL

### Restaurar desde backup:
```bash
cd "C:\Users\DELL VOSTRO 7500"
Expand-Archive -Path "backup_bingo_toggles_completo_22Oct2025.zip" -DestinationPath "bingo-restaurado"
```

### Revertir cambios en git:
```bash
git status
git checkout -- <archivo>  # Revertir un archivo específico
git reset --hard HEAD       # Revertir TODOS los cambios (CUIDADO)
```

### Restaurar migración:
```bash
python manage.py migrate bingo_app <numero_migracion_anterior>
```

---

## 📞 SOPORTE

Si encuentras problemas al implementar estas soluciones:
1. Lee los mensajes de error completos
2. Verifica que copiaste el código correctamente
3. Asegúrate de estar en el archivo correcto
4. Consulta la documentación de Django
5. Revisa los logs en `logs/django.log`

---

**¡Buena suerte con la implementación!** 🚀

