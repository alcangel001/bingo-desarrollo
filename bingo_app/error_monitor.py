import logging
import json
import time
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
import os

class ErrorMonitor:
    """Sistema de monitoreo de errores en tiempo real"""
    
    def __init__(self):
        self.logger = logging.getLogger('error_monitor')
        self.error_counts = {}
        self.last_reset = datetime.now()
    
    def log_error(self, error_type, error_message, user_info=None, request_info=None):
        """Registra un error con información detallada"""
        timestamp = datetime.now()
        
        error_data = {
            'timestamp': timestamp.isoformat(),
            'error_type': error_type,
            'error_message': error_message,
            'user_info': user_info or {},
            'request_info': request_info or {},
            'count': 1
        }
        
        # Incrementar contador de errores
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # Log del error
        self.logger.error(f"ERROR [{error_type}]: {error_message}")
        
        # Guardar en cache para monitoreo en tiempo real (solo si cache está disponible)
        try:
            cache_key = f"error_{error_type}_{timestamp.strftime('%Y%m%d_%H%M')}"
            cache.set(cache_key, error_data, timeout=3600)  # 1 hora
        except Exception:
            # Si cache no está disponible, continuar sin error
            pass
        
        # Alertas críticas
        if self.error_counts[error_type] > 10:  # Más de 10 errores del mismo tipo
            self.send_critical_alert(error_type, error_data)
    
    def send_critical_alert(self, error_type, error_data):
        """Envía alerta crítica cuando hay muchos errores"""
        alert_message = f"🚨 ALERTA CRÍTICA: {error_type} - {self.error_counts[error_type]} errores"
        self.logger.critical(alert_message)
        
        # Aquí podrías integrar con servicios como Slack, Discord, email, etc.
        print(f"🔔 {alert_message}")
    
    def get_error_summary(self, hours=24):
        """Obtiene resumen de errores de las últimas N horas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        summary = {
            'total_errors': sum(self.error_counts.values()),
            'error_types': dict(self.error_counts),
            'critical_errors': [],
            'timeframe': f"Últimas {hours} horas"
        }
        
        # Identificar errores críticos
        for error_type, count in self.error_counts.items():
            if count > 5:  # Más de 5 errores es crítico
                summary['critical_errors'].append({
                    'type': error_type,
                    'count': count
                })
        
        return summary
    
    def reset_counters(self):
        """Reinicia los contadores de errores"""
        self.error_counts = {}
        self.last_reset = datetime.now()
        self.logger.info("Contadores de errores reiniciados")

class FacebookLoginMonitor(ErrorMonitor):
    """Monitor específico para Facebook Login"""
    
    def monitor_facebook_login_attempt(self, request, success=True, error_message=None):
        """Monitorea intentos de login con Facebook"""
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        is_mobile = 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent
        
        request_info = {
            'user_agent': user_agent,
            'is_mobile': is_mobile,
            'ip_address': request.META.get('REMOTE_ADDR', 'Unknown'),
            'referer': request.META.get('HTTP_REFERER', 'Unknown')
        }
        
        if success:
            self.logger.info(f"Facebook Login SUCCESS - Mobile: {is_mobile}")
        else:
            self.log_error(
                'facebook_login_failed',
                error_message or 'Facebook login failed',
                request_info=request_info
            )
    
    def monitor_facebook_callback(self, request, success=True, error_message=None):
        """Monitorea callbacks de Facebook"""
        if not success:
            self.log_error(
                'facebook_callback_failed',
                error_message or 'Facebook callback failed',
                request_info={
                    'ip_address': request.META.get('REMOTE_ADDR', 'Unknown'),
                    'query_params': dict(request.GET)
                }
            )

# Instancia global del monitor
facebook_monitor = FacebookLoginMonitor()

def log_facebook_error(error_type, message, request=None, user=None):
    """Función helper para registrar errores de Facebook"""
    user_info = {}
    if user:
        user_info = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }
    
    request_info = {}
    if request:
        request_info = {
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
            'ip_address': request.META.get('REMOTE_ADDR', 'Unknown'),
            'path': request.path
        }
    
    facebook_monitor.log_error(error_type, message, user_info, request_info)

def get_facebook_error_summary():
    """Obtiene resumen de errores de Facebook"""
    return facebook_monitor.get_error_summary()

def reset_facebook_error_counters():
    """Reinicia contadores de errores de Facebook"""
    facebook_monitor.reset_counters()
