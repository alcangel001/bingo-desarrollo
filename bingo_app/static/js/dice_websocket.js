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
            // Resultado de ronda - TODOS los jugadores han lanzado
            console.log('📊 Resultado de ronda completo recibido:', data);
            updateRoundResults(data.results, data.eliminated);
            // NO deshabilitar el botón aquí - ya está deshabilitado desde rollDice()
            // Solo asegurar que esté deshabilitado y re-habilitarlo después de mostrar resultados (2 segundos)
            // para la siguiente ronda
            setTimeout(() => {
                const rollBtn = document.getElementById('roll-dice-btn');
                if (rollBtn) {
                    // Verificar que el juego aún esté en curso antes de re-habilitar
                    const gameStatusEl = document.getElementById('game-status');
                    if (gameStatusEl && gameStatusEl.textContent.includes('En juego')) {
                        rollBtn.disabled = false;
                        console.log('✅ Botón re-habilitado para siguiente ronda');
                    }
                }
            }, 2000);
            break;
            
        case 'game_finished':
            // Juego terminado
            console.log('🏆 Juego terminado:', data);
            if (data.winner && data.prize) {
                showWinnerAnimation(data.winner, data.prize, data.multiplier || 'N/A');
            } else {
                console.error('⚠️ Datos incompletos en game_finished:', data);
            }
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
            console.log('📢 Cambio de estado recibido:', data.status);
            handleGameStatusChange(data);
            break;
            
        case 'dice_rolled':
            // Dados lanzados - actualizar UI
            updateDiceRoll(data);
            break;
            
        case 'error':
            // Error del servidor
            console.error('Error del servidor:', data.message);
            alert(data.message || 'Ha ocurrido un error');
            // Re-habilitar botón si fue un error
            const rollBtn = document.getElementById('roll-dice-btn');
            if (rollBtn) {
                rollBtn.disabled = false;
            }
            break;
    }
}

function showPrizeSpinAnimation(multiplier, finalPrize) {
    console.log('🎰 Iniciando animación del premio:', multiplier, finalPrize);
    const spinAnimation = document.getElementById('spin-animation');
    const prizeDisplay = document.getElementById('prize-display');
    const rollBtn = document.getElementById('roll-dice-btn');
    
    // Asegurar que el botón esté deshabilitado durante la animación
    if (rollBtn) rollBtn.disabled = true;
    
    // Mostrar animación de spin
    if (spinAnimation) spinAnimation.style.display = 'flex';
    if (prizeDisplay) prizeDisplay.style.display = 'none';
    
    // Simular spin (1-2 segundos)
    let spinCount = 0;
    const spinInterval = setInterval(() => {
        spinCount++;
        
        if (spinCount > 40) { // ~2 segundos a 50ms
            clearInterval(spinInterval);
            
            // Aplicar colores del multiplicador real
            if (typeof applyPrizeColors === 'function') {
                applyPrizeColors(multiplier);
            }
            
            // Mostrar premio final
            if (spinAnimation) spinAnimation.style.display = 'none';
            if (prizeDisplay) prizeDisplay.style.display = 'block';
            
            const prizeAmount = document.getElementById('prize-amount');
            const prizeMultiplier = document.getElementById('prize-multiplier');
            if (prizeAmount) prizeAmount.textContent = `$${parseFloat(finalPrize).toLocaleString()}`;
            if (prizeMultiplier) prizeMultiplier.textContent = multiplier;
            
            // Cambiar estado del juego (pero NO habilitar botón aquí, esperar notificación WebSocket)
            const gameStatusEl = document.getElementById('game-status');
            if (gameStatusEl) {
                gameStatusEl.textContent = '¡Premio determinado! Esperando inicio del juego...';
            }
            
            console.log('🎰 Animación completada, esperando notificación de cambio de estado...');
            
            // Fallback: si no llega la notificación en 10 segundos, habilitar el botón de todas formas
            setTimeout(() => {
                if (rollBtn && rollBtn.disabled) {
                    console.log('⏱️ Timeout: habilitando botón por fallback');
                    rollBtn.disabled = false;
                    if (gameStatusEl) gameStatusEl.textContent = 'En juego - ¡Lanza los dados!';
                }
            }, 10000);
        }
    }, 50);
}

