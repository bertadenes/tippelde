# Generated by Django 2.2.3 on 2019-07-27 20:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tippelde', '0018_auto_20190727_1856'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='numericquestion',
            name='tournament',
        ),
        migrations.DeleteModel(
            name='NumericAnswer',
        ),
        migrations.DeleteModel(
            name='NumericQuestion',
        ),
    ]
