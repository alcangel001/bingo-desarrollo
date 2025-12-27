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
    // Audio Resumer: Activar contexto de audio cuando el jugador hace clic
    if (window.AudioContext || window.webkitAudioContext) {
        const context = new (window.AudioContext || window.webkitAudioContext)();
        if (context.state === 'suspended') {
            context.resume();
        }
    }
    
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
    // La animación de dados 3D se maneja en updateDiceRoll cuando llega el mensaje del servidor
    // Esta función solo se llama cuando el usuario presiona el botón, pero la animación real
    // se dispara cuando llega el mensaje dice_rolled del WebSocket
    console.log('🎲 Animación de dados iniciada (esperando resultado del servidor)');
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

