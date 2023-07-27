# Generated by Django 4.2.3 on 2023-07-27 10:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0011_alter_level_level_number_alter_session_session_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="question",
            options={
                "ordering": ["-date_added"],
                "verbose_name": "question",
                "verbose_name_plural": "questions",
            },
        ),
        migrations.AlterModelOptions(
            name="session",
            options={
                "ordering": ["-date_created"],
                "verbose_name": "session",
                "verbose_name_plural": "sessions",
            },
        ),
        migrations.AlterField(
            model_name="session",
            name="session_id",
            field=models.CharField(
                editable=False, max_length=8, primary_key=True, serialize=False
            ),
        ),
    ]
