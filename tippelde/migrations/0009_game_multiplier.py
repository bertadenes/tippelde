# Generated by Django 2.2.3 on 2019-07-18 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tippelde', '0008_auto_20190715_2140'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='multiplier',
            field=models.SmallIntegerField(default=1),
        ),
    ]
