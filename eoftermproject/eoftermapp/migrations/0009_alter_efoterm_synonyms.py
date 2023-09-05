# Generated by Django 4.2.4 on 2023-09-02 16:46

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eoftermapp", "0008_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="efoterm",
            name="synonyms",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=1000),
                blank=True,
                null=True,
                size=None,
            ),
        ),
    ]
