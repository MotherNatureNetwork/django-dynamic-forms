# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0005_auto_increase_form_label_max_length_255'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='formmodel',
            name='submit_url',
        ),
        migrations.RemoveField(
            model_name='formmodel',
            name='success_template',
        ),
        migrations.RemoveField(
            model_name='formmodel',
            name='success_url',
        ),
    ]
