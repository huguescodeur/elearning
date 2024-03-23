from django.utils import timezone
from django.db import models
from django.utils.text import slugify
from account.models import User


class Videos(models.Model):
    CATEGORY_CHOICES = [
        ('formation', 'Formation'),
        ('tutoriel', 'Tutoriel'),
    ]

    ACCESS_CHOICES = [
        ('gratuit', 'Gratuit'),
        ('premium', 'Premium'),
    ]

    course = models.CharField(max_length=255, default="Lesson")
    course_description = models.CharField(max_length=255, default="Description")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    # video_file = models.FileField(upload_to='videos/static/medias/videos/')
    youtube_video_id = models.CharField(max_length=255, blank=True, null=True)
    logo_url = models.CharField(
        max_length=50,
        default='videos/static/medias/logo/python.png')
    miniature = models.ImageField(
        upload_to='videos/static/medias/miniatures/',
        default='videos/static/medias/miniatures/default_image.png')
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    access = models.CharField(max_length=20, choices=ACCESS_CHOICES)
    duration = models.DurationField()
    date = models.DateTimeField(default=timezone.now)
    niveau = models.CharField(max_length=30, default="debutant")
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
