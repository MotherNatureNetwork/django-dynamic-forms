# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0006_auto_20150803_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='formmodel',
            name='display',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
