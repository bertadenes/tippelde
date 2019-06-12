# Generated by Django 2.2.2 on 2019-06-12 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tippelde', '0004_auto_20190610_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='award',
            field=models.PositiveSmallIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='game',
            name='changed',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='game',
            name='description',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='due',
            field=models.DateTimeField(default='2099-01-01 00:00:00'),
        ),
        migrations.AddField(
            model_name='game',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='penalty',
            field=models.PositiveSmallIntegerField(default=3),
        ),
    ]
