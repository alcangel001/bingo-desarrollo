// WebSocket para partidas de datos en tiempo real

// Constante global para vidas iniciales
const INITIAL_LIVES = 3;

let diceSocket = null;

// Cola de mensajes para procesar secuencialmente
let messageQueue = [];
let isProcessingMessage = false;

// Objetos de audio globales para los sonidos de dados
// Sonidos realistas de dados usando Web Audio API para generar sonidos de dados rodando y golpeando
let rollSound = null;
let hitSound = null;

// Función para crear sonido de dados rodando usando Web Audio API
function createDiceRollSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const duration = 1.2; // Duración del sonido de rodar
        const sampleRate = audioContext.sampleRate;
        const buffer = audioContext.createBuffer(1, sampleRate * duration, sampleRate);
        const data = buffer.getChannelData(0);
        
        // Generar sonido más realista de dados rodando
        // Combinación de ruido filtrado y múltiples frecuencias para simular el choque de dados
        for (let i = 0; i < buffer.length; i++) {
            const t = i / sampleRate;
            // Ruido blanco filtrado (simula el sonido de dados chocando)
            const noise = (Math.random() * 2 - 1) * 0.25;
            // Múltiples modulaciones para simular múltiples dados
            const mod1 = Math.sin(t * 120) * 0.08; // Modulación rápida
            const mod2 = Math.sin(t * 80) * 0.06;  // Modulación media
            const mod3 = Math.sin(t * 200) * 0.05; // Modulación muy rápida
            // Envelope con decay exponencial
            const envelope = Math.max(0, Math.exp(-t * 2));
            data[i] = (noise + mod1 + mod2 + mod3) * envelope;
        }
        
        const source = audioContext.createBufferSource();
        source.buffer = buffer;
        const gainNode = audioContext.createGain();
        gainNode.gain.value = 0.35; // Volumen ajustado
        source.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        return { source, gainNode, audioContext };
    } catch (e) {
        console.log('⚠️ Error creando sonido de dados:', e);
        return null;
    }
}

// Función para crear sonido de impacto de dados
function createDiceHitSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const duration = 0.2; // Sonido corto de impacto
        
        // Crear múltiples osciladores para un sonido más rico (simula el golpe de múltiples dados)
        const osc1 = audioContext.createOscillator();
        const osc2 = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        // Frecuencias que simulan el golpe de dados (más agudas)
        osc1.frequency.setValueAtTime(300, audioContext.currentTime);
        osc1.frequency.exponentialRampToValueAtTime(100, audioContext.currentTime + duration);
        osc1.type = 'square';
        
        osc2.frequency.setValueAtTime(400, audioContext.currentTime);
        osc2.frequency.exponentialRampToValueAtTime(150, audioContext.currentTime + duration);
        osc2.type = 'sawtooth';
        
        // Envelope para el impacto (attack rápido, decay exponencial)
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.4, audioContext.currentTime + 0.005);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
        
        osc1.connect(gainNode);
        osc2.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        return { oscillator: osc1, oscillator2: osc2, gainNode, audioContext };
    } catch (e) {
        console.log('⚠️ Error creando sonido de impacto:', e);
        return null;
    }
}

// Los sonidos se generan dinámicamente usando Web Audio API

// Sonidos adicionales para efectos visuales
// Usar URLs de Mixkit que son más confiables
const sndShake = new Audio('https://assets.mixkit.co/active_storage/sfx/2410/2410-preview.mp3'); // Sonido de dados rodando
const sndHit = new Audio('https://assets.mixkit.co/active_storage/sfx/1017/1017-preview.mp3'); // Sonido de impacto
const sndWin = new Audio('https://assets.mixkit.co/active_storage/sfx/2019/2019-preview.mp3'); // Sonido de victoria

// Configurar volúmenes de los sonidos
sndShake.volume = 0.4;
sndHit.volume = 0.6;
sndWin.volume = 0.7;

// Precargar los sonidos
sndShake.preload = 'auto';
sndHit.preload = 'auto';
sndWin.preload = 'auto';