function updateDiceRoll(data) {
    console.log('🎲 Actualizando lanzamiento de dados:', data);
    
    // Encontrar el asiento del jugador que lanzó
    const players = typeof INITIAL_PLAYERS !== 'undefined' ? INITIAL_PLAYERS : [];
    const playerIndex = players.findIndex(p => p.user_id === data.user_id);
    
    if (playerIndex !== -1) {
        const seatNum = playerIndex + 1;
        const diceElement = document.getElementById(`dice-${seatNum}`);
        if (diceElement) {
            const diceValue = diceElement.querySelector('.dice-value');
            if (diceValue) {
                diceValue.textContent = data.total;
                diceValue.style.animation = 'diceRoll 0.5s ease-in-out';
                setTimeout(() => {
                    diceValue.style.animation = '';
                }, 500);
            }
        }
    } else {
        // Si no encontramos al jugador en INITIAL_PLAYERS, buscar por posición
        // Asumir que los jugadores están en orden de asiento
        const allSeats = [1, 2, 3];
        for (let seatNum of allSeats) {
            const nameEl = document.getElementById(`name-${seatNum}`);
            if (nameEl && nameEl.textContent === data.username) {
                const diceElement = document.getElementById(`dice-${seatNum}`);
                if (diceElement) {
                    const diceValue = diceElement.querySelector('.dice-value');
                    if (diceValue) {
                        diceValue.textContent = data.total;
                        diceValue.style.animation = 'diceRoll 0.5s ease-in-out';
                        setTimeout(() => {
                            diceValue.style.animation = '';
                        }, 500);
                    }
                }
                break;
            }
        }
    }
    
    // Re-habilitar botón después de un tiempo (si no fue el usuario actual)
    const currentUserId = typeof USER_ID !== 'undefined' ? USER_ID : null;
    if (data.user_id !== currentUserId) {
        setTimeout(() => {
            const rollBtn = document.getElementById('roll-dice-btn');
            const gameStatusEl = document.getElementById('game-status');
            if (rollBtn && gameStatusEl && gameStatusEl.textContent.includes('En juego')) {
                rollBtn.disabled = false;
            }
        }, 2000);
    } else {
        // Si fue el usuario actual, re-habilitar después de mostrar el resultado
        setTimeout(() => {
            const rollBtn = document.getElementById('roll-dice-btn');
            if (rollBtn) {
                rollBtn.disabled = false;
            }
        }, 1000);
    }
}

