# Generated by Django 5.0.2 on 2024-02-19 14:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0004_remove_category_name_remove_category_parent_category_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Product',
        ),
    ]
