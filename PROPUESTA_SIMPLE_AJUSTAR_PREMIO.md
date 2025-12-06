# 💡 PROPUESTA SIMPLE: Ajustar Premio Base Antes de Iniciar

## 🎯 **OPCIÓN SIMPLE Y DIRECTA**

### **Concepto:**
Permitir al organizador ajustar el premio base ANTES de iniciar el juego, ajustando automáticamente los créditos bloqueados.

---

## 📋 **CÓMO FUNCIONARÍA:**

### **Escenario Inicial:**
```
Premio base: 30 créditos
Créditos bloqueados: 30 créditos
Saldo disponible: 100 créditos
Ventas: 100 cartones × 1 crédito = 100 créditos recaudados
```

### **El Organizador Quiere:**
Aumentar el premio de 30 a 70 créditos

### **Qué Pasa:**
```
Premio base actual: 30 créditos
Nuevo premio base: 70 créditos
Diferencia: +40 créditos

Ajuste automático:
1. Se bloquean 40 créditos adicionales del saldo disponible
2. Créditos bloqueados: 30 + 40 = 70 créditos
3. Saldo disponible: 100 - 40 = 60 créditos
4. Premio base actualizado: 70 créditos
```

---

## 🔧 **IMPLEMENTACIÓN SIMPLE:**

### **1. En la Página de Editar Configuración:**

Añadir un campo para ajustar el premio base:

```html
<div class="mb-4">
    <h5>Premio Base del Juego</h5>
    
    <div class="alert alert-info">
        <p><strong>Premio actual:</strong> {{ game.base_prize }} créditos</p>
        <p><strong>Créditos bloqueados:</strong> {{ organizer.blocked_credits }} créditos</p>
        <p><strong>Saldo disponible:</strong> {{ organizer.credit_balance }} créditos</p>
        <p><strong>Ventas actuales:</strong> {{ game.held_balance }} créditos recaudados</p>
    </div>
    
    <label>Nuevo Premio Base (créditos)</label>
    <input type="number" name="new_base_prize" 
           value="{{ game.base_prize }}" 
           min="0" 
           step="1"
           required>
    
    <div id="prize-adjustment-preview">
        <!-- Se calcula automáticamente con JavaScript -->
        <p>Diferencia: <span id="prize-difference">0</span> créditos</p>
        <p>Nuevos créditos bloqueados: <span id="new-blocked">0</span> créditos</p>
        <p>Saldo disponible después: <span id="new-balance">0</span> créditos</p>
    </div>
</div>
```

---

### **2. En el Formulario (GameEditForm):**

Añadir campo para el premio base:

```python
class GameEditForm(forms.ModelForm):
    new_base_prize = forms.DecimalField(
        required=False,
        min_value=0,
        help_text="Ajustar el premio base del juego"
    )
    
    def clean_new_base_prize(self):
        new_prize = self.cleaned_data.get('new_base_prize')
        if new_prize is not None:
            current_prize = self.instance.base_prize
            diferencia = new_prize - current_prize
            
            # Validar que tenga suficiente saldo si aumenta
            if diferencia > 0:
                if self.instance.organizer.credit_balance < diferencia:
                    raise forms.ValidationError(
                        f"No tienes suficiente saldo. Necesitas {diferencia} créditos adicionales."
                    )
        
        return new_prize
```

---

### **3. En la Vista (edit_game_config):**

Procesar el ajuste del premio:

