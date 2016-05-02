# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cs', '0003_player_authtoken'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='player',
            options={'verbose_name': 'Player', 'verbose_name_plural': 'Players'},
        ),
        migrations.AddField(
            model_name='encounter',
            name='submission1testtime',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='encounter',
            name='submission2testtime',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='authtoken',
            field=models.CharField(default=b'854d315fe0c244bcabbcadfcc33444e7', max_length=100, null=True, blank=True),
        ),
    ]
