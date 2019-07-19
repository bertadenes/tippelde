# Generated by Django 2.2.3 on 2019-07-19 18:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tippelde', '0012_auto_20190719_1326'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumericQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due', models.DateTimeField()),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('award', models.PositiveSmallIntegerField(default=10)),
                ('changes', models.PositiveSmallIntegerField(default=0)),
                ('penalty', models.PositiveSmallIntegerField(default=3)),
                ('evaluated', models.BooleanField(default=False)),
                ('correct_answer', models.CharField(blank=True, max_length=200, null=True)),
                ('tournament', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tippelde.Tournament')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NumericAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed', models.PositiveSmallIntegerField(default=0)),
                ('answer', models.CharField(max_length=200)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tippelde.NumericQuestion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]