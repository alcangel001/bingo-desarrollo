# middleware.py
from django.utils.deprecation import MiddlewareMixin
import os

class RailwayHostMiddleware(MiddlewareMixin):
    """
    Middleware para permitir automáticamente dominios de Railway.
    Modifica settings.ALLOWED_HOSTS antes de que CommonMiddleware valide el host.
    """
    def process_request(self, request):
        # Solo aplicar en Railway
        if not os.environ.get('RAILWAY_ENVIRONMENT'):
            return None
        
        host = request.get_host()
        if host:
            # Limpiar el host (quitar puerto si existe)
            host = host.split(':')[0].lower()
            
            # Si el host termina con .up.railway.app, agregarlo a ALLOWED_HOSTS si no está
            if host.endswith('.up.railway.app'):
                from django.conf import settings
                if host not in settings.ALLOWED_HOSTS:
                    settings.ALLOWED_HOSTS.append(host)
        
        return None


class FlashMessageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # Mensajes flash almacenados en sesión (sin DB)
            request.flash_messages = request.session.pop('flash_messages', [])
        else:
            request.flash_messages = []

    def process_response(self, request, response):
        if hasattr(request, 'flash_messages') and request.flash_messages:
            request.session['flash_messages'] = request.flash_messages
        return response


class FranchiseMiddleware(MiddlewareMixin):
    """
    Middleware para detectar y filtrar datos por franquicia.
    Agrega request.franchise al request para uso en vistas.
    Detecta la franquicia por dominio personalizado o por usuario.
    """
    def process_request(self, request):
        from .models import Franchise
        
        # Inicializar request.franchise como None
        request.franchise = None
        
        # 1. PRIMERO: Intentar detectar por dominio personalizado
        host = request.get_host()
        if host:
            # Limpiar el host (quitar puerto si existe)
            host = host.split(':')[0].lower()
            
            # Intentar obtener franquicia por dominio personalizado
            franchise_by_domain = Franchise.get_by_domain(host)
            if franchise_by_domain:
                request.franchise = franchise_by_domain
                # Guardar en sesión para mantenerla después de logout
                request.session['franchise_id'] = franchise_by_domain.id
                # Si se detecta por dominio, no continuar con la lógica de usuario
                return None
        
        # 1.5: Si no hay dominio personalizado, intentar obtener de la sesión
        if not request.franchise:
            franchise_id = request.session.get('franchise_id')
            if franchise_id:
                try:
                    request.franchise = Franchise.objects.get(id=franchise_id, is_active=True)
                except Franchise.DoesNotExist:
                    # Si la franquicia ya no existe o está inactiva, limpiar sesión
                    request.session.pop('franchise_id', None)
        
        # 2. SEGUNDO: Si no hay dominio personalizado, usar lógica de usuario
        if request.user.is_authenticated:
            # Si el usuario es super admin, puede ver todo (franchise = None)
            if request.user.is_superuser or request.user.is_admin:
                # Los super admins pueden ver todo, pero también pueden tener una franquicia asignada
                # Si tienen una franquicia propia, usarla
                if hasattr(request.user, 'owned_franchise'):
                    request.franchise = request.user.owned_franchise
                elif request.user.franchise:
                    request.franchise = request.user.franchise
                # Si no tienen franquicia, pueden ver todo (franchise = None)
            else:
                # Usuarios normales: usar su franquicia
                if hasattr(request.user, 'owned_franchise'):
                    # Es propietario de una franquicia
                    request.franchise = request.user.owned_franchise
                elif request.user.franchise:
                    # Pertenece a una franquicia
                    request.franchise = request.user.franchise
                # Si no tiene franquicia, request.franchise = None (usuario sin franquicia)
            
            # Guardar franquicia del usuario en sesión para mantenerla después de logout
            if request.franchise:
                request.session['franchise_id'] = request.franchise.id
        
        return None