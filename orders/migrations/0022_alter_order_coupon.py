# Generated by Django 5.0.3 on 2024-05-14 17:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0021_alter_order_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='coupon',
            field=models.CharField(blank=True, null=True, max_length=100),
        ),
    ]
