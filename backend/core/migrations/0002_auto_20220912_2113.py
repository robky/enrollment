# Generated by Django 3.2.15 on 2022-09-12 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filesystem",
            name="id",
            field=models.CharField(
                max_length=20, primary_key=True, serialize=False, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="filesystem",
            name="size",
            field=models.IntegerField(default=0),
        ),
    ]