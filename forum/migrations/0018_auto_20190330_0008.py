# Generated by Django 2.1.7 on 2019-03-29 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0017_auto_20190329_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farmer',
            name='account_token',
            field=models.CharField(blank=True, default='4d9f77ff-b255-441d-9', max_length=20),
        ),
    ]
