# Generated by Django 5.1.5 on 2025-01-29 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='rating',
            field=models.CharField(default=4, max_length=1),
        ),
    ]
