# Generated by Django 2.2.3 on 2019-07-27 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tippelde', '0016_score_double_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='matchday',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]