# Generated by Django 5.0.3 on 2024-03-16 03:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_wishlist_variation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wishlist',
            old_name='variation',
            new_name='variations',
        ),
    ]