function updateRoundResults(results, eliminated) {
    console.log('🔄 Actualizando resultados de ronda:', results);
    console.log('🔄 Jugador eliminado:', eliminated);
    
    // Usar el estado del juego guardado si está disponible, sino usar INITIAL_PLAYERS
    const players = (window.currentGameState && window.currentGameState.players) 
        ? window.currentGameState.players 
        : (typeof INITIAL_PLAYERS !== 'undefined' ? INITIAL_PLAYERS : []);
    console.log('🔄 Jugadores disponibles:', players);
    
    // Asegurar que siempre se muestren los 3 cuadros de resultados
    // Primero, crear un mapa de user_id -> seatNum para acceso rápido
    const playerIdToSeatMap = {};
    players.forEach((player, index) => {
        if (player && player.user_id) {
            playerIdToSeatMap[String(player.user_id)] = index + 1;
        }
    });
    
    // También buscar por data-player-id en los elementos del DOM
    for (let seatNum = 1; seatNum <= 3; seatNum++) {
        const playerSeat = document.getElementById(`player-${seatNum}`);
        if (playerSeat) {
            const playerIdAttr = playerSeat.getAttribute('data-player-id');
            if (playerIdAttr) {
                playerIdToSeatMap[String(playerIdAttr)] = seatNum;
            }
        }
    }
    
    console.log('🔄 Mapa de jugadores a asientos:', playerIdToSeatMap);
    
    // Actualizar todos los asientos (1, 2, 3) con los resultados disponibles
    for (let seatNum = 1; seatNum <= 3; seatNum++) {
        const diceElement = document.getElementById(`dice-${seatNum}`);
        if (diceElement) {
            const diceValue = diceElement.querySelector('.dice-value');
            if (diceValue) {
                // Buscar si hay un resultado para este asiento
                let foundResult = false;
                
                // Buscar en los resultados usando el mapa de user_id -> seatNum
                if (results) {
                    for (const [playerId, resultData] of Object.entries(results)) {
                        const mappedSeat = playerIdToSeatMap[String(playerId)];
                        if (mappedSeat === seatNum) {
                            let total;
                            if (Array.isArray(resultData)) {
                                total = resultData[2]; // El total está en el índice 2
                            } else if (typeof resultData === 'object' && resultData.total) {
                                total = resultData.total;
                            } else {
                                total = resultData; // Asumir que es el total directamente
                            }
                            
                            console.log(`✅ Actualizando dice-${seatNum} (jugador ${playerId}) con total: ${total}`);
                            diceValue.textContent = total;
                            diceValue.style.animation = 'diceRoll 0.5s ease-in-out';
                            setTimeout(() => {
                                diceValue.style.animation = '';
                            }, 500);
                            foundResult = true;
                            break; // Ya encontramos el resultado para este asiento
                        }
                    }
                }
                
                // Si no se encontró resultado, mantener el valor actual o poner '-'
                if (!foundResult && diceValue.textContent === '-') {
                    // Ya está en '-', no hacer nada
                } else if (!foundResult) {
                    // Si había un valor pero no hay resultado nuevo, mantenerlo
                    console.log(`⚠️ No hay resultado nuevo para asiento ${seatNum}, manteniendo valor actual`);
                }
            }
        }
    }
    
    // También actualizar usando el método original para compatibilidad (usando el mapa)
    if (results) {
        Object.keys(results).forEach((playerId) => {
            const playerIdInt = parseInt(playerId);
            console.log(`🔄 Procesando resultado para playerId: ${playerIdInt}`);
            
            // Usar el mapa para encontrar el asiento
            const seatNum = playerIdToSeatMap[String(playerId)];
            console.log(`🔄 Asiento encontrado en mapa: ${seatNum}`);
            
            if (seatNum && seatNum >= 1 && seatNum <= 3) {
                const diceElement = document.getElementById(`dice-${seatNum}`);
                if (diceElement) {
                    const diceValue = diceElement.querySelector('.dice-value');
                    if (diceValue && results[playerId]) {
                        let total;
                        if (Array.isArray(results[playerId])) {
                            total = results[playerId][2];
                        } else if (typeof results[playerId] === 'object' && results[playerId].total) {
                            total = results[playerId].total;
                        } else {
                            total = results[playerId];
                        }
                        
                        console.log(`✅ Actualizando dice-${seatNum} (jugador ${playerId}) con total: ${total} [método compatibilidad]`);
                        diceValue.textContent = total;
                        diceValue.style.animation = 'diceRoll 0.5s ease-in-out';
                        setTimeout(() => {
                            diceValue.style.animation = '';
                        }, 500);
                    }
                }
            } else {
                console.warn(`⚠️ No se encontró asiento para jugador ${playerId} en el mapa`);
            }
        });
    }
    
    // Mostrar jugador eliminado
    if (eliminated) {
        console.log(`🔄 Marcando jugador eliminado: ${eliminated}`);
        // Buscar por user_id o username
        const eliminatedPlayerIndex = players.findIndex(p => 
            p.user_id === parseInt(eliminated) || 
            p.username === eliminated ||
            String(p.user_id) === String(eliminated)
        );
        if (eliminatedPlayerIndex !== -1 && eliminatedPlayerIndex < 3) {
            const seatNum = eliminatedPlayerIndex + 1;
            console.log(`✅ Jugador eliminado encontrado en asiento ${seatNum}`);
            const eliminatedSeat = document.getElementById(`player-${seatNum}`);
            if (eliminatedSeat) {
                eliminatedSeat.classList.add('eliminated');
            }
            const statusEl = document.getElementById(`status-${seatNum}`);
            if (statusEl) {
                statusEl.style.color = '#ff4444';
                statusEl.textContent = '✕';
            }
        } else {
            console.warn(`⚠️ Jugador eliminado ${eliminated} no encontrado`);
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
            // Si no hay avatar, usar un placeholder simple o dejar vacío
            this.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="64" height="64"%3E%3Ccircle cx="32" cy="32" r="30" fill="%239b59b6"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="white" font-size="24" font-weight="bold"%3E?%3C/text%3E%3C/svg%3E';
        };
    }
}

