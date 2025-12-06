#!/usr/bin/env python3
"""
Script de Verificación de Estado de Lanzamiento
Verifica que todos los aspectos críticos estén listos para producción
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from django.conf import settings
from django.db import connection
from bingo_app.models import User, PercentageSettings, BankAccount, Game, Raffle
from channels.layers import get_channel_layer

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# Lista global de resultados
results = []

def check_secret_key():
    """Verifica que SECRET_KEY esté configurado correctamente"""
    print_header("1. VERIFICACIÓN DE SECRET_KEY")
    
    secret_key = getattr(settings, 'SECRET_KEY', None)
    
    if not secret_key:
        print_error("SECRET_KEY no está configurado")
        results.append(('SECRET_KEY', False, 'No configurado'))
        return False
    
    if len(secret_key) < 50:
        print_error(f"SECRET_KEY es muy corto ({len(secret_key)} caracteres, mínimo 50)")
        results.append(('SECRET_KEY', False, 'Muy corto'))
        return False
    
    # Verificar diversidad de caracteres
    unique_chars = len(set(secret_key))
    if unique_chars < 5:
        print_error(f"SECRET_KEY tiene pocos caracteres únicos ({unique_chars})")
        results.append(('SECRET_KEY', False, 'Poca diversidad'))
        return False
    
    print_success(f"SECRET_KEY configurado correctamente ({len(secret_key)} caracteres, {unique_chars} únicos)")
    results.append(('SECRET_KEY', True, 'OK'))
    return True

def check_debug_mode():
    """Verifica que DEBUG esté en False"""
    print_header("2. VERIFICACIÓN DE DEBUG MODE")
    
    debug = getattr(settings, 'DEBUG', True)
    
    if debug:
        print_error("DEBUG=True (DEBE estar en False para producción)")
        results.append(('DEBUG', False, 'Activado'))
        return False
    
    print_success("DEBUG=False (correcto para producción)")
    results.append(('DEBUG', True, 'OK'))
    return True

def check_database():
    """Verifica conexión a base de datos"""
    print_header("3. VERIFICACIÓN DE BASE DE DATOS")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result:
                print_success("Conexión a PostgreSQL: OK")
                
                # Verificar tablas principales
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema='public' 
                    AND table_type='BASE TABLE'
                    AND table_name LIKE 'bingo_app%'
                """)
                tables = cursor.fetchall()
                print_info(f"Tablas de bingo_app encontradas: {len(tables)}")
                
                results.append(('Database', True, 'OK'))
                return True
    except Exception as e:
        print_error(f"Error de conexión a base de datos: {str(e)}")
        results.append(('Database', False, str(e)))
        return False

def check_migrations():
    """Verifica que todas las migraciones estén aplicadas"""
    print_header("4. VERIFICACIÓN DE MIGRACIONES")
    
    try:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connections
        
        executor = MigrationExecutor(connections['default'])
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print_warning(f"{len(plan)} migración(es) pendiente(s)")
            for migration in plan:
                print_info(f"  - {migration[0].app_label}.{migration[0].name}")
            results.append(('Migrations', False, 'Pendientes'))
            return False
        else:
            print_success("Todas las migraciones están aplicadas")
            results.append(('Migrations', True, 'OK'))
            return True
            
    except Exception as e:
        print_error(f"Error verificando migraciones: {str(e)}")
        results.append(('Migrations', False, str(e)))
        return False

def check_percentage_settings():
    """Verifica que PercentageSettings esté configurado"""
    print_header("5. VERIFICACIÓN DE CONFIGURACIÓN DE COMISIONES")
    
    try:
        settings_obj = PercentageSettings.objects.first()
        
        if not settings_obj:
            print_error("PercentageSettings no está configurado")
            print_info("Ejecutar: python manage.py shell")
            print_info("  from bingo_app.models import PercentageSettings")
            print_info("  PercentageSettings.objects.create(platform_commission=10.00)")
            results.append(('PercentageSettings', False, 'No configurado'))
            return False
        
        print_success(f"Comisión de plataforma: {settings_obj.platform_commission}%")
        print_info(f"  Tarifa creación de juego: ${settings_obj.game_creation_fee}")
        print_info(f"  Tarifa activada: {settings_obj.game_creation_fee_enabled}")
        print_info(f"  Comisión activada: {settings_obj.platform_commission_enabled}")
        
        results.append(('PercentageSettings', True, 'OK'))
        return True
        
    except Exception as e:
        print_error(f"Error verificando PercentageSettings: {str(e)}")
        results.append(('PercentageSettings', False, str(e)))
        return False

