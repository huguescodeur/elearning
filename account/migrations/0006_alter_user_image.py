# Generated by Django 5.0.1 on 2024-03-23 09:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0005_guestcontact"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="image",
            field=models.ImageField(
                default="user_profil/default_image.png", upload_to="user_profil/"
            ),
        ),
    ]
