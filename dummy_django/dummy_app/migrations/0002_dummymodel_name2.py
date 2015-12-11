# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dummy_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dummymodel',
            name='name2',
            field=models.CharField(default=b'fuck', max_length=255),
        ),
    ]
