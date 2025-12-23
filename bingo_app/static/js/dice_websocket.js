// WebSocket para partidas de dados en tiempo real

let diceSocket = null;

function connectDiceWebSocket(roomCode) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/dice/game/${roomCode}/`;
    
    console.log('🔄 Intentando conectar WebSocket a:', wsUrl);
    
    diceSocket = new WebSocket(wsUrl);
    
    diceSocket.onopen = function(e) {
        console.log('✅ Conectado a partida de dados');
    };
    
    diceSocket.onmessage = function(e) {
        try {
            const data = JSON.parse(e.data);
            console.log('📨 Mensaje recibido:', data.type);
            
            // Manejar errores del servidor
            if (data.type === 'error') {
                console.error('❌ Error del servidor:', data.message);
                alert(data.message || 'Error de conexión');
                return;
            }
            
            handleDiceMessage(data);
        } catch (error) {
            console.error('❌ Error al parsear mensaje:', error);
        }
    };
    
    diceSocket.onerror = function(error) {
        console.error('❌ Error en WebSocket:', error);
        console.error('Estado WebSocket:', diceSocket.readyState);
    };
    
    diceSocket.onclose = function(e) {
        console.log('🔌 Desconectado de partida de dados. Código:', e.code, 'Razón:', e.reason);
        
        // No reconectar si fue un cierre intencional (código 1000) o error de autenticación
        if (e.code !== 1000 && e.code !== 1008) {
            // Intentar reconectar después de 3 segundos solo si no fue un cierre intencional
            setTimeout(() => {
                if (roomCode && (!diceSocket || diceSocket.readyState === WebSocket.CLOSED)) {
                    console.log('🔄 Intentando reconectar...');
                    connectDiceWebSocket(roomCode);
                }
            }, 3000);
        }
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
            
        case 'game_status_changed':
            // Estado del juego cambió (SPINNING -> PLAYING)
            handleGameStatusChange(data);
            break;
            
        case 'dice_rolled':
            // Dados lanzados - actualizar UI
            updateDiceRoll(data);
            break;
            
        case 'error':
            // Error del servidor
            console.error('Error del servidor:', data.message);
            // Re-habilitar botón si fue un error
            const rollBtn = document.getElementById('roll-dice-btn');
            if (rollBtn) {
                rollBtn.disabled = false;
            }
            break;
    }
}

function showPrizeSpinAnimation(multiplier, finalPrize) {
    const spinAnimation = document.getElementById('spin-animation');
    const prizeDisplay = document.getElementById('prize-display');
    
    // Mostrar animación de spin
    spinAnimation.style.display = 'flex';
    prizeDisplay.style.display = 'none';
    
    // Simular spin (1-2 segundos)
    let spinCount = 0;
    const spinInterval = setInterval(() => {
        spinCount++;
        
        if (spinCount > 40) { // ~2 segundos a 50ms
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
            
            // Después de 2 segundos, comenzar el juego y habilitar botón
            setTimeout(() => {
                document.getElementById('game-status').textContent = 'En juego - ¡Lanza los dados!';
                const rollBtn = document.getElementById('roll-dice-btn');
                if (rollBtn) {
                    rollBtn.disabled = false;
                }
            }, 2000);
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
    
    // Habilitar botón según el estado del juego
    const rollBtn = document.getElementById('roll-dice-btn');
    const gameStatusEl = document.getElementById('game-status');
    
    if (data.status === 'PLAYING') {
        if (rollBtn) rollBtn.disabled = false;
        if (gameStatusEl) gameStatusEl.textContent = 'En juego - ¡Lanza los dados!';
    } else if (data.status === 'SPINNING') {
        if (rollBtn) rollBtn.disabled = true;
        if (gameStatusEl) gameStatusEl.textContent = 'Determinando premio...';
        
        // Si ya hay multiplicador, mostrar animación de spin
        if (data.multiplier && data.final_prize) {
            showPrizeSpinAnimation(data.multiplier, data.final_prize);
        }
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

