// Sistema de notificaciones WebSocket con sonidos
class WebSocketNotificationHandler {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 5000;
        
        this.init();
    }
    
    init() {
        this.connect();
        this.setupEventListeners();
    }
    
    connect() {
        // Detectar iOS
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || 
                     (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
        
        // Si ya hay un socket abierto o en proceso de conexión, no crear otro
        if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || this.socket.readyState === WebSocket.OPEN)) {
            console.log('WebSocket ya está conectado o conectando, no crear otro');
            return;
        }
        
        // Cerrar socket anterior si existe
        if (this.socket) {
            try {
                this.socket.close();
            } catch (e) {
                console.log('Error al cerrar socket anterior:', e);
            }
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;
        
        try {
            this.socket = new WebSocket(wsUrl);
            
            // En iOS, añadir timeout para evitar conexiones colgadas
            if (isIOS) {
                const connectionTimeout = setTimeout(() => {
                    if (this.socket && this.socket.readyState === WebSocket.CONNECTING) {
                        console.log('Timeout de conexión WebSocket en iOS, cerrando');
                        this.socket.close();
                        this.isConnected = false;
                    }
                }, 10000); // 10 segundos timeout
                
                this.socket.onopen = (event) => {
                    clearTimeout(connectionTimeout);
                    console.log('WebSocket conectado');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.showConnectionStatus(true);
                };
            } else {
                this.socket.onopen = (event) => {
                    console.log('WebSocket conectado');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.showConnectionStatus(true);
                };
            }
            
            this.socket.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };
            
            this.socket.onclose = (event) => {
                console.log('WebSocket desconectado', event.code, event.reason);
                this.isConnected = false;
                this.showConnectionStatus(false);
                
                // En iOS, solo reconectar si no fue un cierre normal (código 1000)
                // y si no estamos en un loop de reconexión
                if (isIOS && event.code === 1000) {
                    console.log('Cierre normal del WebSocket en iOS, no reconectar');
                    return;
                }
                
                // No reconectar inmediatamente en iOS si hay muchos intentos
                if (isIOS && this.reconnectAttempts >= 3) {
                    console.log('Demasiados intentos de reconexión en iOS, esperando más tiempo');
                    setTimeout(() => {
                        this.attemptReconnect();
                    }, 15000); // Esperar 15 segundos antes de intentar de nuevo
                } else {
                    this.attemptReconnect();
                }
            };
            
            this.socket.onerror = (error) => {
                console.error('Error en WebSocket:', error);
                this.isConnected = false;
                // En iOS, no intentar reconectar inmediatamente en caso de error
                // El onclose se encargará de la reconexión
            };
            
        } catch (error) {
            console.error('Error al conectar WebSocket:', error);
            this.isConnected = false;
            // En iOS, esperar más tiempo antes de reintentar
            const delay = isIOS ? 10000 : 5000;
            setTimeout(() => {
                this.attemptReconnect();
            }, delay);
        }
    }
    
    attemptReconnect() {
        // Detectar iOS
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || 
                     (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
        
        // Protección contra loops infinitos en iOS
        const reconnectKey = 'ws_reconnect_attempt';
        const lastReconnect = sessionStorage.getItem(reconnectKey);
        const now = Date.now();
        
        // Si hubo una reconexión hace menos de 5 segundos, no reconectar de nuevo
        if (lastReconnect && (now - parseInt(lastReconnect)) < 5000) {
            console.log('Prevención de reconexión infinita activada');
            return;
        }
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Intentando reconectar... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            // Guardar timestamp de la reconexión
            sessionStorage.setItem(reconnectKey, now.toString());
            
            // En iOS, usar intervalos más largos para evitar problemas
            const reconnectDelay = isIOS ? this.reconnectInterval * 2 : this.reconnectInterval;
            
            setTimeout(() => {
                // Limpiar el flag antes de reconectar
                sessionStorage.removeItem(reconnectKey);
                this.connect();
            }, reconnectDelay);
        } else {
            console.log('Máximo número de intentos de reconexión alcanzado');
            sessionStorage.removeItem(reconnectKey);
        }
    }
    
    handleMessage(data) {
        console.log('🔊 WebSocket mensaje recibido:', data);
        
        // Verificar si el usuario es administrador antes de reproducir sonidos
        const isAdmin = this.isUserAdmin();
        console.log('🔊 Usuario es admin:', isAdmin);
        
        switch (data.type) {
            case 'admin_notification':
                console.log('🔊 Procesando notificación de admin');
                this.handleAdminNotification(data);
                break;
            case 'new_message':
                console.log('🔊 Procesando nuevo mensaje');
                this.handleNewMessage(data);
                break;
            case 'credit_approved_notification':
                console.log('🔊 Procesando crédito aprobado');
                this.handleCreditApproved(data);
                break;
            case 'credit_rejected_notification':
                console.log('🔊 Procesando crédito rechazado');
                this.handleCreditRejected(data);
                break;
            case 'card_purchased':
                console.log('🔊 Procesando compra de cartón');
                this.handleCardPurchased(data);
                break;
            case 'withdrawal_request_notification':
                console.log('🔊 Procesando solicitud de retiro');
                this.handleWithdrawalRequest(data);
                break;
            case 'withdrawal_approved_notification':
                console.log('🔊 Procesando retiro aprobado');
                this.handleWithdrawalApproved(data);
                break;
            case 'withdrawal_completed_notification':
                console.log('🔊 Procesando retiro completado');
                this.handleWithdrawalCompleted(data);
                break;
            case 'withdrawal_rejected_notification':
                console.log('🔊 Procesando retiro rechazado');
                this.handleWithdrawalRejected(data);
                break;
            default:
                console.log('🔊 Tipo de notificación no manejado:', data.type);
        }
        
        // Determinar si se debe reproducir sonido
        const shouldPlaySound = this.shouldPlaySound(data, isAdmin);
        
        if (shouldPlaySound) {
            // Reproducir sonido si está especificado
            if (data.sound_type && window.playNotificationSound) {
                console.log('🔊 Reproduciendo sonido:', data.sound_type);
                window.playNotificationSound(data.sound_type);
            } else if (data.sound_type) {
                console.log('🔊 Sonido especificado pero función playNotificationSound no encontrada');
            } else {
                // Reproducir sonido por defecto basado en el tipo de notificación
                console.log('🔊 No hay tipo de sonido especificado, usando sonido por defecto');
                if (window.playNotificationSound) {
                    switch(data.type) {
                        case 'admin_notification':
                            window.playNotificationSound('admin_notification');
                            break;
                        case 'new_message':
                            window.playNotificationSound('new_message');
                            break;
                        case 'credit_approved_notification':
                        case 'credit_rejected_notification':
                            window.playNotificationSound('credit_request');
                            break;
                        case 'withdrawal_approved_notification':
                        case 'withdrawal_completed_notification':
                        case 'withdrawal_rejected_notification':
                            window.playNotificationSound('withdrawal_request');
                            break;
                        case 'card_purchased':
                            window.playNotificationSound('credit_purchase');
                            break;
                        case 'withdrawal_request_notification':
                            window.playNotificationSound('withdrawal_request');
                            break;
                        default:
                            window.playNotificationSound('game_notification');
                    }
                }
            }
        } else {
            console.log('🔊 No se reproduce sonido para este tipo de notificación');
        }
    }
    
    handleAdminNotification(data) {
        this.showNotification('admin', data.message, data.url);
    }
    
    handleNewMessage(data) {
        this.showNotification('message', data.message.content || data.message, null);
    }
    
    handleCreditApproved(data) {
        this.showNotification('success', data.message, null);
    }
    
    handleCreditRejected(data) {
        this.showNotification('error', data.message, null);
    }
    
    handleCardPurchased(data) {
        // No mostrar notificación para compras de cartones de otros usuarios
        // Solo reproducir sonido
    }
    
    handleWithdrawalRequest(data) {
        this.showNotification('info', data.message, null);
    }
    
    handleWithdrawalApproved(data) {
        this.showNotification('success', data.message, null);
    }
    
    handleWithdrawalCompleted(data) {
        this.showNotification('success', data.message, null);
    }
    
    handleWithdrawalRejected(data) {
        this.showNotification('error', data.message, null);
    }
    
    showNotification(type, message, url) {
        // Usar SweetAlert2 para mostrar notificaciones
        const iconMap = {
            'admin': 'info',
            'message': 'envelope',
            'success': 'success',
            'error': 'error',
            'info': 'info'
        };
        
        const titleMap = {
            'admin': 'Notificación de Admin',
            'message': 'Nuevo Mensaje',
            'success': 'Créditos Aprobados',
            'error': 'Créditos Rechazados',
            'info': 'Solicitud de Retiro'
        };
        
        Swal.fire({
            icon: iconMap[type] || 'info',
            title: titleMap[type] || 'Notificación',
            text: message,
            showConfirmButton: true,
            confirmButtonText: url ? 'Ver' : 'OK',
            allowOutsideClick: true,
            timer: url ? 10000 : 5000,
            timerProgressBar: true
        }).then((result) => {
            if (result.isConfirmed && url) {
                window.location.href = url;
            }
        });
    }
    
    showConnectionStatus(connected) {
        // Crear o actualizar indicador de estado de conexión
        let statusIndicator = document.getElementById('ws-connection-status');
        
        if (!statusIndicator) {
            statusIndicator = document.createElement('div');
            statusIndicator.id = 'ws-connection-status';
            statusIndicator.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 12px;
                z-index: 9999;
                transition: all 0.3s ease;
            `;
            document.body.appendChild(statusIndicator);
        }
        
        if (connected) {
            statusIndicator.textContent = '🟢 Conectado';
            statusIndicator.style.backgroundColor = '#28a745';
            statusIndicator.style.color = 'white';
        } else {
            statusIndicator.textContent = '🔴 Desconectado';
            statusIndicator.style.backgroundColor = '#dc3545';
            statusIndicator.style.color = 'white';
        }
        
        // Ocultar después de 3 segundos si está conectado
        if (connected) {
            setTimeout(() => {
                if (statusIndicator) {
                    statusIndicator.style.opacity = '0.7';
                }
            }, 3000);
        }
    }
    
    isUserAdmin() {
        // Verificar si el usuario es administrador usando los datos del template
        // Usar tanto is_admin como is_superuser para mayor compatibilidad
        const isAdmin = document.body.dataset.userIsAdmin === 'true' || 
                       document.body.dataset.userIsSuperuser === 'true' ||
                       document.querySelector('[data-is-admin="true"]') ||
                       document.querySelector('[data-is-superuser="true"]');
        return !!isAdmin;
    }
    
    shouldPlaySound(data, isAdmin) {
        // Tipos de notificaciones que siempre suenan (para todos los usuarios)
        const personalNotifications = [
            'credit_approved_notification',
            'credit_rejected_notification',
            'withdrawal_approved_notification',
            'withdrawal_completed_notification',
            'withdrawal_rejected_notification',
            'new_message',
            'win_notification'
        ];
        
        // Tipos de notificaciones que solo suenan para administradores
        const adminOnlyNotifications = [
            'admin_notification',
            'card_purchased',
            'withdrawal_request_notification'
        ];
        
        // Notificaciones que solo suenan cuando el admin NO está en un bingo activo
        const adminNotificationsWhenBingoClosed = [
            'new_credit_request',
            'new_withdrawal_request'
        ];
        
        // Verificar si el usuario está en un bingo activo
        const isInActiveBingo = this.isUserInActiveBingo();
        
        // Si es una notificación personal, siempre suena
        if (personalNotifications.includes(data.type)) {
            console.log('🔊 Notificación personal detectada, reproduciendo sonido');
            return true;
        }
        
        // Si es una notificación de admin que solo suena cuando el bingo está cerrado
        if (data.notification_type && adminNotificationsWhenBingoClosed.includes(data.notification_type)) {
            if (isAdmin && !isInActiveBingo) {
                console.log('🔊 Notificación de crédito/retiro detectada, reproduciendo sonido (admin fuera del bingo)');
                return true;
            } else if (isAdmin && isInActiveBingo) {
                console.log('🔊 Notificación de crédito/retiro detectada, NO reproduciendo sonido (admin en bingo activo)');
                return false;
            } else {
                console.log('🔊 Notificación de crédito/retiro detectada, NO reproduciendo sonido (usuario no es admin)');
                return false;
            }
        }
        
        // Si es una notificación de admin normal, solo suena para administradores
        if (adminOnlyNotifications.includes(data.type)) {
            if (isAdmin) {
                console.log('🔊 Notificación de admin detectada, reproduciendo sonido (usuario es admin)');
                return true;
            } else {
                console.log('🔊 Notificación de admin detectada, NO reproduciendo sonido (usuario no es admin)');
                return false;
            }
        }
        
        // Para otros tipos de notificaciones, usar lógica por defecto
        console.log('🔊 Tipo de notificación no clasificado, usando lógica por defecto');
        return isAdmin;
    }
    
    isUserInActiveBingo() {
        // Verificar si estamos en una página de game_room
        const isInGameRoom = window.location.pathname.includes('/game/') && 
                            window.location.pathname.match(/\/game\/\d+\//);
        
        if (!isInGameRoom) {
            console.log('🔊 Usuario NO está en game_room');
            return false;
        }
        
        // Si estamos en game_room, verificar si el juego está activo
        // Buscar variables globales que se definen en game_room.html
        const isGameStarted = typeof window.isGameStarted !== 'undefined' ? window.isGameStarted : false;
        const isGameFinished = typeof window.isGameFinished !== 'undefined' ? window.isGameFinished : false;
        
        // El bingo está activo si está iniciado y no terminado
        const isActive = isGameStarted && !isGameFinished;
        
        console.log('🔊 Usuario en game_room:', {
            isGameStarted,
            isGameFinished,
            isActive
        });
        
        return isActive;
    }
    
    setupEventListeners() {
        // Detectar iOS/Safari
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || 
                     (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
        
        // En iOS, el evento visibilitychange se dispara muy frecuentemente
        // causando loops infinitos. Usar throttling y protección adicional
        let lastVisibilityCheck = 0;
        const visibilityThrottle = isIOS ? 10000 : 2000; // 10 segundos en iOS, 2 en otros
        
        // Escuchar cuando la página se vuelve visible para reconectar
        document.addEventListener('visibilitychange', () => {
            const now = Date.now();
            
            // Throttling: solo reconectar si pasó suficiente tiempo
            if (now - lastVisibilityCheck < visibilityThrottle) {
                return;
            }
            
            // Solo reconectar si la página está visible Y no está conectado
            if (!document.hidden && !this.isConnected) {
                lastVisibilityCheck = now;
                
                // En iOS, esperar un poco más antes de reconectar
                const delay = isIOS ? 2000 : 500;
                setTimeout(() => {
                    // Verificar nuevamente que no esté conectado antes de reconectar
                    if (!this.isConnected) {
                        console.log('Reconectando WebSocket después de visibilitychange');
                        this.connect();
                    }
                }, delay);
            }
        });
        
        // En iOS, también manejar el evento pageshow (cuando se restaura desde cache)
        if (isIOS) {
            window.addEventListener('pageshow', (event) => {
                // Si la página se restauró desde cache y no hay conexión, reconectar
                if (event.persisted && !this.isConnected) {
                    console.log('Página restaurada desde cache en iOS, reconectando WebSocket');
                    setTimeout(() => {
                        if (!this.isConnected) {
                            this.connect();
                        }
                    }, 1000);
                }
            });
        }
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔊 WebSocket notifications: DOM cargado');
    
    // Solo inicializar si el usuario está autenticado
    const isAuthenticated = document.body.dataset.userAuthenticated === 'true' || 
                           document.querySelector('[data-user-authenticated="true"]');
    
    console.log('🔊 WebSocket notifications: Usuario autenticado:', isAuthenticated);
    console.log('🔊 WebSocket notifications: dataset.userAuthenticated:', document.body.dataset.userAuthenticated);
    
    if (isAuthenticated) {
        console.log('🔊 WebSocket notifications: Inicializando WebSocket...');
        window.wsNotificationHandler = new WebSocketNotificationHandler();
        window.notificationWebSocket = window.wsNotificationHandler;
    } else {
        console.log('🔊 WebSocket notifications: Usuario no autenticado, no se inicializa WebSocket');
    }
});

// Función global para probar sonidos
window.testNotificationSounds = function() {
    if (window.notificationSounds) {
        const sounds = ['credit_purchase', 'credit_request', 'withdrawal_request', 'new_message', 'admin_notification'];
        let index = 0;
        
        const playNext = () => {
            if (index < sounds.length) {
                window.notificationSounds.playNotificationSequence(sounds[index]);
                index++;
                setTimeout(playNext, 1000);
            }
        };
        
        playNext();
    }
};
