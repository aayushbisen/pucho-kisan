# Generated by Django 2.1.7 on 2019-03-20 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0013_auto_20190320_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farmer',
            name='phone_number',
            field=models.CharField(max_length=20, unique=True, verbose_name='फ़ोन नंबर'),
        ),
    ]
