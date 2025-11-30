from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from datetime import datetime
import uuid
import json

from .models import (
    Student, Profile, Institute, CourseCategory, Course,
    Admission, AdmissionDocument, StudentFeedback, Enrollment 

)
from .forms import (
    UserForm, ProfileForm, InstituteForm, CourseCategoryForm, CourseForm,
    AdmissionForm, StudentFeedbackForm
)
from .utils.pdf_generator import generate_pdf
from .utils.generate_qr import generate_qr


date = datetime.now()


# -----------------------------------
# Helper Functions
# -----------------------------------
def check_institute_approved(student):
    inst = Institute.objects.filter(owner=student).first()
    if inst and inst.status == "approved":
        return inst
    return None


# -----------------------------------
# Home Page & Feedback
# -----------------------------------
# @login_required
def home(request):
    # Courses
    courses = Course.objects.all().order_by('-id')
    for c in courses:
        c.final_price = c.original_price - (c.original_price * c.discount_percent / 100) if c.discount_percent else c.original_price

    # Categories - Unique by title
    all_categories = CourseCategory.objects.all().order_by('title')[:8]  # top 8
    seen_titles = set()
    categories = []
    for cat in all_categories:
        if cat.title not in seen_titles:
            seen_titles.add(cat.title)
            categories.append(cat)

    # Feedbacks
    feedbacks = StudentFeedback.objects.all().order_by('-created_at')

    if request.method == 'POST':
        form = StudentFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.save()
            return redirect('main:home')
    else:
        form = StudentFeedbackForm()

    feedbacks_json = json.dumps([
        {
            "name": fb.student.username,
            "role": "Student",
            "text": fb.feedback_text,
            "image": fb.student.profile.avatar.url if hasattr(fb.student, 'profile') and fb.student.profile.avatar else "/static/images/tesimg04.png"
        } for fb in feedbacks
    ], cls=DjangoJSONEncoder)

    return render(request, "main/students/home.html", {
        "courses": courses,
        "categories": categories,
        "feedbacks": feedbacks,
        "form": form,
        "feedbacks_json": feedbacks_json,
    })


# -----------------------------------
# Ajax Search
# -----------------------------------
import logging
logger = logging.getLogger(__name__)

def ajax_search(request):
    try:
        query = request.GET.get('q', '').strip()
        # print(f"Search query: {query}")  # Debug print
        
        if not query:
            return JsonResponse({'html': ''})
                
        categories = CourseCategory.objects.filter(title__icontains=query)[:5]
        courses = Course.objects.filter(title__icontains=query)[:5]
        institutes = Institute.objects.filter(name__icontains=query)[:5]
        
        print(f"Found: {categories.count()} categories, {courses.count()} courses, {institutes.count()} institutes")
        
        html = render_to_string('main/search_dropdown.html', {
            'categories': categories,
            'courses': courses,
            'institutes': institutes,
        })
        return JsonResponse({'html': html})
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return JsonResponse({'html': f'<div class="p-2 text-center text-danger">Server Error: {str(e)}</div>'})


# -----------------------------------
# Courses
# -----------------------------------
@login_required
def course(request):
    all_categories = CourseCategory.objects.all().order_by('title')
    categories = []
    seen_titles = set()
    for cat in all_categories:
        if cat.title not in seen_titles:
            seen_titles.add(cat.title)
            categories.append(cat)

    category_title = request.GET.get('category') 
    if category_title:
        courses = Course.objects.filter(category__title=category_title)
    else:
        courses = Course.objects.all()
    for c in courses:
        c.final_price = (
            c.original_price - (c.original_price * c.discount_percent / 100)
            if c.discount_percent else c.original_price
        )
    return render(request, 'main/students/course/course.html', {
        "categories": categories,
        "courses": courses,
        "selected_category": category_title,  
    })



def course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    discount_percent = course.discount_percent or 0
    final_price = course.original_price - (course.original_price * discount_percent / 100)
    return render(request, 'main/students/course/course_detail.html', {
        "course": course,
        "final_price": final_price,
        "discount_percent": discount_percent
    })


# -----------------------------------
# Profile Management
# -----------------------------------
@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name() or request.user.username
        }
    )

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save(commit=False)
            profile = profile_form.save(commit=False)
            full_name = request.POST.get('full_name')
            if full_name:
                profile.full_name = full_name

            avatar = request.FILES.get('avatar')
            if avatar:
                profile.avatar = avatar

            user_form.save()
            profile.save()
            

            update_session_auth_hash(request, request.user)

            messages.success(request, "Profile updated successfully!")
            return redirect('main:home') 

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'current_profile': profile,
    }

    return render(request, 'main/students/edit_profile.html', context)

