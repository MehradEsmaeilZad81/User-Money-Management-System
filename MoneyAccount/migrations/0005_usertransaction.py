# Generated by Django 4.2.3 on 2023-08-13 07:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MoneyAccount', '0004_subscription_withdrawal_interval_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='MoneyAccount.moneyaccount')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='MoneyAccount.moneyaccount')),
            ],
        ),
    ]
