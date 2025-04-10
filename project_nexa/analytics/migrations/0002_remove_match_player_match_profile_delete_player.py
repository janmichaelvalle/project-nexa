# Generated by Django 4.2.20 on 2025-04-10 02:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_profile_region'),
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='player',
        ),
        migrations.AddField(
            model_name='match',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.profile'),
        ),
        migrations.DeleteModel(
            name='Player',
        ),
    ]
