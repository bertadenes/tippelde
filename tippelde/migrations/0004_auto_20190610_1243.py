# Generated by Django 2.2.2 on 2019-06-10 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tippelde', '0003_auto_20190610_1035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='result',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Draw'), (1, 'Home'), (2, 'Away')], null=True),
        ),
    ]
