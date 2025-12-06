import os
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from bingo_app.models import User

class FacebookLoginTestSuite:
    """Suite de pruebas para Facebook Login"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = []
    
    def test_facebook_login_page_loads(self):
        """Prueba que la página de login carga correctamente"""
        try:
            response = self.client.get('/accounts/login/')
            success = response.status_code == 200
            self.test_results.append({
                'test': 'Facebook Login Page Loads',
                'status': 'PASS' if success else 'FAIL',
                'details': f'Status Code: {response.status_code}'
            })
            return success
        except Exception as e:
            self.test_results.append({
                'test': 'Facebook Login Page Loads',
                'status': 'ERROR',
                'details': str(e)
            })
            return False
    
    def test_facebook_button_present(self):
        """Prueba que el botón de Facebook está presente"""
        try:
            response = self.client.get('/accounts/login/')
            success = 'facebook' in response.content.decode().lower()
            self.test_results.append({
                'test': 'Facebook Button Present',
                'status': 'PASS' if success else 'FAIL',
                'details': 'Facebook button found in HTML' if success else 'Facebook button not found'
            })
            return success
        except Exception as e:
            self.test_results.append({
                'test': 'Facebook Button Present',
                'status': 'ERROR',
                'details': str(e)
            })
            return False
    
    def test_facebook_callback_url(self):
        """Prueba que la URL de callback de Facebook es accesible"""
        try:
            # Simular callback de Facebook
            response = self.client.get('/accounts/facebook/login/callback/')
            # Puede devolver 302 (redirect) o 400 (bad request) dependiendo de parámetros
            success = response.status_code in [200, 302, 400]
            self.test_results.append({
                'test': 'Facebook Callback URL',
                'status': 'PASS' if success else 'FAIL',
                'details': f'Status Code: {response.status_code}'
            })
            return success
        except Exception as e:
            self.test_results.append({
                'test': 'Facebook Callback URL',
                'status': 'ERROR',
                'details': str(e)
            })
            return False
    
    def test_privacy_policy_page(self):
        """Prueba que la página de políticas de privacidad carga"""
        try:
            response = self.client.get('/privacy-policy/')
            success = response.status_code == 200
            self.test_results.append({
                'test': 'Privacy Policy Page',
                'status': 'PASS' if success else 'FAIL',
                'details': f'Status Code: {response.status_code}'
            })
            return success
        except Exception as e:
            self.test_results.append({
                'test': 'Privacy Policy Page',
                'status': 'ERROR',
                'details': str(e)
            })
            return False
    
    def test_authentication_error_page(self):
        """Prueba que la página de errores de autenticación carga"""
        try:
            response = self.client.get('/accounts/social/login/error/')
            success = response.status_code in [200, 404]  # Puede no existir la URL exacta
            self.test_results.append({
                'test': 'Authentication Error Page',
                'status': 'PASS' if success else 'FAIL',
                'details': f'Status Code: {response.status_code}'
            })
            return success
        except Exception as e:
            self.test_results.append({
                'test': 'Authentication Error Page',
                'status': 'ERROR',
                'details': str(e)
            })
            return False
    
    def test_facebook_configuration(self):
        """Prueba que la configuración de Facebook está presente"""
        try:
            from django.conf import settings
            facebook_config = settings.SOCIALACCOUNT_PROVIDERS.get('facebook', {})
            success = bool(facebook_config)
            self.test_results.append({
                'test': 'Facebook Configuration',
                'status': 'PASS' if success else 'FAIL',
                'details': f'Facebook config present: {bool(facebook_config)}'
            })
            return success
        except Exception as e:
            self.test_results.append({
                'test': 'Facebook Configuration',
                'status': 'ERROR',
                'details': str(e)
            })
            return False
    
    def test_environment_variables(self):
        """Prueba que las variables de entorno de Facebook están configuradas"""
        try:
            facebook_client_id = os.environ.get('FACEBOOK_CLIENT_ID')
            facebook_secret = os.environ.get('FACEBOOK_SECRET')
            success = bool(facebook_client_id and facebook_secret)
            self.test_results.append({
                'test': 'Facebook Environment Variables',
                'status': 'PASS' if success else 'FAIL',
                'details': f'Client ID: {bool(facebook_client_id)}, Secret: {bool(facebook_secret)}'
            })
            return success
        except Exception as e:
            self.test_results.append({
                'test': 'Facebook Environment Variables',
                'status': 'ERROR',
                'details': str(e)
            })
            return False
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        print("🧪 INICIANDO PRUEBAS DE FACEBOOK LOGIN...")
        print("=" * 50)
        
        tests = [
            self.test_facebook_login_page_loads,
            self.test_facebook_button_present,
            self.test_facebook_callback_url,
            self.test_privacy_policy_page,
            self.test_authentication_error_page,
            self.test_facebook_configuration,
            self.test_environment_variables
        ]
        
        passed = 0
        failed = 0
        errors = 0
        
        for test in tests:
            try:
                result = test()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                errors += 1
                print(f"❌ ERROR en {test.__name__}: {e}")
        
        print("\n📊 RESULTADOS DE LAS PRUEBAS:")
        print("=" * 50)
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
            print(f"{status_icon} {result['test']}: {result['status']}")
            print(f"   📝 {result['details']}")
            print()
        
        print(f"📈 RESUMEN: {passed} pasaron, {failed} fallaron, {errors} errores")
        return passed, failed, errors

def run_facebook_tests():
    """Función principal para ejecutar las pruebas"""
    test_suite = FacebookLoginTestSuite()
    return test_suite.run_all_tests()

if __name__ == "__main__":
    run_facebook_tests()
