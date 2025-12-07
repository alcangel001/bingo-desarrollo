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
    """
    def process_request(self, request):
        # Inicializar request.franchise como None
        request.franchise = None
        
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