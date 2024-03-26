from django.utils import timezone
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.db import models

# Create your models here.


# ? Class User étendue
class User(AbstractUser):
    ROLE_CHOICES = [
        ('apprenant', 'Apprenant'),
        ('formateur', 'Formateur'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    nom = models.CharField(max_length=50)
    image = models.ImageField(upload_to='static/user_image/', default='static/user_image/default_image.png')


    groups = models.ManyToManyField(
        Group, verbose_name='groups', blank=True, related_name='user_groups')
    user_permissions = models.ManyToManyField(
        Permission, verbose_name='user permissions', blank=True, related_name='user_permissions')
    
        


# ? Class Apprenant
class Apprenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom_apprenant = models.CharField(max_length=50)
    is_premium = models.BooleanField(default=False)


# ? Class Formateur
class Formateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom_formateur = models.CharField(max_length=50)


# ? Class Message User
class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    date = models.DateTimeField(default=timezone.now)


# ? Class Message non User
class GuestContact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    date = models.DateTimeField(default=timezone.now)
