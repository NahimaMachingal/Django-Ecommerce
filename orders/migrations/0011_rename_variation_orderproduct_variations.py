# Generated by Django 5.0.3 on 2024-03-15 05:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_remove_orderproduct_color_remove_orderproduct_size'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderproduct',
            old_name='variation',
            new_name='variations',
        ),
    ]
