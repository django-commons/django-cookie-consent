# Generated by Django 4.2.13 on 2024-05-09 19:01

import re

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cookie_consent", "0002_auto__add_logitem"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cookiegroup",
            name="varname",
            field=models.CharField(
                max_length=32,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[-_a-zA-Z0-9]+$"),
                        "Enter a valid 'varname' consisting of letters, numbers, "
                        "underscores or hyphens.",
                        "invalid",
                    )
                ],
                verbose_name="Variable name",
            ),
        ),
    ]
