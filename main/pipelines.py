from main.models import Student

def create_student_profile(backend, user, response, *args, **kwargs):
    if not hasattr(user, 'student_profile'):
        Student.objects.create(user=user)
