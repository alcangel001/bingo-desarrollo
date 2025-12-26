// WebSocket para partidas de dados en tiempo real

let diceSocket = null;

// Objetos de audio globales para los sonidos de dados
const rollSound = new Audio('https://assets.mixkit.co/active_storage/sfx/2004/2004-preview.mp3');
const hitSound = new Audio('https://assets.mixkit.co/active_storage/sfx/1017/1017-preview.mp3');

// Configurar volúmenes
rollSound.volume = 0.5;
hitSound.volume = 0.6;

// Precargar los sonidos
rollSound.preload = 'auto';
hitSound.preload = 'auto';

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
            // Premio determinado - mostrar animación de ruleta
            // Si viene started_at, usarlo para sincronización
            const startedAt = data.started_at || null;
            showPrizeSpinAnimation(data.multiplier, data.final_prize, startedAt);
            break;
            
        case 'round_result':
            // Resultado de ronda - TODOS los jugadores han lanzado
            console.log('📊 Resultado de ronda completo recibido:', data);
            
            // Verificar si hubo empate
            if (data.is_tie) {
                console.log(`🤝 Empate detectado! Total: ${data.tie_total}`);
                const gameStatusEl = document.getElementById('game-status');
                if (gameStatusEl) {
                    gameStatusEl.textContent = `🤝 Empate con total ${data.tie_total}! Todos vuelven a lanzar.`;
                    gameStatusEl.style.color = '#ffd700';
                }
                
                // Mostrar mensaje de empate
                alert(`🤝 ¡Empate! Todos los jugadores sacaron ${data.tie_total}. Nadie pierde vida. Vuelvan a lanzar.`);
            }
            
            updateRoundResults(data.results, data.eliminated);
            
            // Re-habilitar botón después de mostrar resultados (SOLO si el usuario NO está eliminado)
            setTimeout(() => {
                const rollBtn = document.getElementById('roll-dice-btn');
                if (rollBtn) {
                    // Verificar si el usuario actual está eliminado
                    const currentUserId = typeof USER_ID !== 'undefined' ? USER_ID : null;
                    let isCurrentUserEliminated = false;
                    
                    if (currentUserId && window.currentGameState && window.currentGameState.players) {
                        const currentPlayer = window.currentGameState.players.find(p => p.user_id === currentUserId);
                        if (currentPlayer && currentPlayer.is_eliminated) {
                            isCurrentUserEliminated = true;
                        }
                    }
                    
                    // También verificar si el usuario eliminado coincide con el usuario actual
                    if (data.eliminated && currentUserId) {
                        // El backend puede enviar el username o el user_id como eliminado
                        if (data.eliminated === currentUserId || 
                            String(data.eliminated) === String(currentUserId)) {
                            isCurrentUserEliminated = true;
                        }
                    }
                    
                    // Verificar que el juego aún esté en curso antes de re-habilitar
                    const gameStatusEl = document.getElementById('game-status');
                    if (!isCurrentUserEliminated) {
                        if (gameStatusEl && gameStatusEl.textContent.includes('En juego')) {
                            rollBtn.disabled = false;
                            console.log('✅ Botón re-habilitado para siguiente ronda');
                        } else if (data.is_tie) {
                            // Si hubo empate, re-habilitar para que vuelvan a lanzar
                            rollBtn.disabled = false;
                            if (gameStatusEl) {
                                gameStatusEl.textContent = 'En juego - ¡Lanza los dados!';
                                gameStatusEl.style.color = '';
                            }
                        }
                    } else {
                        // Usuario eliminado - mantener botón deshabilitado
                        rollBtn.disabled = true;
                        console.log('❌ Botón deshabilitado: usuario eliminado');
                        if (gameStatusEl) {
                            gameStatusEl.textContent = 'Eliminado - Esperando fin del juego';
                            gameStatusEl.style.color = '#ff4444';
                        }
                    }
                }
            }, data.is_tie ? 3000 : 2000); // Más tiempo si hubo empate
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

// Variables globales para la animación de ruleta
let slotAnimationInProgress = false;
let slotStartTime = null;
let slotTargetMultiplier = null;

