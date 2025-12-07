// Sistema de sonidos de notificación para Bingo
class NotificationSounds {
    constructor() {
        this.sounds = {
            credit_purchase: this.createTone(800, 0.3, 'sine'),
            credit_request: this.createTone(900, 0.8, 'square'),  // Duración doble (0.4 -> 0.8)
            withdrawal_request: this.createTone(800, 1.0, 'square'),  // Duración doble (0.5 -> 1.0)
            new_message: this.createTone(1000, 0.2, 'triangle'),
            game_notification: this.createTone(1200, 0.3, 'sawtooth'),
            admin_notification: this.createTone(500, 0.6, 'square')
        };
        
        this.isEnabled = this.getSoundPreference();
        this.audioContext = null;
        this.contextInitialized = false;
        
        console.log('🔊 NotificationSounds: Constructor ejecutado, enabled:', this.isEnabled);
    }
    
    // Inicializar AudioContext
    initAudioContext() {
        if (!this.audioContext) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                this.contextInitialized = true;
                console.log('🔊 NotificationSounds: AudioContext inicializado');
            } catch (error) {
                console.error('🔊 NotificationSounds: Error inicializando AudioContext:', error);
                return false;
            }
        }
        
        // Si el contexto está suspendido, intentar reanudarlo
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume().then(() => {
                console.log('🔊 NotificationSounds: AudioContext reanudado');
            }).catch(error => {
                console.error('🔊 NotificationSounds: Error reanudando AudioContext:', error);
            });
        }
        
        return true;
    }
    
    // Crear un tono usando Web Audio API
    createTone(frequency, duration, waveType = 'sine') {
        return () => {
            console.log(`🔊 NotificationSounds: createTone ejecutado - freq:${frequency}, dur:${duration}, type:${waveType}`);
            
            if (!this.isEnabled) {
                console.log('🔊 NotificationSounds: Sonidos deshabilitados en createTone');
                return;
            }
            
            try {
                // Usar el contexto compartido si está disponible
                if (!this.audioContext || this.audioContext.state === 'closed') {
                    if (!this.initAudioContext()) {
                        console.error('🔊 NotificationSounds: No se pudo inicializar AudioContext');
                        return;
                    }
                }
                
                const oscillator = this.audioContext.createOscillator();
                const gainNode = this.audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(this.audioContext.destination);
                
                oscillator.frequency.value = frequency;
                oscillator.type = waveType;
                
                // Configurar volumen más alto (fade in/out)
                gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
                gainNode.gain.linearRampToValueAtTime(0.8, this.audioContext.currentTime + 0.01); // Aumentado de 0.3 a 0.8
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
                
                console.log('🔊 NotificationSounds: Iniciando oscilador...');
                oscillator.start(this.audioContext.currentTime);
                oscillator.stop(this.audioContext.currentTime + duration);
                console.log('🔊 NotificationSounds: Oscilador iniciado y programado para parar');
            } catch (error) {
                console.error('🔊 NotificationSounds: Error en createTone:', error);
            }
        };
    }
    
    // Sonidos específicos
    playCreditPurchaseSound() {
        console.log('🔊 NotificationSounds: playCreditPurchaseSound ejecutado');
        this.sounds.credit_purchase();
    }
    
    playCreditRequestSound() {
        console.log('🔊 NotificationSounds: playCreditRequestSound ejecutado');
        this.sounds.credit_request();
    }
    
    playWithdrawalRequestSound() {
        console.log('🔊 NotificationSounds: playWithdrawalRequestSound ejecutado');
        this.sounds.withdrawal_request();
    }
    
    playNewMessageSound() {
        console.log('🔊 NotificationSounds: playNewMessageSound ejecutado');
        this.sounds.new_message();
    }
    
    playGameNotificationSound() {
        console.log('🔊 NotificationSounds: playGameNotificationSound ejecutado');
        this.sounds.game_notification();
    }
    
    playAdminNotificationSound() {
        console.log('🔊 NotificationSounds: playAdminNotificationSound ejecutado');
        this.sounds.admin_notification();
    }
    
    // Control de sonidos
    enableSounds() {
        this.isEnabled = true;
        localStorage.setItem('bingo_sounds_enabled', 'true');
    }
    
    disableSounds() {
        this.isEnabled = false;
        localStorage.setItem('bingo_sounds_enabled', 'false');
    }
    
    toggleSounds() {
        if (this.isEnabled) {
            this.disableSounds();
        } else {
            this.enableSounds();
        }
        return this.isEnabled;
    }
    
    getSoundPreference() {
        const saved = localStorage.getItem('bingo_sounds_enabled');
        return saved !== 'false'; // Por defecto habilitado
    }
    
    // Crear secuencia de sonidos más compleja
    playNotificationSequence(type) {
        console.log('🔊 NotificationSounds: playNotificationSequence llamado con tipo:', type);
        console.log('🔊 NotificationSounds: isEnabled:', this.isEnabled);
        
        if (!this.isEnabled) {
            console.log('🔊 NotificationSounds: Sonidos deshabilitados');
            return;
        }
        
        // Asegurar que el AudioContext esté inicializado
        if (!this.initAudioContext()) {
            console.error('🔊 NotificationSounds: No se pudo inicializar AudioContext para reproducir sonido');
            return;
        }
        
        console.log('🔊 NotificationSounds: Reproduciendo secuencia para:', type);
        
        switch(type) {
            case 'credit_purchase':
                console.log('🔊 NotificationSounds: Reproduciendo sonido de compra de créditos');
                this.playCreditPurchaseSound();
                setTimeout(() => this.playCreditPurchaseSound(), 200);
                break;
            case 'credit_request':
                console.log('🔊 NotificationSounds: Reproduciendo sonido de solicitud de créditos (ALERTA - 6 veces)');
                // Repetir 6 veces con intervalos cortos para hacerlo más notorio
                this.playCreditRequestSound();
                setTimeout(() => this.playCreditRequestSound(), 400);
                setTimeout(() => this.playCreditRequestSound(), 800);
                setTimeout(() => this.playCreditRequestSound(), 1200);
                setTimeout(() => this.playCreditRequestSound(), 1600);
                setTimeout(() => this.playCreditRequestSound(), 2000);
                break;
            case 'withdrawal_request':
                console.log('🔊 NotificationSounds: Reproduciendo sonido de solicitud de retiro (ALERTA - 6 veces)');
                // Repetir 6 veces con intervalos cortos para hacerlo más notorio
                this.playWithdrawalRequestSound();
                setTimeout(() => this.playWithdrawalRequestSound(), 400);
                setTimeout(() => this.playWithdrawalRequestSound(), 800);
                setTimeout(() => this.playWithdrawalRequestSound(), 1200);
                setTimeout(() => this.playWithdrawalRequestSound(), 1600);
                setTimeout(() => this.playWithdrawalRequestSound(), 2000);
                break;
            case 'new_message':
                console.log('🔊 NotificationSounds: Reproduciendo sonido de nuevo mensaje');
                this.playNewMessageSound();
                break;
            case 'admin_notification':
                console.log('🔊 NotificationSounds: Reproduciendo sonido de notificación de admin');
                this.playAdminNotificationSound();
                setTimeout(() => this.playAdminNotificationSound(), 400);
                break;
            case 'game_notification':
                console.log('🔊 NotificationSounds: Reproduciendo sonido de notificación de juego');
                this.playGameNotificationSound();
                break;
            default:
                console.log('🔊 NotificationSounds: Reproduciendo sonido por defecto');
                this.playGameNotificationSound();
        }
    }
}

// Crear instancia global
window.notificationSounds = new NotificationSounds();

// Función helper para usar desde otros scripts
function playNotificationSound(type) {
    if (window.notificationSounds) {
        window.notificationSounds.playNotificationSequence(type);
    }
}

// Función para crear botón de control de sonidos
function createSoundControlButton() {
    const button = document.createElement('button');
    button.id = 'sound-toggle-btn';
    button.className = 'btn btn-sm btn-outline-secondary';
    button.innerHTML = '<i class="fas fa-volume-up"></i>';
    button.title = 'Alternar sonidos de notificación';
    
    button.addEventListener('click', () => {
        const enabled = window.notificationSounds.toggleSounds();
        button.innerHTML = enabled ? '<i class="fas fa-volume-up"></i>' : '<i class="fas fa-volume-mute"></i>';
        button.className = enabled ? 'btn btn-sm btn-outline-secondary' : 'btn btn-sm btn-outline-danger';
    });
    
    // Establecer estado inicial
    if (!window.notificationSounds.isEnabled) {
        button.innerHTML = '<i class="fas fa-volume-mute"></i>';
        button.className = 'btn btn-sm btn-outline-danger';
    }
    
    return button;
}
