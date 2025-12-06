from decimal import Decimal

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('bingo_app', '0048_fix_card_theme_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='card_price',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.10'),
                max_digits=6,
                validators=[django.core.validators.MinValueValidator(Decimal('0.10'))],
                verbose_name='Precio por cartón'
            ),
        ),
    ]

