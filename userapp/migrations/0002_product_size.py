# Generated by Django 5.0.2 on 2024-02-13 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='size',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
