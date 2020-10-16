# Generated by Django 3.1.1 on 2020-10-16 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='wallet_from',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='outcoming_transactions', to='wallet.wallet'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='wallet_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='incoming_transactions', to='wallet.wallet'),
        ),
    ]
