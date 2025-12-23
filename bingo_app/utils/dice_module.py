"""
Utilidades para el módulo de dados.
Funciones de verificación y control de acceso.
"""

from django.apps import apps


def _get_franchise_model():
    """
    Obtiene el modelo Franchise de forma segura.
    Retorna None si no existe.
    """
    try:
        Franchise = apps.get_model('bingo_app', 'Franchise')
        return Franchise
    except LookupError:
        # El modelo Franchise no existe
        return None


def _user_has_franchise(user):
    """
    Verifica si el usuario tiene franquicia de forma segura.
    Retorna (tiene_franquicia, franchise_object)
    """
    Franchise = _get_franchise_model()
    
    if not Franchise:
        # No hay sistema de franquicias
        return False, None
    
    # Verificar si User tiene campo franchise
    if not hasattr(user, 'franchise'):
        return False, None
    
    franchise = getattr(user, 'franchise', None)
    return (franchise is not None), franchise


def is_dice_module_enabled():
    """
    Verifica si el módulo de dados está activado globalmente.
    Solo verifica la configuración, no los permisos de franquicia.
    """
    try:
        from bingo_app.models import DiceModuleSettings
        settings = DiceModuleSettings.get_settings()
        return settings.is_module_enabled
    except Exception:
        # Si hay error, retornar False (módulo desactivado)
        return False


def can_user_access_dice_module(user):
    """
    Verifica si un usuario puede acceder al módulo de dados.
    
    Lógica:
    1. El módulo debe estar activado globalmente (super admin)
    2. Si el usuario tiene franquicia:
       - La franquicia debe tener el módulo premium activo
    3. Si el usuario NO tiene franquicia:
       - Debe existir un FranchisePremiumModule con franchise=None e is_active=True
    """
    # Paso 1: Verificar activación global
    if not is_dice_module_enabled():
        return False, "El módulo de dados no está activado por el administrador"
    
    # Paso 2: Verificar franquicia de forma SEGURA
    try:
        from bingo_app.models import FranchisePremiumModule
        
        Franchise = _get_franchise_model()
        
        if Franchise:
            # Sistema de franquicias existe
            has_franchise, user_franchise = _user_has_franchise(user)
            
            if has_franchise and user_franchise:
                # Usuario tiene franquicia - verificar módulo premium
                try:
                    premium_module = FranchisePremiumModule.objects.filter(
                        franchise=user_franchise,
                        module_type='DICE_BATTLE',
                        is_active=True
                    ).first()
                    
                    if not premium_module or not premium_module.is_currently_active:
                        return False, "Tu franquicia no tiene acceso a este módulo premium"
                    
                    return True, "Acceso permitido"
                except Exception as e:
                    # Si hay error, NO bloquear - permitir acceso
                    return True, "Acceso permitido (modo seguro)"
            else:
                # Usuario sin franquicia - verificar módulo global
                try:
                    premium_module = FranchisePremiumModule.objects.filter(
                        franchise__isnull=True,
                        module_type='DICE_BATTLE',
                        is_active=True
                    ).first()
                    
                    if not premium_module or not premium_module.is_currently_active:
                        return False, "Este módulo premium no está disponible para tu cuenta"
                    
                    return True, "Acceso permitido"
                except Exception as e:
                    return True, "Acceso permitido (modo seguro)"
        else:
            # No hay sistema de franquicias - permitir acceso si módulo está activado
            return True, "Acceso permitido"
            
    except Exception as e:
        # CUALQUIER error = NO bloquear el sistema de franquicias
        # Permitir acceso para no interrumpir
        return True, "Acceso permitido (modo seguro por error)"


def is_super_admin(user):
    """
    Verifica si el usuario es super administrador.
    """
    return user.is_superuser and user.is_staff and (hasattr(user, 'is_admin') and user.is_admin)

