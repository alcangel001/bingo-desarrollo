// Archivo de prueba para el sistema de sonidos de notificaciones
console.log('🔊 test_sounds.js cargado');

// Función para probar todos los sonidos disponibles
function testAllNotificationSounds() {
    console.log('🔊 Iniciando prueba de todos los sonidos...');
    
    const sounds = [
        'credit_purchase',
        'credit_request', 
        'withdrawal_request',
        'new_message',
        'admin_notification',
        'game_notification'
    ];
    
    let currentIndex = 0;
    
    function playNextSound() {
        if (currentIndex < sounds.length) {
            const soundType = sounds[currentIndex];
            console.log(`🔊 Probando sonido: ${soundType}`);
            
            if (window.playNotificationSound) {
                window.playNotificationSound(soundType);
            } else {
                console.error('🔊 Función playNotificationSound no encontrada');
            }
            
            currentIndex++;
            setTimeout(playNextSound, 1500); // Esperar 1.5 segundos entre sonidos
        } else {
            console.log('🔊 Prueba de sonidos completada');
        }
    }
    
    playNextSound();
}

// Función para probar el sistema de fallback
function testFallbackSounds() {
    console.log('🔊 Probando sistema de fallback...');
    
    if (window.fallbackNotificationSounds) {
        const sounds = [
            'credit_purchase',
            'credit_request', 
            'withdrawal_request',
            'new_message',
            'admin_notification',
            'game_notification'
        ];
        
        let currentIndex = 0;
        
        function playNextFallbackSound() {
            if (currentIndex < sounds.length) {
                const soundType = sounds[currentIndex];
                console.log(`🔊 Probando sonido de fallback: ${soundType}`);
                window.fallbackNotificationSounds.playNotificationSequence(soundType);
                currentIndex++;
                setTimeout(playNextFallbackSound, 1500);
            } else {
                console.log('🔊 Prueba de sonidos de fallback completada');
            }
        }
        
        playNextFallbackSound();
    } else {
        console.error('🔊 Sistema de fallback no encontrado');
    }
}

// Función para verificar el estado del AudioContext
function checkAudioContextStatus() {
    console.log('🔊 Verificando estado del AudioContext...');
    
    // Verificar sistema principal
    if (window.notificationSounds && window.notificationSounds.audioContext) {
        console.log('🔊 AudioContext principal:', {
            state: window.notificationSounds.audioContext.state,
            sampleRate: window.notificationSounds.audioContext.sampleRate,
            enabled: window.notificationSounds.isEnabled
        });
    } else {
        console.log('🔊 AudioContext principal: No inicializado');
    }
    
    // Verificar sistema de fallback
    if (window.fallbackNotificationSounds && window.fallbackNotificationSounds.audioContext) {
        console.log('🔊 AudioContext de fallback:', {
            state: window.fallbackNotificationSounds.audioContext.state,
            sampleRate: window.fallbackNotificationSounds.audioContext.sampleRate,
            enabled: window.fallbackNotificationSounds.isEnabled
        });
    } else {
        console.log('🔊 AudioContext de fallback: No inicializado');
    }
    
    // Verificar preferencias guardadas
    const savedPreference = localStorage.getItem('bingo_sounds_enabled');
    console.log('🔊 Preferencia guardada:', savedPreference);
    
    // Verificar estado de administrador
    checkAdminStatus();
}

// Función para verificar el estado de administrador
function checkAdminStatus() {
    console.log('🔊 Verificando estado de administrador...');
    
    const isAuthenticated = document.body.dataset.userAuthenticated === 'true';
    const isAdmin = document.body.dataset.userIsAdmin === 'true';
    const isSuperuser = document.body.dataset.userIsSuperuser === 'true';
    
    console.log('🔊 Estado del usuario:', {
        autenticado: isAuthenticated,
        es_admin: isAdmin,
        es_superuser: isSuperuser,
        puede_recibir_sonidos: isAdmin || isSuperuser
    });
    
    // Verificar usando el método del WebSocket handler
    if (window.wsNotificationHandler && typeof window.wsNotificationHandler.isUserAdmin === 'function') {
        const canReceiveSounds = window.wsNotificationHandler.isUserAdmin();
        console.log('🔊 WebSocket handler dice que es admin:', canReceiveSounds);
    }
}

