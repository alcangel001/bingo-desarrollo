# 📱 ESPECIFICACIONES PARA IMAGEN DE LOGIN EN MÓVILES

## 🎯 OBJETIVO
Crear una imagen donde el texto "BINGO Y RIFA JyM" se vea perfectamente centrado y visible en móviles.

## 📐 DIMENSIONES RECOMENDADAS PARA MÓVILES

### Opción 1: Imagen Vertical (Recomendada)
**Dimensiones:** 1080 x 1920 píxeles (9:16 - proporción móvil)
- **Ancho:** 1080 píxeles
- **Alto:** 1920 píxeles
- **Proporción:** 9:16 (vertical, como los móviles)

### Opción 2: Imagen Cuadrada (Alternativa)
**Dimensiones:** 1080 x 1080 píxeles (1:1)
- Funciona bien en móviles y tablets
- El texto se ve completo

## 🎨 ÁREA SEGURA PARA EL TEXTO

### Posición del Texto Principal "BINGO Y RIFA"
- **Centro horizontal:** 540 píxeles (mitad del ancho)
- **Centro vertical:** 600-700 píxeles desde arriba (zona central superior)
- **Tamaño de fuente:** 140-160 píxeles
- **Color:** Amarillo/Dorado (#FFD700) con contorno rojo oscuro

### Posición del Subtítulo "JyM"
- **Centro horizontal:** 540 píxeles
- **Debajo de "BINGO Y RIFA":** 750-850 píxeles desde arriba
- **Tamaño de fuente:** 120-140 píxeles
- **Color:** Turquesa/Azul claro (#00C8C8) con contorno azul oscuro

## 📏 DISTRIBUCIÓN DE ELEMENTOS

### Zona Superior (0-400px)
- Bolas de bingo pequeñas
- Efectos decorativos
- **NO poner texto importante aquí**

### Zona Central (400-1200px) - ÁREA SEGURA PRINCIPAL
- **"BINGO Y RIFA"** centrado aquí
- **"JyM"** justo debajo
- Elementos decorativos alrededor (bolas, cartas)
- **Esta es la zona que SIEMPRE se verá en móviles**

### Zona Inferior (1200-1920px)
- Elementos decorativos
- Boleto de rifa
- **NO poner texto importante aquí**

## 🎨 DISEÑO RECOMENDADO

### Fondo
- Gradiente radial desde el centro
- Colores: Naranja/Amarillo en centro → Púrpura en bordes
- Efectos de luz/rayos desde el centro

### Elementos Decorativos
- **Lado izquierdo:** Bolas de bingo (7, 17, 29) y cartas
- **Centro:** Texto principal "BINGO Y RIFA JyM"
- **Lado derecho:** Jaula de bingo y bola dentro
- **Inferior:** Boleto de rifa

### Tamaños de Elementos
- **Bolas grandes:** 100-120 píxeles de radio
- **Cartas:** 180 x 220 píxeles
- **Jaula:** 200 x 250 píxeles
- **Boleto:** 150 x 100 píxeles

## ✅ CHECKLIST PARA CREAR LA IMAGEN

- [ ] Dimensiones: 1080 x 1920 píxeles (vertical)
- [ ] Texto "BINGO Y RIFA" centrado horizontalmente
- [ ] Texto "BINGO Y RIFA" a 600-700px desde arriba
- [ ] Texto "JyM" centrado y debajo del anterior
- [ ] Elementos importantes en zona central (400-1200px)
- [ ] Fondo con gradiente radial
- [ ] Formato: PNG (alta calidad)
- [ ] Tamaño de archivo: < 500KB

## 📱 CÓMO SE VERÁ EN MÓVILES

Con estas dimensiones (1080x1920):
- La imagen llenará toda la pantalla del móvil
- El texto estará perfectamente centrado
- No se recortará nada importante
- Se verá completa de arriba a abajo

## 🔧 CSS QUE SE USARÁ

```css
@media (max-width: 767px) {
    .login-container {
        background-image: url('bingo_login_background_mobile.png');
        background-size: cover;
        background-position: center center;
    }
}
```

## 📝 NOTAS IMPORTANTES

1. **Mantén el texto en el centro:** Entre 400-1200px verticalmente
2. **Usa colores contrastantes:** Para que el texto se lea bien
3. **No pongas elementos importantes en los bordes:** Se pueden recortar
4. **Prueba en diferentes móviles:** iPhone, Android, diferentes tamaños

