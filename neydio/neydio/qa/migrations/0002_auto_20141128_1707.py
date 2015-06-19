# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='parent',
            field=models.ForeignKey(blank=True, to='qa.Entry', null=True),
            preserve_default=True,
        ),
    ]
