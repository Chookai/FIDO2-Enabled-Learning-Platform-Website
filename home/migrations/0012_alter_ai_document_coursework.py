# Generated by Django 4.1.2 on 2023-03-28 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0011_alter_hdl_document_docfile_group_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ai_document",
            name="Coursework",
            field=models.ForeignKey(
                default="1",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ai_coursework",
                to="home.ai_coursework",
            ),
        ),
    ]