# Generated by Django 5.1.5 on 2025-01-24 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_consolidatedobjects_date_traitement_cao_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consolidatedobjects',
            name='date_traitement_cao',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='objectsfromcao',
            name='date_traitement_cao',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
