# Generated by Django 5.0.3 on 2024-03-13 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_rename_phone_order_phone_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_total',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
