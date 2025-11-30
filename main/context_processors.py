from main.models import Institute

def approved_institute(request):
    user_student = getattr(request.user, 'student_profile', None)
    approved = None
    if user_student:
        institutes = Institute.objects.filter(owner=user_student, status='approved')
        approved = institutes.first() if institutes.exists() else None
    return {'approved_institute': approved}