function showPrizeSpinAnimation(multiplier, finalPrize, startedAt = null) {
    console.log('🎰 Iniciando animación del premio:', multiplier, finalPrize);
    
    // Si ya hay una animación en progreso, no iniciar otra
    if (slotAnimationInProgress) {
        console.log('⚠️ Animación de ruleta ya en progreso, saltando...');
        return;
    }
    
    slotAnimationInProgress = true;
    slotTargetMultiplier = multiplier;
    
    const slotModal = document.getElementById('multiplier-slot-modal');
    const slotReel = document.getElementById('slot-reel');
    const slotResult = document.getElementById('slot-result');
    const slotResultMultiplier = document.getElementById('slot-result-multiplier');
    const slotResultPrize = document.getElementById('slot-result-prize');
    const rollBtn = document.getElementById('roll-dice-btn');
    
    if (!slotModal || !slotReel) {
        console.error('❌ Elementos del modal de ruleta no encontrados');
        slotAnimationInProgress = false;
        return;
    }
    
    // Asegurar que el botón esté deshabilitado durante la animación
    if (rollBtn) rollBtn.disabled = true;
    
    // Mostrar modal
    slotModal.style.display = 'flex';
    slotResult.style.display = 'none';
    
    // Calcular tiempo transcurrido si se proporciona startedAt
    let elapsedSeconds = 0;
    if (startedAt) {
        const startedTime = new Date(startedAt).getTime();
        elapsedSeconds = (Date.now() - startedTime) / 1000;
        console.log(`⏱️ Tiempo transcurrido desde started_at: ${elapsedSeconds.toFixed(2)}s`);
    }
    
    // Duración total de la animación: 7 segundos
    const totalDuration = 7000; // 7 segundos
    const remainingTime = Math.max(0, totalDuration - (elapsedSeconds * 1000));
    
    // Si ya pasaron más de 7 segundos, mostrar resultado inmediatamente
    if (remainingTime <= 0) {
        showSlotResult(multiplier, finalPrize);
        slotAnimationInProgress = false;
        return;
    }
    
    // Mapeo de multiplicadores a posiciones en el carrete
    const multiplierOrder = ['2x', '3x', '5x', '10x', '25x', '100x', '500x', '1000x'];
    const targetIndex = multiplierOrder.indexOf(multiplier);
    const itemHeight = 200; // Altura de cada item
    
    // Calcular posición inicial basada en tiempo transcurrido
    let startPosition = 0;
    if (elapsedSeconds > 0 && elapsedSeconds < 7) {
        // Si ya pasaron algunos segundos, empezar desde una posición intermedia
        const progress = elapsedSeconds / 7;
        const initialSpins = progress * 20; // 20 vueltas completas en 7 segundos
        startPosition = -(initialSpins * multiplierOrder.length * itemHeight);
    }
    
    // Posición final: el multiplicador objetivo debe estar en el centro
    const finalPosition = -(targetIndex * itemHeight);
    
    // Aplicar posición inicial
    slotReel.style.transform = `translateY(${startPosition}px)`;
    
    // Reproducir sonido de tick
    let tickSoundInterval = null;
    const playTickSound = () => {
        // Crear sonido de tick simple usando Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.1);
        } catch (e) {
            console.log('⚠️ No se pudo reproducir sonido de tick:', e);
        }
    };
    
    // Iniciar sonido de tick cada vez que un número pase
    let lastItemIndex = Math.floor(Math.abs(startPosition) / itemHeight) % multiplierOrder.length;
    tickSoundInterval = setInterval(() => {
        const currentPosition = parseFloat(slotReel.style.transform.match(/-?\d+\.?\d*/)?.[0] || 0);
        const currentItemIndex = Math.floor(Math.abs(currentPosition) / itemHeight) % multiplierOrder.length;
        
        if (currentItemIndex !== lastItemIndex) {
            playTickSound();
            lastItemIndex = currentItemIndex;
        }
    }, 50);
    
    // Animar hacia la posición final
    setTimeout(() => {
        slotReel.style.transition = `transform ${remainingTime}ms cubic-bezier(0.25, 0.46, 0.45, 0.94)`;
        slotReel.style.transform = `translateY(${finalPosition}px)`;
        
        // Detener sonido de tick cuando termine la animación
        setTimeout(() => {
            if (tickSoundInterval) {
                clearInterval(tickSoundInterval);
            }
            showSlotResult(multiplier, finalPrize);
            slotAnimationInProgress = false;
        }, remainingTime);
    }, 50);
}