# student profile

@login_required
def student_profile(request):

    profile = getattr(request.user, 'profile', None)

    if not hasattr(request.user, 'student_profile'):
        admissions = Admission.objects.filter(user=request.user).order_by('-created_at')
    else:
        admissions = Admission.objects.filter(
            user=request.user,
            course__in=Enrollment.objects.filter(
                student=request.user.student_profile
            ).values_list('course', flat=True)
        ).order_by('-created_at')

    return render(request, "main/students/student_profile.html", {
        "profile": profile,
        "admissions": admissions
    })



# -----------------------------------
# Authentication
# -----------------------------------

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        full_name = request.POST.get('full_name').strip()
        avatar = request.FILES.get('avatar')

        # -----------------------------
        # Validations
        # -----------------------------
        if not username or not email or not password or not password1 or not full_name:
            messages.error(request, "All fields are required.")
            return redirect('main:register')

        if password != password1:
            messages.error(request, "Passwords do not match.")
            return redirect('main:register')

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('main:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('main:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('main:register')

        # -----------------------------
        # Create User & Profile
        # -----------------------------
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = full_name  
            user.save()
            user.full_clean()

            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': full_name,
                    'avatar': avatar
                }
            )
            if not created:
                updated = False
            if avatar:
                profile.avatar = avatar
                updated = True
            if full_name and profile.full_name != full_name:
                profile.full_name = full_name
                updated = True
            if updated:
                profile.save()

            message = render_to_string('main/auth/msg.html', {'name': full_name, 'date': date.today()})
            send_mail('Education', message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)

            messages.success(request, "Account created successfully! Please login.")
            return redirect('main:login')

        except Exception as e:
            messages.error(request, f"Error during registration: {e}")
            return redirect('main:register')

    return render(request, 'main/auth/register.html')