```python
@login_required
def edit_game_config(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # Validaciones de seguridad
    if game.organizer != request.user:
        return error("No eres el organizador")
    
    if game.is_started:
        return error("No se puede editar después de iniciar")
    
    if request.method == 'POST':
        form = GameEditForm(request.POST, instance=game)
        
        if form.is_valid():
            new_base_prize = form.cleaned_data.get('new_base_prize')
            
            if new_base_prize is not None:
                # Calcular diferencia
                diferencia = new_base_prize - game.base_prize
                
                try:
                    with transaction.atomic():
                        organizer = request.user
                        
                        if diferencia > 0:  # AUMENTAR premio
                            # Bloquear créditos adicionales
                            if organizer.credit_balance >= diferencia:
                                organizer.credit_balance -= diferencia
                                organizer.blocked_credits += diferencia
                                organizer.save()
                                
                                # Actualizar premio
                                game.base_prize = new_base_prize
                                game.prize = new_base_prize  # Actualizar premio total
                                game.save()
                                
                                # Registrar transacción
                                Transaction.objects.create(
                                    user=organizer,
                                    amount=-diferencia,
                                    transaction_type='PRIZE_LOCK',
                                    description=f"Ajuste de premio base: {game.base_prize} → {new_base_prize}",
                                    related_game=game
                                )
                                
                                messages.success(request, 
                                    f'Premio aumentado de {game.base_prize} a {new_base_prize} créditos. '
                                    f'Se bloquearon {diferencia} créditos adicionales.'
                                )
                            else:
                                messages.error(request, 
                                    f'Saldo insuficiente. Necesitas {diferencia} créditos adicionales.'
                                )
                                return render(...)
                        
                        elif diferencia < 0:  # REDUCIR premio
                            # Desbloquear créditos
                            diferencia_abs = abs(diferencia)
                            
                            # Verificar que hay suficientes bloqueados
                            if organizer.blocked_credits >= diferencia_abs:
                                organizer.blocked_credits -= diferencia_abs
                                organizer.credit_balance += diferencia_abs
                                organizer.save()
                                
                                # Actualizar premio
                                game.base_prize = new_base_prize
                                game.prize = new_base_prize
                                game.save()
                                
                                # Registrar transacción
                                Transaction.objects.create(
                                    user=organizer,
                                    amount=diferencia_abs,
                                    transaction_type='PRIZE_UNLOCK',
                                    description=f"Reducción de premio base: {game.base_prize} → {new_base_prize}",
                                    related_game=game
                                )
                                
                                messages.success(request, 
                                    f'Premio reducido de {game.base_prize} a {new_base_prize} créditos. '
                                    f'Se desbloquearon {diferencia_abs} créditos.'
                                )
                            else:
                                messages.error(request, 
                                    'No hay suficientes créditos bloqueados para reducir el premio.'
                                )
                                return render(...)
                        
                        else:  # diferencia == 0, no hay cambio
                            pass
                
                except Exception as e:
                    messages.error(request, f'Error al ajustar premio: {str(e)}')
            
            # Guardar otros cambios del formulario
            game = form.save()
            return redirect('game_room', game_id=game.id)
```

---

## 📊 **EJEMPLO PASO A PASO:**

### **Situación Inicial:**
```
Organizador: angel
Saldo disponible: 100 créditos
Créditos bloqueados: 30 créditos (premio base)
Juego: "Bingo de Navidad"
Premio base: 30 créditos
Ventas: 100 cartones × 1 = 100 créditos recaudados
```

### **El Organizador Quiere Aumentar a 70:**

**Paso 1: Entra a "Editar Configuración"**

**Paso 2: Ve el formulario:**
```
Premio Base del Juego
─────────────────────
Premio actual: 30 créditos
Créditos bloqueados: 30 créditos
Saldo disponible: 100 créditos
Ventas actuales: 100 créditos recaudados

Nuevo Premio Base: [70] créditos

Vista Previa:
- Diferencia: +40 créditos
- Nuevos créditos bloqueados: 70 créditos
- Saldo disponible después: 60 créditos
```

**Paso 3: Guarda los cambios**

**Paso 4: El sistema hace:**
```
1. Calcula diferencia: 70 - 30 = +40 créditos
2. Verifica saldo: 100 >= 40 ✅
3. Bloquea 40 créditos adicionales:
   - credit_balance: 100 - 40 = 60
   - blocked_credits: 30 + 40 = 70
4. Actualiza premio:
   - base_prize: 30 → 70
   - prize: 30 → 70
5. Registra transacción
```

**Paso 5: Resultado:**
```
Premio base: 70 créditos ✅
Créditos bloqueados: 70 créditos ✅
Saldo disponible: 60 créditos ✅
```

---

## ⚠️ **VALIDACIONES Y RESTRICCIONES:**

### **1. Solo Antes de Iniciar:**
```python
if game.is_started:
    return error("No se puede ajustar después de iniciar el juego")
```

### **2. Verificar Saldo:**
```python
if diferencia > 0:  # Aumentar
    if organizer.credit_balance < diferencia:
        return error("Saldo insuficiente")
```

### **3. Verificar Créditos Bloqueados (si reduce):**
```python
if diferencia < 0:  # Reducir
    if organizer.blocked_credits < abs(diferencia):
        return error("No hay suficientes créditos bloqueados")
```

