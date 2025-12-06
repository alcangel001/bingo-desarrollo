from django.core.management.base import BaseCommand
from bingo_app.models import Transaction
from django.db.models import Sum, Count
from decimal import Decimal

class Command(BaseCommand):
    help = 'Verifica las transacciones en la base de datos'

    def handle(self, *args, **options):
        self.stdout.write("=== VERIFICACIÓN DE TRANSACCIONES ===\n")
        
        # 1. Contar todas las transacciones
        total_transactions = Transaction.objects.count()
        self.stdout.write(f"Total de transacciones: {total_transactions}")
        
        # 2. Ver transacciones por tipo
        transaction_types = Transaction.objects.values('transaction_type').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('transaction_type')
        
        self.stdout.write("\n=== TRANSACCIONES POR TIPO ===")
        for tt in transaction_types:
            self.stdout.write(f"{tt['transaction_type']}: {tt['count']} transacciones, total: ${tt['total']}")
        
        # 3. Ver las últimas 10 transacciones
        recent = Transaction.objects.all().order_by('-created_at')[:10]
        self.stdout.write("\n=== ÚLTIMAS 10 TRANSACCIONES ===")
        for t in recent:
            self.stdout.write(f"{t.created_at.strftime('%Y-%m-%d %H:%M')} | {t.transaction_type} | ${t.amount} | {t.description}")
        
        # 4. Buscar específicamente transacciones COMPRA
        compra_transactions = Transaction.objects.filter(transaction_type='COMPRA')
        compra_count = compra_transactions.count()
        compra_total = compra_transactions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        self.stdout.write(f"\n=== TRANSACCIONES COMPRA ===")
        self.stdout.write(f"Cantidad: {compra_count}")
        self.stdout.write(f"Total (negativo): ${compra_total}")
        self.stdout.write(f"Total (positivo): ${abs(compra_total)}")
        
        if compra_count > 0:
            self.stdout.write("\nDetalles de transacciones COMPRA:")
            for ct in compra_transactions.order_by('-created_at')[:5]:
                self.stdout.write(f"  {ct.created_at.strftime('%Y-%m-%d %H:%M')} | ${ct.amount} | {ct.description}")
        
        # 5. Verificar si hay transacciones de compra de créditos
        credit_purchase_types = ['CREDIT_PURCHASE', 'DEPOSIT', 'COMPRA_CREDITOS', 'PURCHASE_CREDITS']
        for cpt in credit_purchase_types:
            count = Transaction.objects.filter(transaction_type=cpt).count()
            if count > 0:
                total = Transaction.objects.filter(transaction_type=cpt).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
                self.stdout.write(f"\n{cpt}: {count} transacciones, total: ${total}")
        
        self.stdout.write("\n=== FIN DE VERIFICACIÓN ===")
