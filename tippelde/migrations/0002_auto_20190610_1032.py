# Generated by Django 2.2.2 on 2019-06-10 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tippelde', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bet',
            name='value',
            field=models.SmallIntegerField(choices=[(0, 'Draw'), (1, 'Home'), (2, 'Away')], default=0),
        ),
    ]