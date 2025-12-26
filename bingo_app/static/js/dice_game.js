// Lógica del juego de dados

document.addEventListener('DOMContentLoaded', function() {
    const rollBtn = document.getElementById('roll-dice-btn');
    
    if (rollBtn) {
        rollBtn.addEventListener('click', function() {
            rollDice();
        });
    }
});

function rollDice() {
    console.log('🎲 Función rollDice() llamada');
    const rollBtn = document.getElementById('roll-dice-btn');
    
    if (!rollBtn) {
        console.error('❌ No se encontró el botón roll-dice-btn');
        return;
    }
    
    // Verificar que el botón no esté deshabilitado
    if (rollBtn.disabled) {
        console.log('⚠️ El botón está deshabilitado. Estado:', rollBtn.disabled);
        return;
    }
    
    // Verificar conexión WebSocket
    if (!diceSocket) {
        console.error('❌ diceSocket no está definido');
        alert('Error: No hay conexión con el servidor. Por favor, recarga la página.');
        return;
    }
    
    if (diceSocket.readyState !== WebSocket.OPEN) {
        console.error('❌ WebSocket no está conectado. Estado:', diceSocket.readyState);
        alert('Error: No hay conexión con el servidor. Por favor, recarga la página.');
        return;
    }
    
    console.log('✅ Enviando mensaje roll_dice al servidor');
    rollBtn.disabled = true;
    
    // Enviar lanzamiento al servidor vía WebSocket
    diceSocket.send(JSON.stringify({
        type: 'roll_dice'
    }));
    
    console.log('✅ Mensaje enviado, iniciando animación');
    // Mostrar animación de lanzamiento
    animateDiceRoll();
}

function animateDiceRoll() {
    // Mostrar contenedor de dados animados
    const diceContainer = document.getElementById('dice-container');
    if (diceContainer) {
        diceContainer.classList.add('show');
        
        // Animar los dados con valores aleatorios mientras giran
        const die1 = document.getElementById('die-1');
        const die2 = document.getElementById('die-2');
        
        if (die1 && die2) {
            // Valores de dados para mostrar durante la animación
            const diceFaces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
            
            // Cambiar valores aleatorios mientras giran (efecto visual)
            const rollInterval = setInterval(() => {
                if (die1 && die2) {
                    die1.textContent = diceFaces[Math.floor(Math.random() * 6)];
                    die2.textContent = diceFaces[Math.floor(Math.random() * 6)];
                }
            }, 100);
            
            // Ocultar después de 1.5 segundos (tiempo suficiente para la animación)
            setTimeout(() => {
                if (diceContainer) {
                    diceContainer.classList.remove('show');
                }
                if (rollInterval) {
                    clearInterval(rollInterval);
                }
                // Resetear a "?" para la próxima vez
                if (die1) die1.textContent = '?';
                if (die2) die2.textContent = '?';
            }, 1500);
        }
    }
    
    // También mantener la animación en los cuadros de resultados
    const diceElements = document.querySelectorAll('.player-dice .dice-value');
    diceElements.forEach(dice => {
        dice.style.animation = 'diceRoll 0.5s ease-in-out';
    });
    
    setTimeout(() => {
        diceElements.forEach(dice => {
            dice.style.animation = '';
        });
    }, 500);
}

// CSS para animación de dados
const diceStyle = document.createElement('style');
diceStyle.textContent = `
    @keyframes diceRoll {
        0%, 100% {
            transform: rotate(0deg);
        }
        25% {
            transform: rotate(90deg);
        }
        50% {
            transform: rotate(180deg);
        }
        75% {
            transform: rotate(270deg);
        }
    }
`;
document.head.appendChild(diceStyle);

