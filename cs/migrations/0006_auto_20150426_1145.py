# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cs', '0005_auto_20150426_0403'),
    ]

    operations = [
        migrations.AddField(
            model_name='encounter',
            name='player1expired',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='encounter',
            name='player2expired',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='player',
            name='authtoken',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='level',
            field=models.IntegerField(default=0),
        ),
    ]
