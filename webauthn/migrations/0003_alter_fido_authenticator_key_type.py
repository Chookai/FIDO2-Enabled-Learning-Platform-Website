# Generated by Django 4.1.2 on 2023-04-16 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webauthn", "0002_fido_authenticator"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fido_authenticator",
            name="key_type",
            field=models.CharField(default="FIDO", max_length=25),
        ),
    ]
