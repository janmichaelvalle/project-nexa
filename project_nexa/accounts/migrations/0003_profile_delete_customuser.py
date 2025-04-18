# Generated by Django 5.1.7 on 2025-04-09 03:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_customuser_options_alter_customuser_managers_and_more'),
        ('analytics', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_game_name', models.CharField(max_length=100, unique=True)),
                ('polaris_id', models.CharField(max_length=50, unique=True)),
                ('region', models.CharField(blank=True, max_length=50, null=True)),
                ('rank', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.rank')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
