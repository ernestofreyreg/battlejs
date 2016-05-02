# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cs', '0004_auto_20150426_0236'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='maxtime',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='authtoken',
            field=models.CharField(default=b'079c677562474b53b726298ab999e31d', max_length=100, null=True, blank=True),
        ),
    ]
