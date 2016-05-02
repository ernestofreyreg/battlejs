# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cs', '0002_remove_player_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='authtoken',
            field=models.CharField(default=b'ac2f68a1cc364b61b2d272f8c1cd987b', max_length=100, null=True, blank=True),
        ),
    ]
