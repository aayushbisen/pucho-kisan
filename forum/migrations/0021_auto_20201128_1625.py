# Generated by Django 2.2.13 on 2020-11-28 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0020_auto_20190613_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farmer',
            name='account_token',
            field=models.CharField(blank=True, default='e0e996bf-1efe-42b4-9', max_length=20),
        ),
    ]
