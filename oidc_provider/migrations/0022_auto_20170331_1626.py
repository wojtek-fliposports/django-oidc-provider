# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-31 16:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oidc_provider', '0021_refresh_token_not_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='require_consent',
            field=models.BooleanField(
                default=True,
                help_text='If disabled, the Server will NEVER ask the user for consent.',
                verbose_name='Require Consent?'),
        ),
        migrations.AddField(
            model_name='client',
            name='reuse_consent',
            field=models.BooleanField(
                default=True,
                help_text="If enabled, the Server will save the user consent given to a specific client,"
                          " so that user won't be prompted for the same authorization multiple times.",
                verbose_name='Reuse Consent?'),
        ),
    ]