def login_user(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username').strip()
        password = request.POST.get('password')

        if not username_or_email or not password:
            messages.error(request, "Both fields are required.")
            return redirect('main:login')

        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('main:home')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('main:login')

    return render(request, 'main/auth/login.html')



def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('main:login')


# -----------------------------------
# Institute Application & Dashboard
# -----------------------------------
@login_required
def apply_institute(request):
    student = getattr(request.user, 'student_profile', None)
    if not student:
        messages.error(request, "Student profile not found.")
        return redirect("main:home")

    institute = Institute.objects.filter(owner=student).first()
    if institute:
        if institute.status == "approved":
            return redirect("main:dashboard")
        elif institute.status == "pending":
            messages.warning(request, 'Your application is in pending wait 48 hour')
            return redirect('main:home')
        elif institute.status == "rejected":
            messages.warning(request, "Your previous application was rejected. Please reapply.")

    if request.method == "POST":
        form = InstituteForm(request.POST, request.FILES)
        if form.is_valid():
            new_inst = form.save(commit=False)
            new_inst.owner = student
            new_inst.status = "pending"
            new_inst.save()
            messages.success(request, "Application submitted successfully!")
            return redirect("main:dashboard")
        messages.error(request, "Please check all required fields.")
    else:
        form = InstituteForm()

    return render(request, "admin/custom_admin/apply_institute.html", {"form": form})

# -----------------------------------
# Institute Details
# -----------------------------------

from django.views.generic.detail import DetailView

class InstituteDetailView(DetailView):
    model = Institute
    template_name = "main/institute_detail.html"  
    context_object_name = "institute"


# -----------------------------------
# Dashboard
# -----------------------------------
@login_required
def dashboard(request, category_id=None):
    student = getattr(request.user, 'student_profile', None)
    if not student:
        messages.error(request, "Student profile not found.")
        return redirect("main:home")

    institutes = Institute.objects.filter(owner=student)
    approved = institutes.filter(status="approved").first()
    pending = institutes.filter(status="pending").first()
    rejected = institutes.filter(status="rejected").first()

    categories = CourseCategory.objects.filter(institute=approved) if approved else []
    if category_id:
        categories = categories.filter(id=category_id)

    enrolled = Admission.objects.filter(institute=approved, course__isnull=False) if approved else []

    return render(request, "admin/custom_admin/dashboard.html", {
        "approved_institute": approved,
        "pending_institute": pending,
        "rejected_institute": rejected,
        "categories": categories,
        "students": enrolled,
        "course_form": CourseForm(),
    })



# -----------------------------------
# Edit Institute
# -----------------------------------
@login_required
def edit_institute(request, institute_id):
    student = getattr(request.user, 'student_profile', None)
    if not student:
        messages.error(request, "Student profile not found.")
        return redirect("main:home")

    institute = get_object_or_404(Institute, id=institute_id, owner=student)

    if request.method == "POST":
        form = InstituteForm(request.POST, request.FILES, instance=institute)
        if form.is_valid():
            form.save()
            messages.success(request, "Institute updated successfully!")
            return redirect("main:dashboard")
        messages.error(request, "Please correct the errors below.")
    else:
        form = InstituteForm(instance=institute)

    return render(request, "admin/custom_admin/edit_institute.html", {"form": form, "institute": institute})

# -----------------------------------
# Remove Student From Course
# -----------------------------------
def remove_student_from_course(request, student_id):
    student = get_object_or_404(Admission, id=student_id)
    student.course = None
    student.save()

    messages.success(request, "Student removed from the enrolled course!")
    return redirect('main:dashboard')



# -----------------------------------
# Student Management
# -----------------------------------
@login_required
@login_required
def manage_student(request, admission_id):
    admission = get_object_or_404(Admission, id=admission_id)

    if request.method == "POST":
        action = request.POST.get("action")

        # SHORTLIST
        if action == "shortlist":
            admission.status = "shortlisted"
            admission.save()
            messages.success(request, "Student shortlisted successfully!")
            return redirect("main:dashboard")

        # ACCEPT + AUTO ENROLLMENT
        elif action == "accept":
            admission.status = "accepted"
            admission.save()
            if not hasattr(admission.user, 'student_profile'):
                messages.error(request, "Student profile is missing. Cannot enroll.")
                return redirect("main:dashboard")

            student_instance = admission.user.student_profile
            enrollment, created = Enrollment.objects.get_or_create(
                student=student_instance,
                course=admission.course,
                institute=admission.institute
            )

            if created:
                messages.success(request, "Student accepted and auto-enrolled successfully!")
            else:
                messages.info(request, "Student was already enrolled in this course.")

            return redirect("main:dashboard")
        # REJECT
        elif action == "reject":
            admission.status = "rejected"
            admission.save()
            messages.success(request, "Student rejected successfully!")
            return redirect("main:dashboard")

    courses = admission.course.institute.courses.all() if admission.course else []

    return render(request, "admin/custom_admin/student/manage_student.html", {
        "student": admission,
        "courses": courses,
    })

# -----------------------------------
# Accept Admission
# -----------------------------------
def accept_admission(request, admission_id):
    admission = get_object_or_404(Admission, id=admission_id)
    
    if request.user != admission.institute.owner.user:
        messages.error(request, "You are not authorized to approve this admission.")
        return redirect('main:institute_dashboard')

    admission.status = 'accepted'
    admission.save()

    Enrollment.objects.create(
        student=admission.user.student_profile,
        course=admission.course,
        institute=admission.institute
    )

    messages.success(request, f"Admission for {admission.student_name} accepted and enrollment created.")
    return redirect('main:institute_dashboard')

def reject_admission(request, admission_id):
    admission = get_object_or_404(Admission, id=admission_id)
    if request.user != admission.institute.owner.user:
        messages.error(request, "You are not authorized to reject this admission.")
        return redirect('main:institute_dashboard')

    admission.status = 'rejected'
    admission.save()
    messages.success(request, f"Admission for {admission.student_name} rejected.")
    return redirect('main:institute_dashboard')


# -----------------------------------
# CourseCategory CRUD
# -----------------------------------
@login_required
def add_category(request):
    student = getattr(request.user, 'student_profile', None)
    institute = check_institute_approved(student)
    if not institute:
        messages.warning(request, "Your institute is not approved yet.")
        return redirect("main:dashboard")

    if request.method == "POST":
        form = CourseCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.institute = institute
            category.save()
            messages.success(request, "Category added successfully!")
            return redirect("main:dashboard")
    else:
        form = CourseCategoryForm()

    return render(request, "admin/custom_admin/category/add_category.html", {"form": form})

# category list
@login_required
def category_list(request):
    student = getattr(request.user, 'student_profile', None)
    institute = check_institute_approved(student)
    if not institute:
        messages.warning(request, "Your institute is not approved yet.")
        return redirect("main:dashboard")

    categories = CourseCategory.objects.filter(institute=institute)
    return render(request, "admin/custom_admin/category/category_list.html", {"categories": categories})

# single category
def category_list_stu(request, pk=None):
    if pk:
        category = get_object_or_404(CourseCategory, id=pk)
        courses = Course.objects.filter(category=category)
        return render(request, "admin/custom_admin/category/category_detail.html", {
            'category': category,
            'courses': courses
        })
    else:
        # List all categories
        categories = CourseCategory.objects.all()
        return render(request, "admin/custom_admin/category/category_list.html", {
            'categories': categories
        })

# edit category
@login_required
def edit_category(request, category_id):
    student = getattr(request.user, 'student_profile', None)
    institute = check_institute_approved(student)
    category = get_object_or_404(CourseCategory, id=category_id, institute=institute)

    if request.method == "POST":
        form = CourseCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect("main:category_list")
    else:
        form = CourseCategoryForm(instance=category)

    return render(request, "admin/custom_admin/category/edit_category.html", {"form": form, "category": category})

# delete category
@login_required
def delete_category(request, category_id):
    student = getattr(request.user, 'student_profile', None)
    institute = check_institute_approved(student)
    category = get_object_or_404(CourseCategory, id=category_id, institute=institute)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect("main:dashboard")


# -----------------------------------
# Course CRUD
# -----------------------------------
@login_required
def add_course(request, category_id=None):
    student = getattr(request.user, 'student_profile', None)
    institute = check_institute_approved(student)
    categories = CourseCategory.objects.filter(institute=institute)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.institute = institute
            cat_id = request.POST.get('category')
            if cat_id:
                course.category = get_object_or_404(CourseCategory, id=cat_id, institute=institute)
            course.save()
            messages.success(request, "Course added successfully!")
            return redirect("main:course_list", category_id=course.category.id)
    else:
        form = CourseForm()
        form.fields['category'].queryset = categories
        if category_id:
            form.initial['category'] = category_id

    return render(request, "admin/custom_admin/course/add_course.html", {"form": form, "categories": categories, "selected_category_id": category_id})

# course list
@login_required
def course_list(request, category_id):
    student = getattr(request.user, 'student_profile', None)
    institute = check_institute_approved(student)
    category = get_object_or_404(CourseCategory, id=category_id, institute=institute)
    courses = Course.objects.filter(category=category)
    return render(request, "admin/custom_admin/course/course_list.html", {"courses": courses, "category": category})

# course view
@login_required
def view_course(request, course_id):
    student = getattr(request.user, 'student_profile', None)
    institute = check_institute_approved(student)
    course = get_object_or_404(Course, id=course_id, institute=institute)
    return render(request, "admin/custom_admin/course/course_detail.html", {"course": course})

# edit course
@login_required
def edit_course(request, course_id):
    student = getattr(request.user, 'student_profile', None)
    institute = check_institute_approved(student)
    course = get_object_or_404(Course, id=course_id, institute=institute)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
        return redirect("main:course_list", category_id=course.category.id)
    else:
        form = CourseForm(instance=course)

    return render(request, "admin/custom_admin/course/edit_course.html", {"form": form, "course": course})

# delete course
@login_required
def delete_course(request, course_id):
    student = getattr(request.user, 'student_profile', None)
    institute = check_institute_approved(student)
    course = get_object_or_404(Course, id=course_id, institute=institute)
    course.delete()
    messages.success(request, "Course deleted successfully!")
    return redirect("main:dashboard")


# -----------------------------------
# Payments
# -----------------------------------
@login_required
def esewa_payment(request, admission_id):
    admission = get_object_or_404(Admission, id=admission_id)
    admission.is_paid = True
    admission.esewa_ref_id = "MOCK12345"
    admission.save()
    return redirect("main:esewa_success", admission_id=admission.id)


@login_required
def esewa_success_mock(request, admission_id):
    admission = get_object_or_404(Admission, id=admission_id)
    admission.is_paid = True
    admission.esewa_ref_id = "MOCK_REF_12345"
    admission.save()
    return render(request, "main/students/esewa_result.html", {"status": "success", "message": "Payment simulated successfully (mock).", "admission": admission, "ref_id": admission.esewa_ref_id})


@login_required
def esewa_fail_mock(request, admission_id):
    admission = get_object_or_404(Admission, id=admission_id)
    return render(request, "main/students/esewa_result.html", {"status": "cancelled", "admission": admission})


@login_required
def payment_page(request, admission_id):
    admission = get_object_or_404(Admission, id=admission_id)
    return render(request, "main/students/payment.html", {"admission": admission})


# -----------------------------------
# Admission Form
# -----------------------------------
@login_required
def admission_form(request):
    course_id = request.GET.get("course_id")
    profile = getattr(request.user, 'profile', None)
    selected_course = None
    initial = {
        "student_name": request.user.get_full_name() or request.user.username,
        "email": request.user.email,
        "phone": profile.phone if profile else "",
        "address": profile.address if profile else "",
        "dob": profile.date_of_birth if profile else "",
    }

    if course_id:
        selected_course = get_object_or_404(Course, id=course_id)
        initial.update({"course": selected_course.id, "category": selected_course.category.id, "institute": selected_course.category.institute.id})

    if request.method == "POST":
        form = AdmissionForm(request.POST)
        if form.is_valid():
            admission = form.save(commit=False)
            admission.user = request.user

            course = admission.course
            discount = (course.original_price * course.discount_percent) / 100
            admission.amount = course.original_price - discount
            admission.esewa_pid = str(uuid.uuid4())
            admission.save()

            for doc_type in ["photo", "marksheet", "id_card"]:
                if request.FILES.get(doc_type):
                    AdmissionDocument.objects.create(admission=admission, file=request.FILES[doc_type], doc_type=doc_type)

            return redirect("main:esewa_payment", admission_id=admission.id)
    else:
        form = AdmissionForm(initial=initial)

    return render(request, "main/students/admission_form.html", {"form": form, "selected_course": selected_course})


# -----------------------------------
# Offer Letter
# -----------------------------------

@login_required
def download_offer_letter(request, admission_id):
    import os
    import base64
    import qrcode
    from io import BytesIO
    from django.conf import settings
    from django.template.loader import render_to_string
    from django.http import HttpResponse
    from xhtml2pdf import pisa
    from django.shortcuts import get_object_or_404
    from .models import Admission, Enrollment, Institute

    admission = get_object_or_404(Admission, id=admission_id)

    if request.user != admission.user:
        return HttpResponse("Access denied.")

    try:
        enrollment = Enrollment.objects.get(
            student=admission.user.student_profile,
            course=admission.course
        )
    except Enrollment.DoesNotExist:
        return HttpResponse("Enrollment not found.")

    institute = Institute.objects.get(id=enrollment.institute.id)

    if institute.status != "approved":
        return HttpResponse("Offer letter not available.")

    def image_to_base64(image_field):
        if image_field and hasattr(image_field, 'path') and os.path.exists(image_field.path):
            try:
                with open(image_field.path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')
            except Exception as e:
                print(f"Error converting image to base64: {e}")
                return None
        else:
            print(f"Image field is empty or file doesn't exist: {image_field}")
            return None

    qr_buffer = BytesIO()
    qrcode.make(f"ADMISSION VERIFIED: {admission.id}").save(qr_buffer, format='PNG')
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')

    signature_base64 = image_to_base64(institute.signature)
    stamp_base64 = image_to_base64(institute.stamp)
    logo_base64 = image_to_base64(institute.profile_logo)
    
    student_photo_base64 = None
    if admission.user and hasattr(admission.user, 'profile') and admission.user.profile.avatar:
        student_photo_base64 = image_to_base64(admission.user.profile.avatar)

    student_full_name = admission.user.get_full_name() if admission.user else admission.student_name

    context = {
        "admission": admission,
        "course": admission.course,
        "institute": institute,
        "student_name": student_full_name,
        "qr_base64": qr_base64,
        "signature_base64": signature_base64,
        "stamp_base64": stamp_base64,
        "logo_base64": logo_base64,
        "student_photo_base64": student_photo_base64,
    }

    html = render_to_string("main/offer_letter.html", context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Offer_Letter_{admission.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('PDF generation error')
    return response





# -----------------------------------
# Dynamic AJAX Loading
# -----------------------------------
def load_categories(request):
    institute_id = request.GET.get("institute_id")
    categories = CourseCategory.objects.filter(institute_id=institute_id)
    return JsonResponse(list(categories.values("id", "title")), safe=False)


def load_courses(request):
    category_id = request.GET.get("category_id")
    courses = Course.objects.filter(category_id=category_id)
    data = [{"id": c.id, "title": c.title, "original_price": float(c.original_price), "discount_percent": c.discount_percent} for c in courses]
    return JsonResponse(data, safe=False)