function showSlotResult(multiplier, finalPrize) {
    const slotModal = document.getElementById('multiplier-slot-modal');
    const slotResult = document.getElementById('slot-result');
    const slotResultMultiplier = document.getElementById('slot-result-multiplier');
    const slotResultPrize = document.getElementById('slot-result-prize');
    const prizeDisplay = document.getElementById('prize-display');
    const prizeAmount = document.getElementById('prize-amount');
    const prizeMultiplier = document.getElementById('prize-multiplier');
    
    // Mostrar resultado en el modal
    if (slotResult && slotResultMultiplier && slotResultPrize) {
        slotResultMultiplier.textContent = multiplier;
        slotResultPrize.textContent = `Premio: $${parseFloat(finalPrize).toLocaleString()}`;
        slotResult.style.display = 'block';
    }
    
    // Aplicar colores del multiplicador
    if (typeof applyPrizeColors === 'function') {
        applyPrizeColors(multiplier);
    }
    
    // Actualizar premio en la mesa
    if (prizeAmount) prizeAmount.textContent = `$${parseFloat(finalPrize).toLocaleString()}`;
    if (prizeMultiplier) prizeMultiplier.textContent = multiplier;
    
    // Ocultar modal después de 2 segundos
    setTimeout(() => {
        if (slotModal) {
            slotModal.style.display = 'none';
        }
        if (prizeDisplay) {
            prizeDisplay.style.display = 'block';
        }
        
        const gameStatusEl = document.getElementById('game-status');
        if (gameStatusEl) {
            gameStatusEl.textContent = '¡Premio determinado! Esperando inicio del juego...';
        }
    }, 2000);
}

/**
 * Calcula la rotación 3D para mostrar un número específico en el dado
 * @param {number} number - Número del dado (1-6)
 * @returns {object} Objeto con rotateX y rotateY en grados
 */
function getRotation(number) {
    // Rotaciones para cada cara del dado
    // Cada número necesita una combinación única de rotateX y rotateY
    const rotations = {
        1: { rotateX: 0, rotateY: 0 },        // Cara frontal
        2: { rotateX: 0, rotateY: -90 },     // Cara derecha
        3: { rotateX: 0, rotateY: 180 },    // Cara trasera
        4: { rotateX: 0, rotateY: 90 },      // Cara izquierda
        5: { rotateX: -90, rotateY: 0 },    // Cara superior
        6: { rotateX: 90, rotateY: 0 }      // Cara inferior
    };
    
    return rotations[number] || rotations[1];
}

/**
 * Reproduce sonido de dados
 * Sincronizado con la animación de los cubos 3D
 */
function playDiceSound() {
    try {
        // Detener y reiniciar sonidos si hay lanzamientos muy seguidos
        rollSound.pause();
        rollSound.currentTime = 0;
        hitSound.pause();
        hitSound.currentTime = 0;
        
        // Reproducir sonido de giro cuando el cubo empieza a girar
        rollSound.play().catch(e => {
            console.log('⚠️ Audio bloqueado o error al reproducir sonido de giro:', e);
        });
        
        // Sonido de impacto cuando el dado se detiene (1200ms para sincronizar con el final de la animación)
        setTimeout(() => {
            hitSound.play().catch(e => {
                console.log('⚠️ Audio bloqueado o error al reproducir sonido de impacto:', e);
            });
        }, 1200);
    } catch (e) {
        console.log('⚠️ Error al reproducir sonido:', e);
    }
}

