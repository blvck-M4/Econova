# Generated by Django 5.1.6 on 2025-02-24 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='nom',
        ),
        migrations.AddField(
            model_name='member',
            name='nomfamille',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='prenom',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
