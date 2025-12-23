"""
Decoradores para el módulo de dados.
"""

from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import redirect
from .utils.dice_module import can_user_access_dice_module


def dice_module_required(view_func):
    """
    Decorador que verifica que el usuario tenga acceso al módulo de dados.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para acceder a este módulo")
            return redirect('login')
        
        can_access, error_message = can_user_access_dice_module(request.user)
        
        if not can_access:
            messages.error(request, error_message)
            return redirect('lobby')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def super_admin_required(view_func):
    """
    Decorador que verifica que el usuario sea super administrador.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not (request.user.is_superuser and request.user.is_staff):
            return HttpResponseForbidden("Solo super administradores pueden acceder a esta función")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

