# students/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Admission, Enrollment, Student, Profile, Course
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from django.db.models.signals import pre_save



@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if created:
        Student.objects.get_or_create(user=instance)
        
        Profile.objects.get_or_create(
            user=instance,
            defaults={
                'full_name': instance.get_full_name() or instance.username,
            }
        )

# Social login signup
@receiver(user_signed_up)
def create_student_on_google_login(request, user, **kwargs):
    if not hasattr(user, "student_profile"):
        Student.objects.create(user=user)


# ----------------------------
# Admission accepted → Enrollment + seat decrement
# ----------------------------
@receiver(pre_save, sender=Admission)
def handle_admission_accept(sender, instance, **kwargs):
    if not instance.pk:
        return

    previous = Admission.objects.get(pk=instance.pk)

    if previous.status == "accepted" or instance.status != "accepted":
        return

    # Student check
    if not instance.user or not hasattr(instance.user, "student_profile"):
        return

    course = instance.course
    if not course:
        return

    with transaction.atomic():
        course_locked = Course.objects.select_for_update().get(id=course.id)

        # Create enrollment
        Enrollment.objects.create(
            student=instance.user.student_profile,
            course=course_locked,
            institute=instance.institute
        )

        # Decrease seat
        if course_locked.seats > 0:
            course_locked.seats -= 1
            course_locked.save()
