# Generated by Django 4.1.2 on 2023-03-05 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0002_ai_document_a"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ai_document",
            name="docfile_individual",
            field=models.FileField(
                blank=True, default=None, null=True, upload_to="AI_Folder_Individual"
            ),
        ),
    ]
