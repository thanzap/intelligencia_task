# Generated by Django 4.2.4 on 2023-09-02 17:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eoftermapp", "0011_remove_efoterm_parent_link"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="efoterm",
            name="parent",
        ),
        migrations.AddField(
            model_name="efoterm",
            name="parent",
            field=models.ManyToManyField(
                blank=True, related_name="children", to="eoftermapp.efoterm"
            ),
        ),
    ]
