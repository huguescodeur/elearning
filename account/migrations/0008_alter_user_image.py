# Generated by Django 5.0.1 on 2024-03-23 09:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0007_alter_user_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="image",
            field=models.ImageField(
                default="account/static/images/user_profil/default_image.png",
                upload_to="account/static/images/user_profil/",
            ),
        ),
    ]