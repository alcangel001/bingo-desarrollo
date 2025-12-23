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
    const rollBtn = document.getElementById('roll-dice-btn');
    
    // Verificar que el botón no esté deshabilitado
    if (rollBtn.disabled) {
        console.log('El botón está deshabilitado. El juego aún no ha comenzado.');
        return;
    }
    
    // Verificar conexión WebSocket
    if (!diceSocket || diceSocket.readyState !== WebSocket.OPEN) {
        console.error('WebSocket no está conectado');
        alert('Error: No hay conexión con el servidor. Por favor, recarga la página.');
        return;
    }
    
    rollBtn.disabled = true;
    
    // Enviar lanzamiento al servidor vía WebSocket
    diceSocket.send(JSON.stringify({
        type: 'roll_dice'
    }));
    
    // Mostrar animación de lanzamiento
    animateDiceRoll();
}

function animateDiceRoll() {
    // Animación visual de dados girando
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

