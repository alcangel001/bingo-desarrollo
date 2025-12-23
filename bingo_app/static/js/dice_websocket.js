// WebSocket para partidas de dados en tiempo real

let diceSocket = null;

function connectDiceWebSocket(roomCode) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/dice/game/${roomCode}/`;
    
    diceSocket = new WebSocket(wsUrl);
    
    diceSocket.onopen = function(e) {
        console.log('✅ Conectado a partida de dados');
    };
    
    diceSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        handleDiceMessage(data);
    };
    
    diceSocket.onerror = function(error) {
        console.error('❌ Error en WebSocket:', error);
    };
    
    diceSocket.onclose = function(e) {
        console.log('🔌 Desconectado de partida de dados');
        // Intentar reconectar después de 3 segundos
        setTimeout(() => {
            if (roomCode) {
                connectDiceWebSocket(roomCode);
            }
        }, 3000);
    };
}

function handleDiceMessage(data) {
    switch(data.type) {
        case 'prize_spun':
            // Premio determinado - aplicar colores
            applyPrizeColors(data.multiplier);
            showPrizeSpinAnimation(data.multiplier, data.final_prize);
            break;
            
        case 'round_result':
            // Resultado de ronda
            updateRoundResults(data.results, data.eliminated);
            break;
            
        case 'game_finished':
            // Juego terminado
            showWinnerAnimation(data.winner, data.prize, data.multiplier);
            break;
            
        case 'player_joined':
            // Jugador se unió
            updatePlayerInfo(data.player_id, data.username, data.avatar_url, data.seat_position);
            break;
            
        case 'game_state':
            // Estado actual del juego
            updateGameState(data);
            break;
    }
}

function showPrizeSpinAnimation(multiplier, finalPrize) {
    const spinAnimation = document.getElementById('spin-animation');
    const prizeDisplay = document.getElementById('prize-display');
    
    // Mostrar animación de spin
    spinAnimation.style.display = 'flex';
    prizeDisplay.style.display = 'none';
    
    // Simular spin (1 segundo)
    let currentMultiplier = 2;
    const spinInterval = setInterval(() => {
        const randomMultipliers = ['2x', '3x', '5x', '10x', '25x', '100x', '500x', '1000x'];
        const random = randomMultipliers[Math.floor(Math.random() * randomMultipliers.length)];
        currentMultiplier++;
        
        if (currentMultiplier > 20) {
            clearInterval(spinInterval);
            
            // Aplicar colores del multiplicador real
            applyPrizeColors(multiplier);
            
            // Mostrar premio final
            spinAnimation.style.display = 'none';
            prizeDisplay.style.display = 'block';
            document.getElementById('prize-amount').textContent = `$${parseFloat(finalPrize).toLocaleString()}`;
            document.getElementById('prize-multiplier').textContent = multiplier;
            
            // Cambiar estado del juego
            document.getElementById('game-status').textContent = '¡Premio determinado! Preparando partida...';
            
            // Después de 3 segundos, comenzar el juego
            setTimeout(() => {
                document.getElementById('game-status').textContent = 'En juego...';
                document.getElementById('roll-dice-btn').disabled = false;
            }, 3000);
        }
    }, 50);
}

function updateRoundResults(results, eliminated) {
    // Actualizar resultados de cada jugador
    Object.keys(results).forEach((playerId, index) => {
        const seatNum = index + 1;
        const diceElement = document.getElementById(`dice-${seatNum}`);
        if (diceElement) {
            const diceValue = diceElement.querySelector('.dice-value');
            diceValue.textContent = results[playerId].total;
        }
    });
    
    // Mostrar jugador eliminado
    if (eliminated) {
        const eliminatedSeat = document.querySelector(`[data-player-id="${eliminated}"]`);
        if (eliminatedSeat) {
            eliminatedSeat.classList.add('eliminated');
        }
    }
}

function updatePlayerInfo(playerId, username, avatarUrl, seatPosition) {
    const nameElement = document.getElementById(`name-${seatPosition}`);
    const avatarElement = document.getElementById(`avatar-${seatPosition}`);
    
    if (nameElement) nameElement.textContent = username;
    if (avatarElement) {
        avatarElement.src = avatarUrl;
        avatarElement.onerror = function() {
            this.src = '/static/avatars/default/male.png';
        };
    }
}

function updateGameState(data) {
    if (data.players) {
        data.players.forEach((player, index) => {
            const seatNum = index + 1;
            updatePlayerInfo(
                player.user_id,
                player.username,
                player.avatar_url,
                seatNum
            );
        });
    }
    
    if (data.multiplier) {
        applyPrizeColors(data.multiplier);
    }
}

function showWinnerAnimation(winner, prize, multiplier) {
    document.getElementById('game-status').textContent = `¡${winner} ganó $${prize}!`;
    document.getElementById('roll-dice-btn').disabled = true;
    
    // Mostrar animación de ganador
    alert(`¡${winner} ganó $${prize} con multiplicador ${multiplier}!`);
    
    // Redirigir después de 5 segundos
    setTimeout(() => {
        window.location.href = '/dice/';
    }, 5000);
}

// Conectar cuando se carga la página
if (typeof ROOM_CODE !== 'undefined') {
    connectDiceWebSocket(ROOM_CODE);
}

