# Generated by Django 5.2.3 on 2025-06-23 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='show_in_home',
            field=models.BooleanField(default=False),
        ),
    ]
