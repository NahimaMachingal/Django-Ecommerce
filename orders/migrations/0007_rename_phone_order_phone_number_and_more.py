# Generated by Django 5.0.3 on 2024-03-13 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_delete_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='phone',
            new_name='phone_number',
        ),
        migrations.RemoveField(
            model_name='order',
            name='address_line_1',
        ),
        migrations.RemoveField(
            model_name='order',
            name='address_line_2',
        ),
        migrations.RemoveField(
            model_name='order',
            name='order_note',
        ),
        migrations.RemoveField(
            model_name='order',
            name='order_total',
        ),
        migrations.AddField(
            model_name='order',
            name='street_address',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='city',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='country',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.CharField(max_length=100),
        ),
    ]
