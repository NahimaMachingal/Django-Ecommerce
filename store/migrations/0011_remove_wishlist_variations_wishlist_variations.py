# Generated by Django 5.0.3 on 2024-03-16 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_rename_variation_wishlist_variations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlist',
            name='variations',
        ),
        migrations.AddField(
            model_name='wishlist',
            name='variations',
            field=models.ManyToManyField(null=True, to='store.variation'),
        ),
    ]