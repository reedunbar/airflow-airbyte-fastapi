# Generated by Django 5.0.4 on 2024-05-01 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0003_remove_wordpressconnection_connection_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
