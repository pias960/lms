# Generated by Django 5.1.5 on 2025-02-07 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_course_urll'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='urll',
            new_name='url',
        ),
    ]
