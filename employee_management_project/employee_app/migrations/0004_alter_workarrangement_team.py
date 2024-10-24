# Generated by Django 5.1.2 on 2024-10-24 04:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee_app', '0003_workarrangement_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workarrangement',
            name='team',
            field=models.ForeignKey(default=7, on_delete=django.db.models.deletion.PROTECT, related_name='work_arrangements', to='employee_app.team'),
        ),
    ]
