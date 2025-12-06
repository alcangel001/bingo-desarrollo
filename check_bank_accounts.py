import os
import django
from django.conf import settings
from bingo_app.models import BankAccount

# Configurar Django si no está configurado (necesario para scripts independientes)
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
    django.setup()

print("--- Verificando BankAccounts ---")
try:
    accounts = BankAccount.objects.all()
    if not accounts.exists():
        print("No se encontraron métodos de pago (BankAccounts).")
    for account in accounts:
        print(f"{account.title}: Activo={account.is_active}")
except Exception as e:
    print(f"Error al acceder a BankAccounts: {e}")
print("--- Fin de la verificación ---")