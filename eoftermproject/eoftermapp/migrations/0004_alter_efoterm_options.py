# Generated by Django 4.2.4 on 2023-09-02 16:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("eoftermapp", "0003_alter_efoterm_table"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="efoterm",
            options={"verbose_name": "EFO Term", "verbose_name_plural": "EFO Terms"},
        ),
    ]