// Función para simular notificaciones WebSocket
function simulateWebSocketNotifications() {
    console.log('🔊 Simulando notificaciones WebSocket...');
    
    const notifications = [
        {
            type: 'admin_notification',
            message: 'Nueva solicitud de créditos pendiente',
            url: '/admin/credit-requests/',
            sound_type: 'admin_notification'
        },
        {
            type: 'new_message',
            message: {
                sender: { username: 'UsuarioPrueba' },
                content: 'Mensaje de prueba'
            },
            sound_type: 'new_message'
        },
        {
            type: 'credit_approved_notification',
            message: 'Sus créditos han sido aprobados',
            sound_type: 'credit_purchase'
        },
        {
            type: 'withdrawal_request_notification',
            message: 'Nueva solicitud de retiro',
            sound_type: 'withdrawal_request'
        },
        {
            type: 'withdrawal_approved_notification',
            message: 'Retiro aprobado',
            sound_type: 'withdrawal_request'
        },
        {
            type: 'withdrawal_completed_notification',
            message: 'Retiro completado',
            sound_type: 'withdrawal_request'
        },
        {
            type: 'withdrawal_rejected_notification',
            message: 'Retiro rechazado',
            sound_type: 'withdrawal_request'
        }
    ];
    
    let currentIndex = 0;
    
    function sendNextNotification() {
        if (currentIndex < notifications.length) {
            const notification = notifications[currentIndex];
            console.log(`🔊 Enviando notificación simulada:`, notification);
            
            // Simular el manejo de mensaje WebSocket
            if (window.wsNotificationHandler) {
                window.wsNotificationHandler.handleMessage(notification);
            } else {
                console.log('🔊 WebSocket handler no encontrado, reproduciendo sonido directamente');
                if (window.playNotificationSound && notification.sound_type) {
                    window.playNotificationSound(notification.sound_type);
                }
            }
            
            currentIndex++;
            setTimeout(sendNextNotification, 3000); // Esperar 3 segundos entre notificaciones
        } else {
            console.log('🔊 Simulación de notificaciones completada');
        }
    }
    
    sendNextNotification();
}

// Crear botones de prueba en la interfaz
function createTestButtons() {
    // Solo crear botones si estamos en modo de desarrollo o si el usuario es admin
    const isAdmin = document.body.dataset.userAuthenticated === 'true' && 
                   document.querySelector('[data-is-admin="true"]');
    
    if (!isAdmin && !window.location.hostname.includes('localhost') && !window.location.hostname.includes('127.0.0.1')) {
        return; // No mostrar botones de prueba en producción para usuarios normales
    }
    
    console.log('🔊 Creando botones de prueba...');
    
    const testContainer = document.createElement('div');
    testContainer.id = 'sound-test-container';
    testContainer.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        background: rgba(44, 62, 80, 0.9);
        border: 2px solid #E74C3C;
        border-radius: 10px;
        padding: 15px;
        z-index: 9999;
        color: white;
        font-family: monospace;
        font-size: 12px;
        max-width: 300px;
    `;
    
    testContainer.innerHTML = `
        <div style="margin-bottom: 10px; font-weight: bold; color: #E74C3C;">
            🔊 Pruebas de Sonido
        </div>
        <button onclick="testAllNotificationSounds()" style="margin: 2px; padding: 5px 10px; background: #E74C3C; color: white; border: none; border-radius: 3px; cursor: pointer;">
            Probar Sonidos
        </button>
        <button onclick="testFallbackSounds()" style="margin: 2px; padding: 5px 10px; background: #3498DB; color: white; border: none; border-radius: 3px; cursor: pointer;">
            Probar Fallback
        </button>
        <button onclick="checkAudioContextStatus()" style="margin: 2px; padding: 5px 10px; background: #2ECC71; color: white; border: none; border-radius: 3px; cursor: pointer;">
            Verificar Estado
        </button>
        <button onclick="checkAdminStatus()" style="margin: 2px; padding: 5px 10px; background: #9B59B6; color: white; border: none; border-radius: 3px; cursor: pointer;">
            Verificar Admin
        </button>
        <button onclick="simulateWebSocketNotifications()" style="margin: 2px; padding: 5px 10px; background: #F39C12; color: white; border: none; border-radius: 3px; cursor: pointer;">
            Simular WS
        </button>
        <button onclick="this.parentElement.style.display='none'" style="margin: 2px; padding: 5px 10px; background: #95A5A6; color: white; border: none; border-radius: 3px; cursor: pointer;">
            Cerrar
        </button>
    `;
    
    document.body.appendChild(testContainer);
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔊 test_sounds.js: DOM cargado');
    
    // Esperar un poco para que otros scripts se carguen
    setTimeout(() => {
        createTestButtons();
        checkAudioContextStatus();
    }, 1000);
});

// Exportar funciones para uso global
window.testAllNotificationSounds = testAllNotificationSounds;
window.testFallbackSounds = testFallbackSounds;
window.checkAudioContextStatus = checkAudioContextStatus;
window.checkAdminStatus = checkAdminStatus;
window.simulateWebSocketNotifications = simulateWebSocketNotifications;