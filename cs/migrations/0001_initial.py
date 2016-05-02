# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Battle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('level', models.IntegerField()),
                ('visibletests', models.TextField()),
                ('invisibletests', models.TextField()),
            ],
            options={
                'verbose_name': 'Battle',
                'verbose_name_plural': 'Battles',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Encounter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField()),
                ('player1notified', models.DateTimeField(null=True, blank=True)),
                ('player2notified', models.DateTimeField(null=True, blank=True)),
                ('submission1', models.TextField(null=True, blank=True)),
                ('submission2', models.TextField(null=True, blank=True)),
                ('submission1created', models.DateTimeField(null=True, blank=True)),
                ('submission2created', models.DateTimeField(null=True, blank=True)),
                ('passedtests1', models.BooleanField(default=False)),
                ('passedtests2', models.BooleanField(default=False)),
                ('pointsawarded', models.IntegerField(default=0)),
                ('closed', models.BooleanField(default=False)),
                ('battle', models.ForeignKey(to='cs.Battle')),
            ],
            options={
                'verbose_name': 'Encounter',
                'verbose_name_plural': 'Encounters',
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('subscribedate', models.DateField()),
                ('playing', models.BooleanField(default=True)),
                ('score', models.IntegerField(default=0)),
                ('level', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Player',
                'verbose_name_plural': 'Player',
            },
        ),
        migrations.AddField(
            model_name='encounter',
            name='player1',
            field=models.ForeignKey(related_name='player1', blank=True, to='cs.Player', null=True),
        ),
        migrations.AddField(
            model_name='encounter',
            name='player2',
            field=models.ForeignKey(related_name='player2', blank=True, to='cs.Player', null=True),
        ),
        migrations.AddField(
            model_name='encounter',
            name='winner',
            field=models.ForeignKey(related_name='winner', blank=True, to='cs.Player', null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='category',
            field=models.ForeignKey(to='cs.Category'),
        ),
    ]
