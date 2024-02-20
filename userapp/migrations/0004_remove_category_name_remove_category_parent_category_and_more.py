# Generated by Django 5.0.2 on 2024-02-18 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0003_product_image_delete_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='name',
        ),
        migrations.RemoveField(
            model_name='category',
            name='parent_category',
        ),
        migrations.AddField(
            model_name='category',
            name='cat_image',
            field=models.ImageField(blank=True, upload_to='photos/categories'),
        ),
        migrations.AddField(
            model_name='category',
            name='category_name',
            field=models.CharField(default='Uncategorized', max_length=255, unique=True),
        ),
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.CharField(default='Uncategorized', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, max_length=255),
        ),
    ]
