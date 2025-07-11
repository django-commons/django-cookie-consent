# Generated by Django 2.1 on 2019-02-08 14:14

import re

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cookie",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250, verbose_name="Name")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "path",
                    models.TextField(blank=True, default="/", verbose_name="Path"),
                ),
                (
                    "domain",
                    models.CharField(blank=True, max_length=250, verbose_name="Domain"),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created"),
                ),
            ],
            options={
                "verbose_name": "Cookie",
                "verbose_name_plural": "Cookies",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="CookieGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "varname",
                    models.CharField(
                        max_length=32,
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile("^[-_a-zA-Z0-9]+$"),
                                "Enter a valid 'varname' consisting of letters, "
                                "numbers, underscores or hyphens.",
                                "invalid",
                            )
                        ],
                        verbose_name="Variable name",
                    ),
                ),
                (
                    "name",
                    models.CharField(blank=True, max_length=100, verbose_name="Name"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "is_required",
                    models.BooleanField(
                        default=False,
                        help_text="Are cookies in this group required.",
                        verbose_name="Is required",
                    ),
                ),
                (
                    "is_deletable",
                    models.BooleanField(
                        default=True,
                        help_text="Can cookies in this group be deleted.",
                        verbose_name="Is deletable?",
                    ),
                ),
                ("ordering", models.IntegerField(default=0, verbose_name="Ordering")),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created"),
                ),
            ],
            options={
                "verbose_name": "Cookie Group",
                "verbose_name_plural": "Cookie Groups",
                "ordering": ["ordering"],
            },
        ),
        migrations.AddField(
            model_name="cookie",
            name="cookiegroup",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cookie_consent.CookieGroup",
                verbose_name="Cookie Group",
            ),
        ),
    ]