def check_payment_methods():
    """Verifica que haya métodos de pago configurados"""
    print_header("6. VERIFICACIÓN DE MÉTODOS DE PAGO")
    
    try:
        active_methods = BankAccount.objects.filter(is_active=True)
        all_methods = BankAccount.objects.all()
        
        if not all_methods.exists():
            print_error("No hay métodos de pago configurados")
            print_info("Ir al admin: /admin/bingo_app/bankaccount/add/")
            results.append(('Payment Methods', False, 'No configurados'))
            return False
        
        if not active_methods.exists():
            print_warning(f"Hay {all_methods.count()} método(s) pero NINGUNO activo")
            results.append(('Payment Methods', False, 'Ninguno activo'))
            return False
        
        print_success(f"{active_methods.count()} método(s) de pago activo(s)")
        for method in active_methods:
            print_info(f"  - {method.title}")
        
        results.append(('Payment Methods', True, 'OK'))
        return True
        
    except Exception as e:
        print_error(f"Error verificando métodos de pago: {str(e)}")
        results.append(('Payment Methods', False, str(e)))
        return False

def check_admin_user():
    """Verifica que exista al menos un superusuario"""
    print_header("7. VERIFICACIÓN DE USUARIO ADMIN")
    
    try:
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            print_error("No hay superusuarios configurados")
            print_info("Ejecutar: python manage.py createsu")
            results.append(('Admin User', False, 'No existe'))
            return False
        
        print_success(f"{superusers.count()} superusuario(s) configurado(s)")
        for admin in superusers:
            print_info(f"  - {admin.username} ({admin.email})")
        
        results.append(('Admin User', True, 'OK'))
        return True
        
    except Exception as e:
        print_error(f"Error verificando admin: {str(e)}")
        results.append(('Admin User', False, str(e)))
        return False

def check_redis():
    """Verifica conexión a Redis"""
    print_header("8. VERIFICACIÓN DE REDIS")
    
    try:
        channel_layer = get_channel_layer()
        
        if not channel_layer:
            print_error("Channel layer no está configurado")
            results.append(('Redis', False, 'No configurado'))
            return False
        
        # Intentar enviar un mensaje de prueba
        import asyncio
        async def test_redis():
            await channel_layer.group_send(
                'test_group',
                {'type': 'test_message', 'message': 'test'}
            )
        
        asyncio.run(test_redis())
        print_success("Conexión a Redis: OK")
        results.append(('Redis', True, 'OK'))
        return True
        
    except Exception as e:
        print_error(f"Error conectando a Redis: {str(e)}")
        results.append(('Redis', False, str(e)))
        return False

def check_environment_variables():
    """Verifica variables de entorno críticas"""
    print_header("9. VERIFICACIÓN DE VARIABLES DE ENTORNO")
    
    critical_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'REDIS_URL',
        'ALLOWED_HOSTS',
    ]
    
    optional_vars = [
        'AGORA_APP_ID',
        'AGORA_APP_CERTIFICATE',
        'SENTRY_DSN',
        'SENDGRID_API_KEY',
        'FACEBOOK_CLIENT_ID',
        'GOOGLE_CLIENT_ID',
    ]
    
    all_ok = True
    
    print_info("Variables críticas:")
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            print_success(f"  {var}: Configurado")
        else:
            print_error(f"  {var}: NO configurado")
            all_ok = False
    
    print_info("\nVariables opcionales:")
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print_success(f"  {var}: Configurado")
        else:
            print_warning(f"  {var}: No configurado")
    
    if all_ok:
        results.append(('Environment Vars', True, 'OK'))
    else:
        results.append(('Environment Vars', False, 'Faltan críticas'))
    
    return all_ok

def check_security_settings():
    """Verifica configuraciones de seguridad"""
    print_header("10. VERIFICACIÓN DE SEGURIDAD")
    
    security_checks = {
        'CSRF_COOKIE_SECURE': getattr(settings, 'CSRF_COOKIE_SECURE', False),
        'SESSION_COOKIE_SECURE': getattr(settings, 'SESSION_COOKIE_SECURE', False),
        'SECURE_PROXY_SSL_HEADER': bool(getattr(settings, 'SECURE_PROXY_SSL_HEADER', None)),
        'ALLOWED_HOSTS': bool(getattr(settings, 'ALLOWED_HOSTS', [])),
    }
    
    all_secure = True
    
    for check, is_secure in security_checks.items():
        if is_secure:
            print_success(f"{check}: Activado")
        else:
            print_warning(f"{check}: No configurado")
            all_secure = False
    
    # Verificar HSTS (opcional pero recomendado)
    hsts = getattr(settings, 'SECURE_HSTS_SECONDS', 0)
    if hsts:
        print_success(f"SECURE_HSTS_SECONDS: {hsts} segundos")
    else:
        print_warning("SECURE_HSTS_SECONDS: No configurado (opcional)")
    
    if all_secure:
        results.append(('Security Settings', True, 'OK'))
    else:
        results.append(('Security Settings', False, 'Algunas faltantes'))
    
    return all_secure