### **4. Límite Mínimo (opcional):**
```python
if new_base_prize < 10:  # Ejemplo: mínimo 10 créditos
    return error("El premio mínimo es 10 créditos")
```

### **5. Límite Máximo (opcional):**
```python
max_prize = game.held_balance + organizer.credit_balance
if new_base_prize > max_prize:
    return error(f"El premio máximo es {max_prize} créditos")
```

---

## 🎨 **INTERFAZ DE USUARIO:**

### **En la Página de Editar Configuración:**

```html
<!-- Sección de Premio Base -->
<div class="card mb-4">
    <div class="card-header">
        <h5><i class="fas fa-trophy me-2"></i>Ajustar Premio Base</h5>
    </div>
    <div class="card-body">
        <!-- Estado Actual -->
        <div class="row mb-3">
            <div class="col-md-6">
                <p><strong>Premio Actual:</strong> {{ game.base_prize }} créditos</p>
                <p><strong>Créditos Bloqueados:</strong> {{ organizer.blocked_credits }} créditos</p>
            </div>
            <div class="col-md-6">
                <p><strong>Saldo Disponible:</strong> {{ organizer.credit_balance }} créditos</p>
                <p><strong>Ventas Recaudadas:</strong> {{ game.held_balance }} créditos</p>
            </div>
        </div>
        
        <!-- Campo de Ajuste -->
        <div class="mb-3">
            <label for="id_new_base_prize" class="form-label">
                Nuevo Premio Base (créditos)
            </label>
            <input type="number" 
                   class="form-control" 
                   id="id_new_base_prize" 
                   name="new_base_prize"
                   value="{{ game.base_prize }}"
                   min="0"
                   step="1"
                   oninput="updatePrizePreview(this.value)">
        </div>
        
        <!-- Vista Previa en Tiempo Real -->
        <div id="prize-preview" class="alert alert-info" style="display: none;">
            <h6>Vista Previa del Ajuste:</h6>
            <p id="preview-difference"></p>
            <p id="preview-blocked"></p>
            <p id="preview-balance"></p>
        </div>
    </div>
</div>
```

### **JavaScript para Vista Previa:**

```javascript
function updatePrizePreview(newPrize) {
    const currentPrize = {{ game.base_prize }};
    const currentBlocked = {{ organizer.blocked_credits }};
    const currentBalance = {{ organizer.credit_balance }};
    
    const diferencia = parseFloat(newPrize) - currentPrize;
    const previewDiv = document.getElementById('prize-preview');
    
    if (diferencia !== 0) {
        previewDiv.style.display = 'block';
        
        if (diferencia > 0) {
            // Aumentar
            const newBlocked = currentBlocked + diferencia;
            const newBalance = currentBalance - diferencia;
            
            document.getElementById('preview-difference').innerHTML = 
                `<strong>Diferencia:</strong> +${diferencia} créditos (aumentar)`;
            document.getElementById('preview-blocked').innerHTML = 
                `<strong>Nuevos créditos bloqueados:</strong> ${newBlocked} créditos`;
            document.getElementById('preview-balance').innerHTML = 
                `<strong>Saldo disponible después:</strong> ${newBalance} créditos`;
            
            // Validar saldo
            if (newBalance < 0) {
                previewDiv.className = 'alert alert-danger';
                previewDiv.innerHTML += '<p class="text-danger"><strong>⚠️ Saldo insuficiente</strong></p>';
            } else {
                previewDiv.className = 'alert alert-info';
            }
        } else {
            // Reducir
            const diferenciaAbs = Math.abs(diferencia);
            const newBlocked = currentBlocked - diferenciaAbs;
            const newBalance = currentBalance + diferenciaAbs;
            
            document.getElementById('preview-difference').innerHTML = 
                `<strong>Diferencia:</strong> -${diferenciaAbs} créditos (reducir)`;
            document.getElementById('preview-blocked').innerHTML = 
                `<strong>Nuevos créditos bloqueados:</strong> ${newBlocked} créditos`;
            document.getElementById('preview-balance').innerHTML = 
                `<strong>Saldo disponible después:</strong> ${newBalance} créditos`;
            
            // Validar créditos bloqueados
            if (newBlocked < 0) {
                previewDiv.className = 'alert alert-danger';
                previewDiv.innerHTML += '<p class="text-danger"><strong>⚠️ No hay suficientes créditos bloqueados</strong></p>';
            } else {
                previewDiv.className = 'alert alert-warning';
                previewDiv.innerHTML += '<p class="text-warning"><strong>⚠️ Reducir el premio puede decepcionar a los jugadores</strong></p>';
            }
        }
    } else {
        previewDiv.style.display = 'none';
    }
}
```

