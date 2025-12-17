# middleware.py
from django.utils.deprecation import MiddlewareMixin

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
                # Si se detecta por dominio, no continuar con la lógica de usuario
                return None
        
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
        
        return None