function updateGameState(data) {
    // Guardar el estado del juego para usarlo en updateRoundResults
    window.currentGameState = data;
    
    if (data.players) {
        data.players.forEach((player, index) => {
            const seatNum = index + 1;
            updatePlayerInfo(
                player.user_id,
                player.username,
                player.avatar_url,
                seatNum
            );
            
            // Guardar el user_id en el elemento del asiento para referencia
            const playerSeat = document.getElementById(`player-${seatNum}`);
            if (playerSeat) {
                playerSeat.setAttribute('data-player-id', player.user_id);
            }
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

function handleGameStatusChange(data) {
    console.log('🔄 Manejando cambio de estado:', data);
    const rollBtn = document.getElementById('roll-dice-btn');
    const gameStatusEl = document.getElementById('game-status');
    
    if (data.status === 'PLAYING') {
        console.log('✅ Cambiando a PLAYING - habilitando botón');
        if (rollBtn) {
            rollBtn.disabled = false;
            rollBtn.style.opacity = '1';
            rollBtn.style.cursor = 'pointer';
        }
        if (gameStatusEl) {
            gameStatusEl.textContent = 'En juego - ¡Lanza los dados!';
        }
        
        // Asegurarse de que la animación del spin esté oculta
        const spinAnimation = document.getElementById('spin-animation');
        const prizeDisplay = document.getElementById('prize-display');
        if (spinAnimation) spinAnimation.style.display = 'none';
        if (prizeDisplay) prizeDisplay.style.display = 'block';
        
        // Actualizar premio si viene en el mensaje
        if (data.final_prize && data.multiplier) {
            const prizeAmount = document.getElementById('prize-amount');
            const prizeMultiplier = document.getElementById('prize-multiplier');
            if (prizeAmount) prizeAmount.textContent = `$${parseFloat(data.final_prize).toLocaleString()}`;
            if (prizeMultiplier) prizeMultiplier.textContent = data.multiplier;
            if (typeof applyPrizeColors === 'function') {
                applyPrizeColors(data.multiplier);
            }
        }
    } else if (data.status === 'SPINNING') {
        console.log('⏳ Cambiando a SPINNING - deshabilitando botón');
        if (rollBtn) rollBtn.disabled = true;
        if (gameStatusEl) gameStatusEl.textContent = 'Determinando premio...';
    }
}

function showWinnerAnimation(winner, prize, multiplier) {
    console.log('🎉 Mostrando animación de ganador:', { winner, prize, multiplier });
    
    const gameStatusEl = document.getElementById('game-status');
    const rollBtn = document.getElementById('roll-dice-btn');
    
    if (gameStatusEl) {
        gameStatusEl.textContent = `¡${winner} ganó $${parseFloat(prize).toLocaleString()}!`;
        gameStatusEl.style.color = '#4CAF50';
        gameStatusEl.style.fontSize = '1.5em';
        gameStatusEl.style.fontWeight = 'bold';
    }
    
    if (rollBtn) {
        rollBtn.disabled = true;
        rollBtn.style.opacity = '0.5';
        rollBtn.style.cursor = 'not-allowed';
    }
    
    // Mostrar animación de ganador
    const prizeFormatted = parseFloat(prize).toLocaleString('es-ES', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    alert(`¡${winner} ganó $${prizeFormatted} con multiplicador ${multiplier}!`);
    
    // Redirigir después de 5 segundos
    setTimeout(() => {
        console.log('🔄 Redirigiendo al lobby...');
        window.location.href = '/dice/';
    }, 5000);
}

// Conectar cuando se carga la página
if (typeof ROOM_CODE !== 'undefined') {
    connectDiceWebSocket(ROOM_CODE);
}

