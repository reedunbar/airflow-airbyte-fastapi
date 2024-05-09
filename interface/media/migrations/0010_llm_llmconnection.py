# Generated by Django 5.0.4 on 2024-05-07 02:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0009_youtubevideos'),
    ]

    operations = [
        migrations.CreateModel(
            name='LLM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='media.client')),
            ],
        ),
        migrations.CreateModel(
            name='LLMConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metadata', models.CharField(max_length=300)),
                ('client_connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='media.clientconnection')),
                ('llm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='media.llm')),
            ],
        ),
    ]