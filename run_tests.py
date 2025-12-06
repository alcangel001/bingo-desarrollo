#!/usr/bin/env python3
"""
Script de Pruebas Automatizadas para Bingo y Rifa JyM
Ejecuta pruebas de Facebook Login y otras funcionalidades críticas
"""

import os
import sys
import django
import subprocess
import time
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔧 {description}")
    print("=" * 50)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ ÉXITO: {description}")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ ERROR: {description}")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {description} - {str(e)}")
        return False

def test_database_connection():
    """Prueba la conexión a la base de datos"""
    print("\n🗄️ PROBANDO CONEXIÓN A BASE DE DATOS")
    print("=" * 50)
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Conexión a base de datos: OK")
                return True
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {str(e)}")
        return False

def test_facebook_configuration():
    """Prueba la configuración de Facebook"""
    print("\n📘 PROBANDO CONFIGURACIÓN DE FACEBOOK")
    print("=" * 50)
    try:
        from django.conf import settings
        
        # Verificar configuración básica
        facebook_config = settings.SOCIALACCOUNT_PROVIDERS.get('facebook', {})
        if not facebook_config:
            print("❌ Configuración de Facebook no encontrada")
            return False
        
        print("✅ Configuración de Facebook encontrada")
        
        # Verificar variables de entorno
        client_id = os.environ.get('FACEBOOK_CLIENT_ID')
        secret = os.environ.get('FACEBOOK_SECRET')
        
        if client_id and secret:
            print("✅ Variables de entorno de Facebook configuradas")
        else:
            print("⚠️ Variables de entorno de Facebook no configuradas")
        
        # Verificar configuración específica
        if facebook_config.get('METHOD') == 'oauth2':
            print("✅ Método OAuth2 configurado")
        else:
            print("⚠️ Método OAuth2 no configurado")
        
        if 'email' in facebook_config.get('SCOPE', []):
            print("✅ Scope de email configurado")
        else:
            print("⚠️ Scope de email no configurado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración de Facebook: {str(e)}")
        return False

def test_urls():
    """Prueba que las URLs críticas funcionen"""
    print("\n🌐 PROBANDO URLs CRÍTICAS")
    print("=" * 50)
    
    critical_urls = [
        ('/accounts/login/', 'Página de Login'),
        ('/privacy-policy/', 'Política de Privacidad'),
        ('/accounts/facebook/login/', 'Login Facebook'),
        ('/accounts/google/login/', 'Login Google'),
    ]
    
    success_count = 0
    for url, description in critical_urls:
        try:
            from django.test import Client
            client = Client()
            response = client.get(url)
            
            if response.status_code in [200, 302, 400]:  # 400 es aceptable para URLs de login
                print(f"✅ {description}: OK (Status: {response.status_code})")
                success_count += 1
            else:
                print(f"❌ {description}: ERROR (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {description}: EXCEPCIÓN - {str(e)}")
    
    return success_count == len(critical_urls)

def test_models():
    """Prueba que los modelos funcionen correctamente"""
    print("\n📊 PROBANDO MODELOS")
    print("=" * 50)
    try:
        from bingo_app.models import User, Game
        from allauth.socialaccount.models import SocialAccount
        
        # Contar registros
        user_count = User.objects.count()
        game_count = Game.objects.count()
        social_count = SocialAccount.objects.count()
        
        print(f"✅ Usuarios en BD: {user_count}")
        print(f"✅ Juegos en BD: {game_count}")
        print(f"✅ Cuentas sociales en BD: {social_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en modelos: {str(e)}")
        return False

def test_static_files():
    """Prueba que los archivos estáticos estén disponibles"""
    print("\n📁 PROBANDO ARCHIVOS ESTÁTICOS")
    print("=" * 50)
    
    static_files = [
        '/static/js/websocket_notifications.js',
        '/static/js/test_sounds.js',
        '/static/sounds/notification.js',
    ]
    
    success_count = 0
    for file_path in static_files:
        try:
            from django.test import Client
            client = Client()
            response = client.get(file_path)
            
            if response.status_code == 200:
                print(f"✅ {file_path}: OK")
                success_count += 1
            else:
                print(f"❌ {file_path}: ERROR (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {file_path}: EXCEPCIÓN - {str(e)}")
    
    return success_count == len(static_files)

def run_facebook_login_tests():
    """Ejecuta las pruebas específicas de Facebook Login"""
    print("\n🧪 EJECUTANDO PRUEBAS DE FACEBOOK LOGIN")
    print("=" * 50)
    try:
        # Importar y ejecutar las pruebas
        from test_facebook_login import run_facebook_tests
        passed, failed, errors = run_facebook_tests()
        
        if failed == 0 and errors == 0:
            print(f"\n✅ TODAS LAS PRUEBAS DE FACEBOOK PASARON ({passed} pruebas)")
            return True
        else:
            print(f"\n❌ ALGUNAS PRUEBAS FALLARON: {passed} pasaron, {failed} fallaron, {errors} errores")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando pruebas de Facebook: {str(e)}")
        return False

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS AUTOMATIZADAS DE BINGO Y RIFA JYM")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Lista de pruebas a ejecutar
    tests = [
        (test_database_connection, "Conexión a Base de Datos"),
        (test_facebook_configuration, "Configuración de Facebook"),
        (test_models, "Modelos de Django"),
        (test_urls, "URLs Críticas"),
        (test_static_files, "Archivos Estáticos"),
        (run_facebook_login_tests, "Pruebas de Facebook Login"),
    ]
    
    results = []
    total_tests = len(tests)
    
    for test_func, test_name in tests:
        print(f"\n⏳ Ejecutando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERROR CRÍTICO en {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL DE PRUEBAS")
    print("=" * 60)
    
    passed_tests = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status}: {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n📈 RESULTADO: {passed_tests}/{total_tests} pruebas pasaron")
    
    if passed_tests == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente.")
        return True
    else:
        print("⚠️ ALGUNAS PRUEBAS FALLARON. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
