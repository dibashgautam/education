# students/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from .models import Student

# Manual signup
@receiver(post_save, sender=User)
def create_student_for_user(sender, instance, created, **kwargs):
    if created:
        Student.objects.get_or_create(user=instance)

# Social login signup
@receiver(user_signed_up)
def create_student_on_google_login(request, user, **kwargs):
    # Prevent duplicate student profile
    if not hasattr(user, "student_profile"):
        Student.objects.create(user=user)
