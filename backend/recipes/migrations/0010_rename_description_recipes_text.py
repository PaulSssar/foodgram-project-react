# Generated by Django 3.2.19 on 2023-06-01 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20230525_1023'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipes',
            old_name='description',
            new_name='text',
        ),
    ]