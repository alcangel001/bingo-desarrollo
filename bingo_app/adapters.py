from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from allauth.exceptions import ImmediateHttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
import logging
import re
from .error_monitor import log_facebook_error, facebook_monitor

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    
    def is_open_for_signup(self, request, sociallogin):
        """Permitir registro abierto para cuentas sociales"""
        return True
    
    def save_user(self, request, sociallogin, form=None):
        """
        Guarda un nuevo usuario de login social y envía email de bienvenida
        """
        # Verificar si el usuario ya existe ANTES de guardarlo
        # Esto es la forma más confiable de saber si es un usuario nuevo
        user_email = sociallogin.user.email or getattr(sociallogin.user, 'email', None)
        user_exists_before = False
        
        # Verificar por ID del objeto primero (si ya tiene pk, no es nuevo)
        if sociallogin.user.pk is not None:
            user_exists_before = True
            logger.info(f"Usuario ya tiene PK antes de guardar: {sociallogin.user.pk}")
        
        # Si no tiene PK, verificar por email
        if not user_exists_before and user_email:
            # Verificar si ya existe un usuario con este email
            try:
                existing_user = User.objects.filter(email__iexact=user_email).first()
                user_exists_before = existing_user is not None and existing_user.pk is not None
                logger.info(f"Usuario existente encontrado por email: {existing_user.pk if existing_user else None}")
            except Exception as e:
                logger.warning(f"Error verificando usuario existente: {e}")
        
        # Obtener el provider antes de guardar (puede no estar disponible después)
        provider = 'Unknown'
        try:
            provider = sociallogin.account.provider.title() if hasattr(sociallogin, 'account') and sociallogin.account else 'Unknown'
        except:
            pass
        
        logger.info(f"Social login save_user - Email: {user_email}, Exists before save: {user_exists_before}, Provider: {provider}")
        
        # Guardar el usuario
        user = super().save_user(request, sociallogin, form)
        
        # Refrescar el usuario de la base de datos para obtener datos actualizados
        user.refresh_from_db()
        
        # Obtener el email final (puede estar disponible ahora si no lo estaba antes)
        final_email = user.email or user_email or getattr(user, 'email', None)
        
        # Verificar nuevamente si es un usuario nuevo
        # La lógica principal: si no existía antes, es nuevo
        is_new_user = not user_exists_before
        
        # Verificación adicional: si date_joined es muy reciente (menos de 2 minutos), 
        # y no existía antes, entonces definitivamente es nuevo
        from django.utils import timezone
        from datetime import timedelta
        if user.date_joined and not user_exists_before:
            time_since_joined = timezone.now() - user.date_joined
            if time_since_joined < timedelta(minutes=2):
                is_new_user = True
            else:
                # Si pasó más de 2 minutos pero no existía antes, algo raro pasó
                # Pero aún así considerarlo nuevo si no existía antes
                is_new_user = True
        
        logger.info(f"Social login save_user - User ID: {user.pk}, Email: {final_email}, Is New: {is_new_user}, Date Joined: {user.date_joined}")
        
        # Enviar email de bienvenida solo para usuarios nuevos
        if is_new_user and final_email:
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                from datetime import datetime
                
                # Verificar que tenemos la configuración necesaria
                if not settings.DEFAULT_FROM_EMAIL:
                    logger.error(f"No se puede enviar email de bienvenida: DEFAULT_FROM_EMAIL no está configurado")
                else:
                    subject = '🎉 ¡Bienvenido a Bingo JyM!'
                    fecha = datetime.now().strftime('%d/%m/%Y')
                    # Usar el provider que obtuvimos antes, o intentar obtenerlo de nuevo
                    try:
                        if not provider or provider == 'Unknown':
                            provider = sociallogin.account.provider.title() if hasattr(sociallogin, 'account') and sociallogin.account else 'Registro Social'
                    except:
                        provider = provider if provider != 'Unknown' else 'Registro Social'
                    
                    message = f'''
Hola {user.username or user.first_name or 'Usuario'},

¡Bienvenido a Bingo JyM!

Tu cuenta ha sido creada exitosamente el {fecha} mediante {provider}.

Ahora puedes:
✅ Participar en juegos de bingo
✅ Comprar tickets para rifas
✅ Gestionar tus créditos
✅ Crear tus propios juegos (si eres organizador)

¡Gracias por unirte a nuestra comunidad!

Saludos,
El equipo de Bingo JyM
                    '''
                    
                    logger.info(f"=== INTENTANDO ENVIAR EMAIL DE BIENVENIDA ===")
                    logger.info(f"Destinatario: {final_email}")
                    logger.info(f"Remitente: {settings.DEFAULT_FROM_EMAIL}")
                    logger.info(f"Provider: {provider}")
                    logger.info(f"Usuario nuevo: {is_new_user}")
                    
                    result = send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [final_email],
                        fail_silently=False,  # No silenciar errores para poder debuggear
                    )
                    
                    if result == 1:
                        logger.info(f"✅ Email de bienvenida enviado EXITOSAMENTE a {final_email}, resultado: {result}")
                    else:
                        logger.warning(f"⚠️ Email de bienvenida NO se envió correctamente a {final_email}, resultado: {result}")
            except Exception as e:
                # Log el error pero no interrumpir el registro
                logger.error(f"❌ ERROR CRÍTICO enviando email de bienvenida a {final_email} (social login): {str(e)}", exc_info=True)
                logger.error(f"Tipo de error: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        else:
            if not is_new_user:
                logger.info(f"ℹ️ No se envía email de bienvenida - usuario ya existía (email: {final_email}, date_joined: {user.date_joined})")
            elif not final_email:
                logger.warning(f"⚠️ No se envía email de bienvenida - usuario no tiene email (user_id: {user.pk}, username: {user.username})")
        
        return user
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just prior to the social login process.
        Here we can intervene to ensure email verification for existing users.
        """
        try:
            # Información del request
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
            is_mobile = any(mobile in user_agent for mobile in ['Mobile', 'Android', 'iPhone', 'iPad'])
            provider = sociallogin.account.provider
            
            # Log para debugging
            logger.info(f"Social Login Debug - User Agent: {user_agent}")
            logger.info(f"Social Login Debug - IP: {ip_address}")
            logger.info(f"Social Login Debug - Provider: {provider}")
            logger.info(f"Social Login Debug - User Email: {sociallogin.user.email}")
            logger.info(f"Social Login Debug - Is Mobile: {is_mobile}")
            logger.info(f"Social Login Debug - Social Account UID: {sociallogin.account.uid}")
            
            # Validaciones de seguridad SOLO para Facebook (más permisivas)
            if provider == 'facebook':
                # Verificar si ya existe una cuenta de Facebook con este UID
                existing_account = SocialAccount.objects.filter(
                    provider='facebook',
                    uid=sociallogin.account.uid
                ).first()
                
                if existing_account:
                    # Si existe la cuenta social, usar el usuario existente
                    logger.info(f"Facebook account exists for UID {sociallogin.account.uid}, connecting to existing user {existing_account.user.id}")
                    # Actualizar el usuario en sociallogin para usar el existente
                    sociallogin.user = existing_account.user
                    # Monitoreo exitoso
                    facebook_monitor.monitor_facebook_login_attempt(request, success=True)
                    # Continuar con el proceso normal de allauth
                    return super().pre_social_login(request, sociallogin)
                
                # Si no existe, validar datos pero ser más permisivo
                validation_result = self._validate_facebook_login(request, sociallogin)
                if not validation_result:
                    logger.warning(f"Facebook validation failed, but allowing login to proceed")
                    # No bloquear el login, solo loggear
                    log_facebook_error('facebook_validation_failed', 'Facebook login validation failed but allowing', request)
                
                # Monitoreo de intento de login de Facebook
                facebook_monitor.monitor_facebook_login_attempt(request, success=True)
            
            user = sociallogin.user
            if user.pk and user.email:  # User exists AND has an email
                try:
                    email_address = EmailAddress.objects.get(user=user, email=user.email)
                    if not email_address.verified:
                        # If email is not verified, mark it as unverified and send a new confirmation email
                        email_address.verified = False
                        email_address.save()
                        email_address.send_confirmation(request, signup=False)
                except EmailAddress.DoesNotExist:
                    # This case should ideally not happen if the user exists and has an email
                    # but as a fallback, we can ensure an email address object is created and verified.
                    EmailAddress.objects.add_email(request, user, user.email, confirm=True)

            return super().pre_social_login(request, sociallogin)
            
        except Exception as e:
            logger.error(f"Error en pre_social_login: {str(e)}")
            # Solo registrar error de Facebook si es ese provider
            if sociallogin.account.provider == 'facebook':
                log_facebook_error('facebook_pre_login_error', str(e), request)
                facebook_monitor.monitor_facebook_login_attempt(request, success=False, error_message=str(e))
            # No bloquear el login por errores de validación
            return super().pre_social_login(request, sociallogin)
    
    def _validate_facebook_login(self, request, sociallogin):
        """Valida el login de Facebook con múltiples verificaciones (más permisivo)"""
        try:
            # 1. Verificar que es realmente Facebook
            if sociallogin.account.provider != 'facebook':
                logger.warning(f"Intento de login con provider incorrecto: {sociallogin.account.provider}")
                return False
            
            # 2. Verificar que la cuenta de Facebook tiene UID válido (más permisivo)
            if not sociallogin.account.uid or len(str(sociallogin.account.uid)) < 3:
                logger.warning(f"UID de Facebook inválido: {sociallogin.account.uid}")
                return False
            
            # 3. Verificar que el email existe (opcional - algunos usuarios pueden no tener email público)
            if not sociallogin.user.email:
                logger.warning(f"Email faltante en Facebook login, pero permitiendo login")
                # No bloquear si no hay email, solo loggear
            
            # 4. Verificar que el nombre existe (opcional - algunos usuarios pueden no tener nombre completo)
            if not sociallogin.user.first_name and not sociallogin.user.last_name:
                logger.warning("Nombre completo faltante en Facebook login, pero permitiendo login")
                # No bloquear si no hay nombre, solo loggear
            
            return True
            
        except Exception as e:
            logger.error(f"Error en validación de Facebook: {str(e)}")
            # En caso de error, permitir el login pero logear el error
            return True
    
    def _is_valid_email(self, email):
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def authentication_error(self, request, provider, error=None, exception=None, extra_context=None):
        """Maneja errores de autenticación social (Facebook, Google, etc.)"""
        try:
            error_message = str(error) if error else "Error de autenticación desconocido"
            
            # Solo registrar errores de Facebook si es ese provider
            if provider == 'facebook':
                logger.error(f"Facebook authentication error: {error_message}")
                
                # Monitoreo del error
                facebook_monitor.monitor_facebook_login_attempt(
                    request, 
                    success=False, 
                    error_message=error_message
                )
                
                # Log del error específico
                log_facebook_error('facebook_authentication_error', error_message, request)
                
                # Redirigir a página de error con mensaje específico
                messages.error(request, f"Error en el login con Facebook: {error_message}")
                return HttpResponseRedirect(reverse('login'))
            else:
                # Para otros providers (Google, etc.), solo loggear y continuar
                logger.warning(f"{provider} authentication error: {error_message}")
                messages.error(request, f"Error en el login con {provider}: {error_message}")
                return HttpResponseRedirect(reverse('login'))
            
        except Exception as e:
            logger.error(f"Error en manejo de authentication_error: {str(e)}")
            return super().authentication_error(request, provider, error, exception, extra_context)
