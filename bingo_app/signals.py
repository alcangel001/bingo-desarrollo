"""
Señales para enviar emails de bienvenida cuando usuarios se registran
"""
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@receiver(user_signed_up)
def send_welcome_email_on_signup(sender, request, user, **kwargs):
    """
    Envía email de bienvenida cuando un usuario se registra (cualquier método)
    """
    try:
        if user.email:
            # Verificar si es un usuario nuevo (creado hace menos de 1 minuto)
            from django.utils import timezone
            from datetime import timedelta
            
            if user.date_joined:
                time_since_joined = timezone.now() - user.date_joined
                is_new = time_since_joined < timedelta(minutes=1)
                
                if is_new:
                    subject = '🎉 ¡Bienvenido a Bingo JyM!'
                    fecha = datetime.now().strftime('%d/%m/%Y')
                    
                    # Intentar determinar el método de registro
                    provider = 'Registro manual'
                    try:
                        from allauth.socialaccount.models import SocialAccount
                        social_account = SocialAccount.objects.filter(user=user).first()
                        if social_account:
                            provider = social_account.provider.title()
                    except:
                        pass
                    
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
                    
                    logger.info(f"Enviando email de bienvenida (señal) a {user.email} (método: {provider})")
                    result = send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    logger.info(f"Email de bienvenida enviado (señal) a {user.email}, resultado: {result}")
    except Exception as e:
        logger.error(f"Error enviando email de bienvenida (señal) a {user.email}: {str(e)}", exc_info=True)

@receiver(social_account_added)
def send_welcome_email_on_social_account_added(sender, request, sociallogin, **kwargs):
    """
    Envía email de bienvenida cuando se añade una cuenta social nueva
    NOTA: Este es un backup en caso de que el adapter no envíe el email
    """
    try:
        user = sociallogin.user
        
        if user and user.email:
            # Refrescar el usuario de la base de datos
            user.refresh_from_db()
            
            # Verificar si es un usuario nuevo (menos de 2 minutos desde date_joined)
            from django.utils import timezone
            from datetime import timedelta
            
            is_new = False
            if user.date_joined:
                time_since_joined = timezone.now() - user.date_joined
                is_new = time_since_joined < timedelta(minutes=2)
            
            # También verificar si es la primera cuenta social del usuario
            from allauth.socialaccount.models import SocialAccount
            social_accounts_count = SocialAccount.objects.filter(user=user).count()
            is_first_social_account = social_accounts_count <= 1
            
            # Solo enviar si es nuevo Y es la primera cuenta social
            if is_new and is_first_social_account:
                subject = '🎉 ¡Bienvenido a Bingo JyM!'
                fecha = datetime.now().strftime('%d/%m/%Y')
                provider = sociallogin.account.provider.title()
                
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
                
                logger.info(f"Enviando email de bienvenida (social_account_added signal) a {user.email} (provider: {provider})")
                result = send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"Email de bienvenida enviado (social_account_added signal) a {user.email}, resultado: {result}")
            else:
                logger.info(f"No se envía email (social_account_added signal) - is_new: {is_new}, is_first: {is_first_social_account}, email: {user.email}")
    except Exception as e:
        logger.error(f"Error enviando email de bienvenida (social_account_added): {str(e)}", exc_info=True)


