# Generated by Django 5.0.3 on 2024-05-14 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0019_alter_order_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='coupon',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
