# Generated by Django 5.0.1 on 2024-02-06 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0007_videos_course_description_delete_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videos',
            name='logo',
            field=models.ImageField(default='videos/static/medias/logo/default_image.png', upload_to='videos/static/medias/logo/'),
        ),

    ]