function connectDiceWebSocket(roomCode) {
    // Limpieza de conexiones: Cerrar WebSocket del lobby si existe
    if (window.wsNotificationHandler && window.wsNotificationHandler.socket) {
        try {
            window.wsNotificationHandler.socket.close();
            console.log('🔌 WebSocket del lobby cerrado al conectar al juego de dados');
        } catch (e) {
            console.log('Error al cerrar WebSocket del lobby:', e);
        }
    }
    
    // Añadir esto al principio de connectDiceWebSocket
    // Esto "despierta" los audios en Chrome/Mobile para evitar errores de AudioContext
    document.addEventListener('click', () => {
        // Esto "despierta" los audios en Chrome/Mobile
        [sndShake, sndHit, sndWin].forEach(audio => {
            audio.play().then(() => {
                audio.pause();
                audio.currentTime = 0;
            }).catch(() => {});
        });
    }, { once: true });
    
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
            console.log("DEBUG_DATA:", JSON.stringify(data, null, 2));
            console.log('📨 Mensaje recibido:', data.type);
            
            // Manejar errores del servidor inmediatamente (no en cola)
            if (data.type === 'error') {
                console.error('❌ Error del servidor:', data.message);
                alert(data.message || 'Error de conexión');
                return;
            }
            
            // Añadir mensaje a la cola (especialmente dice_rolled y round_result)
            if (data.type === 'dice_rolled' || data.type === 'round_result') {
                messageQueue.push(data);
                console.log(`📦 Mensaje añadido a la cola (tipo: ${data.type}). Cola: ${messageQueue.length} mensajes`);
                processNextMessage();
            } else {
                // Otros mensajes se procesan inmediatamente
                handleDiceMessage(data);
            }
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

// Función para procesar el siguiente mensaje de la cola
function processNextMessage() {
    // Si ya se está procesando un mensaje o la cola está vacía, no hacer nada
    if (isProcessingMessage || messageQueue.length === 0) {
        return;
    }
    
    isProcessingMessage = true;
    const data = messageQueue.shift();
    console.log(`🔄 Procesando mensaje de la cola (tipo: ${data.type}). Mensajes restantes: ${messageQueue.length}`);
    
    // Procesar el mensaje
    handleDiceMessage(data);
    
    // Si es dice_rolled o round_result, esperar a que termine la animación antes de procesar el siguiente
    if (data.type === 'dice_rolled') {
        // La animación de dados dura 1.5 segundos
        setTimeout(() => {
            isProcessingMessage = false;
            processNextMessage(); // Procesar siguiente mensaje
        }, 1500);
    } else if (data.type === 'round_result') {
        // Esperar a que termine la animación de barras de vida (0.8s) + tiempo adicional
        setTimeout(() => {
            isProcessingMessage = false;
            processNextMessage(); // Procesar siguiente mensaje
        }, 2000); // 2 segundos para que se vea el resultado completo
    } else {
        // Otros mensajes se procesan inmediatamente
        isProcessingMessage = false;
        processNextMessage();
    }
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
            
            // Actualizar número de ronda
            const roundNumberEl = document.getElementById('round-number');
            if (roundNumberEl && data.round_number !== undefined) {
                roundNumberEl.textContent = data.round_number;
                console.log(`🔄 Ronda actualizada a: ${data.round_number}`);
            }
            
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
            
            // Reproducir sonido de victoria
            try {
                sndWin.play().catch(e => {
                    console.log('⚠️ Error al reproducir sonido de victoria:', e);
                });
            } catch (e) {
                console.log('⚠️ Error al reproducir sonido de victoria:', e);
            }
            
            // Agregar efecto de sacudida de pantalla
            document.body.classList.add('shake-screen');
            setTimeout(() => {
                document.body.classList.remove('shake-screen');
            }, 500);
            
            if (data.winner && data.prize) {
                showWinnerAnimation(data.winner, data.prize, data.multiplier || 'N/A');
            } else {
                console.error('⚠️ Datos incompletos en game_finished:', data);
            }
            break;
            
        case 'player_joined':
            // Jugador se unió
            updatePlayerInfo(data.player_id, data.username, data.avatar_url, data.seat_position, data.stake || 0);
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
 * Usa Web Audio API para generar sonidos realistas de dados
 */
function playDiceSound() {
    try {
        // Crear y reproducir sonido de dados rodando
        const rollSoundData = createDiceRollSound();
        if (rollSoundData) {
            rollSoundData.source.start(0);
            rollSoundData.source.stop(rollSoundData.audioContext.currentTime + 1.2);
        }
        
        // Sonido de impacto cuando el dado se detiene (1200ms para sincronizar con el final de la animación)
        setTimeout(() => {
            const hitSoundData = createDiceHitSound();
            if (hitSoundData) {
                hitSoundData.oscillator.start(0);
                if (hitSoundData.oscillator2) {
                    hitSoundData.oscillator2.start(0);
                    hitSoundData.oscillator2.stop(hitSoundData.audioContext.currentTime + 0.2);
                }
                hitSoundData.oscillator.stop(hitSoundData.audioContext.currentTime + 0.2);
            }
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
            
            // Reproducir sonido de shake adicional (solo si no está ya reproduciéndose)
            try {
                if (sndShake.paused || sndShake.currentTime === 0) {
                    sndShake.currentTime = 0;
                    sndShake.play().catch(e => {
                        console.log('⚠️ Error al reproducir sonido de shake:', e);
                    });
                }
            } catch (e) {
                console.log('⚠️ Error al reproducir sonido de shake:', e);
            }
            
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
                
                // Reproducir sonido de impacto cuando los dados caen (solo si no está ya reproduciéndose)
                try {
                    if (sndHit.paused || sndHit.currentTime === 0) {
                        sndHit.currentTime = 0;
                        sndHit.play().catch(e => {
                            console.log('⚠️ Error al reproducir sonido de impacto:', e);
                        });
                    }
                } catch (e) {
                    console.log('⚠️ Error al reproducir sonido de impacto:', e);
                }
                
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
    if (!results) return;

    // Usar el estado del juego guardado si está disponible, sino usar INITIAL_PLAYERS
    const players = (window.currentGameState && window.currentGameState.players) 
        ? window.currentGameState.players 
        : (typeof INITIAL_PLAYERS !== 'undefined' ? INITIAL_PLAYERS : []);
    
    // Crear un mapa de user_id -> seatNum para acceso rápido
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

    // 1. Actualizar barras de vida visualmente
    Object.entries(results).forEach(([playerId, resultData]) => {
        // El servidor envía: resultData = [dado1, dado2, vidas_restantes]
        // El índice [2] contiene las vidas reales, NO la suma de los dados
        const seatNum = playerIdToSeatMap[String(playerId)];
        if (seatNum) {
            // CRÍTICO: Usar el índice [2] que contiene las vidas restantes
            let currentLives = 3; // Valor por defecto
            if (Array.isArray(resultData) && resultData.length >= 3) {
                currentLives = resultData[2]; // Índice 2 es la vida real enviada por el servidor
            } else {
                console.warn(`⚠️ resultData no es un array válido para jugador ${playerId}:`, resultData);
            }
            
            // Usar INITIAL_LIVES global para calcular el porcentaje correctamente
            const percentage = Math.max(0, Math.min(100, (currentLives / INITIAL_LIVES) * 100));

            const healthBar = document.getElementById(`health-bar-${seatNum}`);
            const playerSeat = document.getElementById(`player-${seatNum}`);
            
            if (healthBar) {
                // Guardar el ancho anterior para detectar si las vidas disminuyeron
                const previousWidth = parseFloat(healthBar.style.width) || 100;
                const previousLives = Math.round((previousWidth / 100) * INITIAL_LIVES);
                
                // Asegurar que la barra se actualice correctamente: (vidas_recibidas / INITIAL_LIVES) * 100
                healthBar.style.width = (currentLives / INITIAL_LIVES) * 100 + '%';
                
                // Si vidas_recibidas es 0, marcar como eliminado inmediatamente
                if (currentLives === 0 && playerSeat) {
                    playerSeat.classList.add('player-eliminated');
                    console.log(`💀 Jugador ${playerId} eliminado (0 vidas) - marcado inmediatamente`);
                }
                
                // Colores dinámicos (sin gradientes para mejor rendimiento)
                if (percentage <= 33) {
                    healthBar.style.background = "#ff4d4d";
                } else if (percentage <= 66) {
                    healthBar.style.background = "#ffa502";
                } else {
                    healthBar.style.background = "#2ecc71";
                }
                
                // Efecto de Daño: Si las vidas disminuyeron, añadir parpadeo rojo y shake
                if (currentLives < previousLives && playerSeat) {
                    // Parpadeo rojo al contenedor .player-seat
                    playerSeat.style.backgroundColor = 'rgba(255, 0, 0, 0.4)';
                    setTimeout(() => {
                        playerSeat.style.backgroundColor = '';
                    }, 300);
                    
                    // Sacudida (Shake): Añadir clase de animación shake
                    playerSeat.classList.add('shake-screen');
                    setTimeout(() => {
                        playerSeat.classList.remove('shake-screen');
                    }, 400);
                    
                    console.log(`💥 Efecto de daño aplicado: ${previousLives} → ${currentLives} vidas (asiento ${seatNum})`);
                }
                
                console.log(`💚 Actualizando barra de vida para jugador ${playerId} (asiento ${seatNum}): ${currentLives} vidas (${percentage.toFixed(1)}%)`);
            } else {
                console.warn(`⚠️ No se encontró la barra de vida para asiento ${seatNum}`);
            }
        }
    });

    // 2. Lógica para marcar al eliminado visualmente
    if (eliminated) {
        // Marcar visualmente al eliminado
        const playerBoxes = document.querySelectorAll('.player-info');
        playerBoxes.forEach(box => {
            if (box.innerText.includes(eliminated)) {
                box.closest('.player-seat')?.classList.add('player-eliminated');
                console.log(`💀 Jugador ${eliminated} marcado como eliminado en UI`);
            }
        });
        
        // También buscar por user_id usando el mapa
        const eliminatedPlayer = players.find(p => 
            p.user_id === parseInt(eliminated) || 
            p.username === eliminated ||
            String(p.user_id) === String(eliminated)
        );
        
        if (eliminatedPlayer) {
            const seatNum = playerIdToSeatMap[String(eliminatedPlayer.user_id)];
            if (seatNum) {
                const playerSeat = document.getElementById(`player-${seatNum}`);
                if (playerSeat) {
                    playerSeat.classList.add('player-eliminated');
                    console.log(`💀 Jugador ${eliminated} marcado como eliminado en asiento ${seatNum}`);
                }
            }
        }
    }
    
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
                                // Si el array es [dado1, dado2, vidas], calcular el total
                                // Si el array es [dado1, dado2, total], usar el índice 2
                                if (resultData.length >= 3) {
                                    // Intentar calcular: dado1 + dado2
                                    const die1 = resultData[0] || 0;
                                    const die2 = resultData[1] || 0;
                                    total = die1 + die2;
                                } else {
                                    total = resultData[2] || 0; // Fallback al índice 2
                                }
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
                            // Si el array es [dado1, dado2, vidas], calcular el total
                            if (results[playerId].length >= 2) {
                                const die1 = results[playerId][0] || 0;
                                const die2 = results[playerId][1] || 0;
                                total = die1 + die2;
                            } else {
                                total = results[playerId][2] || 0; // Fallback
                            }
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

function updatePlayerInfo(playerId, username, avatarUrl, seatPosition, stake = 0) {
    const nameElement = document.getElementById(`name-${seatPosition}`);
    const avatarElement = document.getElementById(`avatar-${seatPosition}`);
    const stackElement = document.getElementById(`stack-${seatPosition}`);
    
    if (nameElement) nameElement.textContent = username;
    if (avatarElement) {
        avatarElement.src = avatarUrl;
        avatarElement.onerror = function() {
            // Si no hay avatar, usar un placeholder simple o dejar vacío
            this.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="64" height="64"%3E%3Ccircle cx="32" cy="32" r="30" fill="%239b59b6"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="white" font-size="24" font-weight="bold"%3E?%3C/text%3E%3C/svg%3E';
        };
    }
    
    // Actualizar dinero/stack del jugador
    if (stackElement && stake > 0) {
        stackElement.textContent = `$${parseFloat(stake).toFixed(2)}`;
        console.log(`💰 Actualizando stack para asiento ${seatPosition}: $${stake}`);
    }
}

function updateGameState(data) {
    // Guardar el estado del juego para usarlo en updateRoundResults
    window.currentGameState = data;
    
    // Actualizar número de ronda
    const roundNumberEl = document.getElementById('round-number');
    if (roundNumberEl && data.round_number !== undefined) {
        roundNumberEl.textContent = data.round_number;
        console.log(`🔄 Ronda actualizada a: ${data.round_number}`);
    }
    
    if (data.players) {
        data.players.forEach((player, index) => {
            const seatNum = index + 1;
            updatePlayerInfo(
                player.user_id,
                player.username,
                player.avatar_url,
                seatNum,
                data.entry_price || data.stake || 0  // Pasar el dinero de la apuesta
            );
            
            // Guardar el user_id en el elemento del asiento para referencia
            const playerSeat = document.getElementById(`player-${seatNum}`);
            if (playerSeat) {
                playerSeat.setAttribute('data-player-id', player.user_id);
            }
            
            // Reset: Al iniciar una nueva partida (game_state), todas las barras deben volver forzosamente al 100%
            const bar = document.getElementById(`health-bar-${seatNum}`);
            if (bar) {
                // Forzar reset al 100% al recibir game_state
                bar.style.width = "100%";
                bar.style.background = "#2ecc71"; // Verde por defecto (3 vidas)
                
                // Si el jugador tiene vidas definidas, usar ese valor, sino asumir INITIAL_LIVES
                const lives = (player.lives !== undefined) ? player.lives : INITIAL_LIVES;
                if (lives !== INITIAL_LIVES) {
                    const percent = (lives / INITIAL_LIVES) * 100;
                    bar.style.width = percent + "%";
                    
                    // Cambiar color según las vidas restantes
                    if (lives <= 1) {
                        bar.style.background = "#ff4d4d"; // Rojo
                    } else if (lives === 2) {
                        bar.style.background = "#ffa502"; // Naranja
                    } else {
                        bar.style.background = "#2ecc71"; // Verde
                    }
                }
                
                console.log(`💚 Inicializando/reseteando barra de vida para jugador ${player.username} (asiento ${seatNum}): ${lives} vidas (${bar.style.width})`);
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

