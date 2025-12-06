from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime

class Command(BaseCommand):
    help = 'Envía un email de prueba para verificar que SendGrid está funcionando'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email destino para la prueba (opcional, usa DEFAULT_FROM_EMAIL si no se especifica)',
        )

    def handle(self, *args, **options):
        email_destino = options.get('email') or settings.DEFAULT_FROM_EMAIL
        
        if not email_destino:
            self.stdout.write(self.style.ERROR('❌ No hay email destino. Configura DEFAULT_FROM_EMAIL o usa --email'))
            return
        
        self.stdout.write('=' * 70)
        self.stdout.write('ENVIANDO EMAIL DE PRUEBA CON SENDGRID')
        self.stdout.write('=' * 70)
        self.stdout.write(f'Email destino: {email_destino}')
        self.stdout.write(f'Email remitente: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write('')
        
        try:
            # Enviar email de prueba
            subject = '🧪 Prueba de Email - Bingo JyM'
            fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            message = f'''
Hola,

Este es un email de prueba para verificar que SendGrid está funcionando correctamente.

Si recibes este mensaje, significa que:
✅ SendGrid está configurado correctamente
✅ La API key es válida
✅ Los emails se pueden enviar desde el sistema

Fecha: {fecha}
Sistema: Bingo JyM - Producción
            '''
            
            from_email = settings.DEFAULT_FROM_EMAIL
            
            self.stdout.write('Enviando email...')
            result = send_mail(
                subject,
                message,
                from_email,
                [email_destino],
                fail_silently=False,
            )
            
            if result == 1:
                self.stdout.write(self.style.SUCCESS('✅ Email enviado exitosamente!'))
                self.stdout.write('')
                self.stdout.write('Revisa tu bandeja de entrada (y spam) en:')
                self.stdout.write(f'   {email_destino}')
                self.stdout.write('')
                self.stdout.write('Si recibes el email, SendGrid está funcionando correctamente.')
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  Email no se envió (resultado: {result})'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al enviar email: {str(e)}'))
            self.stdout.write('')
            self.stdout.write('Posibles causas:')
            self.stdout.write('  - API key de SendGrid inválida')
            self.stdout.write('  - Email remitente no verificado en SendGrid')
            self.stdout.write('  - Problemas de red/conexión')
            import traceback
            traceback.print_exc()