function updateDiceRoll(data) {
    console.log('🎲 Actualizando lanzamiento de dados:', data);
    
    // Encontrar el asiento del jugador que lanzó usando el mismo método que updateRoundResults
    let seatNum = null;
    
    // Usar window.currentGameState si está disponible, sino INITIAL_PLAYERS
    const players = (window.currentGameState && window.currentGameState.players) 
        ? window.currentGameState.players 
        : (typeof INITIAL_PLAYERS !== 'undefined' ? INITIAL_PLAYERS : []);
    
    // Crear mapa de user_id -> seatNum (igual que en updateRoundResults)
    const playerIdToSeatMap = {};
    players.forEach((player, index) => {
        if (player && player.user_id) {
            playerIdToSeatMap[String(player.user_id)] = index + 1;
        }
    });
    
    // También buscar por data-player-id en los elementos del DOM
    for (let seat = 1; seat <= 3; seat++) {
        const seatElement = document.getElementById(`player-${seat}`);
        if (seatElement) {
            const playerIdAttr = seatElement.getAttribute('data-player-id');
            if (playerIdAttr) {
                playerIdToSeatMap[String(playerIdAttr)] = seat;
            }
        }
    }
    
    // Buscar el asiento del jugador que lanzó
    seatNum = playerIdToSeatMap[String(data.user_id)];
    
    // Si aún no encontramos, buscar por nombre como fallback
    if (!seatNum) {
        for (let i = 1; i <= 3; i++) {
            const nameEl = document.getElementById(`name-${i}`);
            if (nameEl && nameEl.textContent === data.username) {
                seatNum = i;
                break;
            }
        }
    }
    
    if (seatNum) {
        console.log(`🎲 Animando dados 3D para jugador en asiento ${seatNum} (${data.username})`);
        
        // Animar los cubos 3D
        const cube1 = document.getElementById(`cube-${seatNum}-1`);
        const cube2 = document.getElementById(`cube-${seatNum}-2`);
        const dice3dContainer = document.getElementById(`dice-3d-${seatNum}`);
        
        if (cube1 && cube2 && dice3dContainer) {
            // Reproducir sonido de giro cuando el cubo empieza a girar
            playDiceSound();
            
            // Mostrar contenedor de dados 3D
            dice3dContainer.style.display = 'flex';
            
            // Resetear transformaciones previas
            cube1.style.transform = '';
            cube2.style.transform = '';
            
            // Agregar clase de animación de vuelo
            cube1.classList.add('rolling');
            cube2.classList.add('rolling');
            
            // Calcular rotaciones finales para cada dado
            const rotation1 = getRotation(data.die1);
            const rotation2 = getRotation(data.die2);
            
            console.log(`🎲 Rotaciones finales: Dado 1 (${data.die1}) = X:${rotation1.rotateX}° Y:${rotation1.rotateY}°, Dado 2 (${data.die2}) = X:${rotation2.rotateX}° Y:${rotation2.rotateY}°`);
            
            // Después de 1.5 segundos, aplicar rotación final
            setTimeout(() => {
                // Remover clase de animación
                cube1.classList.remove('rolling');
                cube2.classList.remove('rolling');
                
                // Aplicar rotación final para mostrar el número correcto
                cube1.style.transform = `rotateX(${rotation1.rotateX}deg) rotateY(${rotation1.rotateY}deg)`;
                cube2.style.transform = `rotateX(${rotation2.rotateX}deg) rotateY(${rotation2.rotateY}deg)`;
                
                console.log(`✅ Dados 3D animados y rotados para mostrar ${data.die1} y ${data.die2}`);
                
                // Actualizar el valor numérico también (por compatibilidad)
                const diceElement = document.getElementById(`dice-${seatNum}`);
                if (diceElement) {
                    const diceValue = diceElement.querySelector('.dice-value');
                    if (diceValue) {
                        diceValue.textContent = data.total;
                    }
                }
            }, 1500);
        } else {
            console.warn(`⚠️ No se encontraron cubos 3D para asiento ${seatNum}, usando fallback`);
            // Fallback: si no hay cubos 3D, usar el método anterior
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
        }
    } else {
        console.warn(`⚠️ No se pudo encontrar el asiento para el jugador ${data.username} (ID: ${data.user_id})`);
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
            
            // Actualizar el estado del jugador en window.currentGameState
            if (window.currentGameState && window.currentGameState.players) {
                const eliminatedPlayer = window.currentGameState.players.find(p => 
                    p.user_id === parseInt(eliminated) || 
                    p.username === eliminated ||
                    String(p.user_id) === String(eliminated)
                );
                if (eliminatedPlayer) {
                    eliminatedPlayer.is_eliminated = true;
                    console.log(`✅ Estado actualizado: jugador ${eliminatedPlayer.username} marcado como eliminado`);
                }
            }
            
            // Si el usuario eliminado es el usuario actual, deshabilitar el botón inmediatamente
            const currentUserId = typeof USER_ID !== 'undefined' ? USER_ID : null;
            if (currentUserId && (
                eliminated === currentUserId || 
                String(eliminated) === String(currentUserId) ||
                players.find(p => (p.user_id === parseInt(eliminated) || p.username === eliminated) && p.user_id === currentUserId)
            )) {
                const rollBtn = document.getElementById('roll-dice-btn');
                if (rollBtn) {
                    rollBtn.disabled = true;
                    console.log('❌ Botón deshabilitado: usuario actual eliminado');
                }
                const gameStatusEl = document.getElementById('game-status');
                if (gameStatusEl) {
                    gameStatusEl.textContent = 'Eliminado - Esperando fin del juego';
                    gameStatusEl.style.color = '#ff4444';
                }
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
        
        // Si ya hay multiplicador, mostrar animación de ruleta con sincronización
        if (data.multiplier && data.final_prize) {
            // Obtener started_at del juego si está disponible
            const startedAt = data.started_at || null;
            showPrizeSpinAnimation(data.multiplier, data.final_prize, startedAt);
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