def check_static_files():
    """Verifica que los archivos estáticos estén configurados"""
    print_header("11. VERIFICACIÓN DE ARCHIVOS ESTÁTICOS")
    
    try:
        static_root = getattr(settings, 'STATIC_ROOT', None)
        static_url = getattr(settings, 'STATIC_URL', None)
        
        if not static_root:
            print_error("STATIC_ROOT no está configurado")
            results.append(('Static Files', False, 'STATIC_ROOT no configurado'))
            return False
        
        if not static_url:
            print_error("STATIC_URL no está configurado")
            results.append(('Static Files', False, 'STATIC_URL no configurado'))
            return False
        
        print_success(f"STATIC_ROOT: {static_root}")
        print_success(f"STATIC_URL: {static_url}")
        
        # Verificar WhiteNoise
        middleware = getattr(settings, 'MIDDLEWARE', [])
        has_whitenoise = any('whitenoise' in m.lower() for m in middleware)
        
        if has_whitenoise:
            print_success("WhiteNoise está configurado")
        else:
            print_warning("WhiteNoise no está en MIDDLEWARE")
        
        results.append(('Static Files', True, 'OK'))
        return True
        
    except Exception as e:
        print_error(f"Error verificando archivos estáticos: {str(e)}")
        results.append(('Static Files', False, str(e)))
        return False

def print_summary():
    """Imprime resumen final"""
    print_header("📊 RESUMEN FINAL")
    
    passed = sum(1 for _, status, _ in results if status)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}Verificaciones completadas: {passed}/{total} ({percentage:.1f}%){Colors.END}\n")
    
    # Agrupar por estado
    critical_failures = []
    warnings = []
    successes = []
    
    for check, status, message in results:
        if status:
            successes.append((check, message))
        else:
            critical_failures.append((check, message))
    
    if critical_failures:
        print(f"{Colors.RED}{Colors.BOLD}❌ VERIFICACIONES FALLIDAS:{Colors.END}")
        for check, message in critical_failures:
            print(f"   {Colors.RED}• {check}: {message}{Colors.END}")
        print()
    
    if successes:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ VERIFICACIONES EXITOSAS:{Colors.END}")
        for check, message in successes:
            print(f"   {Colors.GREEN}• {check}: {message}{Colors.END}")
        print()
    
    # Conclusión
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    if percentage == 100:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ¡TODO ESTÁ LISTO PARA LANZAMIENTO!{Colors.END}")
        print(f"{Colors.GREEN}El sistema está 100% configurado y listo para producción.{Colors.END}")
        return True
    elif percentage >= 80:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  CASI LISTO - FALTAN ALGUNOS AJUSTES{Colors.END}")
        print(f"{Colors.YELLOW}Completar las verificaciones fallidas antes de lanzar.{Colors.END}")
        return False
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ NO ESTÁ LISTO PARA LANZAMIENTO{Colors.END}")
        print(f"{Colors.RED}Hay problemas críticos que deben resolverse.{Colors.END}")
        return False

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "═" * 58 + "╗")
    print("║" + "  VERIFICACIÓN DE ESTADO DE LANZAMIENTO".center(58) + "║")
    print("║" + "  Bingo JyM - Producción Ready Check".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print(f"{Colors.END}")
    print(f"{Colors.BLUE}Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Colors.END}\n")
    
    # Ejecutar todas las verificaciones
    checks = [
        check_secret_key,
        check_debug_mode,
        check_database,
        check_migrations,
        check_percentage_settings,
        check_payment_methods,
        check_admin_user,
        check_redis,
        check_environment_variables,
        check_security_settings,
        check_static_files,
    ]
    
    for check in checks:
        try:
            check()
        except Exception as e:
            print_error(f"Error ejecutando verificación: {str(e)}")
            results.append((check.__name__, False, str(e)))
    
    # Mostrar resumen
    is_ready = print_summary()
    
    # Código de salida
    sys.exit(0 if is_ready else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verificación interrumpida por el usuario{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error fatal: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

