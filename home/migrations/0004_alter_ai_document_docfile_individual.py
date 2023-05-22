# Generated by Django 4.1.2 on 2023-03-05 03:34

from django.db import migrations, models
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0003_alter_ai_document_docfile_individual"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ai_document",
            name="docfile_individual",
            field=models.FileField(
                blank=True,
                default=None,
                null=True,
                upload_to=home.models.rename_uploaded_file,
            ),
        ),
    ]