---

## 📝 **FLUJO COMPLETO:**

### **1. Organizador entra a "Editar Configuración"**

### **2. Ve la sección "Ajustar Premio Base":**
```
┌─────────────────────────────────────────┐
│ Ajustar Premio Base                    │
├─────────────────────────────────────────┤
│ Premio Actual: 30 créditos             │
│ Créditos Bloqueados: 30 créditos       │
│ Saldo Disponible: 100 créditos         │
│ Ventas Recaudadas: 100 créditos        │
│                                         │
│ Nuevo Premio Base: [70] créditos       │
│                                         │
│ Vista Previa:                          │
│ - Diferencia: +40 créditos (aumentar) │
│ - Nuevos créditos bloqueados: 70       │
│ - Saldo disponible después: 60         │
└─────────────────────────────────────────┘
```

### **3. Guarda los cambios**

### **4. El sistema procesa:**
```
✅ Verifica que el juego no haya iniciado
✅ Calcula diferencia: +40 créditos
✅ Verifica saldo: 100 >= 40 ✅
✅ Bloquea 40 créditos adicionales
✅ Actualiza premio base: 30 → 70
✅ Registra transacción
✅ Notifica éxito
```

### **5. Resultado:**
```
Premio base: 70 créditos ✅
Créditos bloqueados: 70 créditos ✅
Saldo disponible: 60 créditos ✅
```

---

## ⚠️ **ADVERTENCIAS Y PROTECCIONES:**

### **1. Si Aumenta el Premio:**
- ✅ Verificar que tenga suficiente saldo
- ✅ Mostrar advertencia si queda poco saldo
- ✅ Notificar a jugadores (opcional)

### **2. Si Reduce el Premio:**
- ⚠️ **ADVERTENCIA:** "Reducir el premio puede decepcionar a los jugadores"
- ⚠️ Confirmar antes de reducir
- ⚠️ Verificar que haya suficientes créditos bloqueados

### **3. Validaciones:**
- ✅ Solo antes de iniciar
- ✅ Solo el organizador
- ✅ Saldo suficiente
- ✅ Límites mínimos/máximos (opcional)

---

## 💡 **VENTAJAS DE ESTA OPCIÓN:**

1. ✅ **Simple:** Solo ajustar un número
2. ✅ **Directo:** Se bloquea/desbloquea automáticamente
3. ✅ **Transparente:** Muestra exactamente qué pasa
4. ✅ **Seguro:** Validaciones claras
5. ✅ **Flexible:** Puede aumentar o reducir

---

## 📊 **EJEMPLO COMPLETO:**

### **Caso 1: Aumentar Premio**
```
Antes:
- Premio: 30 créditos
- Bloqueados: 30 créditos
- Disponible: 100 créditos

Ajuste: 30 → 70 créditos

Después:
- Premio: 70 créditos ✅
- Bloqueados: 70 créditos (30 + 40)
- Disponible: 60 créditos (100 - 40)
```

### **Caso 2: Reducir Premio**
```
Antes:
- Premio: 70 créditos
- Bloqueados: 70 créditos
- Disponible: 60 créditos

Ajuste: 70 → 50 créditos

Después:
- Premio: 50 créditos ✅
- Bloqueados: 50 créditos (70 - 20)
- Disponible: 80 créditos (60 + 20)
```

---

## 🎯 **RESUMEN:**

**Esta opción permite:**
- ✅ Ajustar el premio base antes de iniciar
- ✅ Aumentar: Bloquea créditos adicionales del saldo
- ✅ Reducir: Desbloquea créditos proporcionalmente
- ✅ Vista previa en tiempo real
- ✅ Validaciones automáticas
- ✅ Transacciones registradas

**Es simple porque:**
- Solo un campo: "Nuevo Premio Base"
- El sistema calcula todo automáticamente
- Muestra claramente qué pasa antes de guardar
- No requiere cálculos complejos del usuario

---

**¿Te parece bien esta opción?** Es la más simple y directa. El organizador solo cambia un número y el sistema ajusta todo automáticamente.








