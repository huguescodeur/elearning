# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import User, Apprenant, Formateur


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created and instance.role == 'apprenant':
#         Apprenant.objects.create(user=instance)
#     elif created and instance.role == 'formateur':
#         Formateur.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     if instance.role == 'apprenant':
#         try:
#             instance.apprenant.save()
#         except Apprenant.DoesNotExist:
#             pass
#     elif instance.role == 'formateur':
#         try:
#             instance.formateur.save()
#         except Formateur.DoesNotExist:
#             pass
