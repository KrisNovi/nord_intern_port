# Generated by Django 3.2 on 2023-06-22 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comcodes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='publication_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата создания'),
        ),
    ]
