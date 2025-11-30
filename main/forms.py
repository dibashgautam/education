from django import forms
from django.contrib.auth.models import User
from .models import (
    Profile, Admission, AdmissionDocument, StudentFeedback,
    Institute, CourseCategory, Course
)

# -----------------------------
# 1) User & Profile Forms
# -----------------------------
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "avatar", "date_of_birth", "phone", "address"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"})
        }


# -----------------------------
# 2) Institute & Courses Forms
# -----------------------------
class InstituteForm(forms.ModelForm):
    class Meta:
        model = Institute
        fields = [
            "name", "description", "estd", "email", "phone", "website",
            "address", "profile_logo", "background_image", "signature",
            "stamp", "register_number", "register_image"
        ]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["profile_logo"].required = False
            self.fields["background_image"].required = False
            self.fields["signature"].required = False
            self.fields["stamp"].required = False
            self.fields["register_image"].required = False


class CourseCategoryForm(forms.ModelForm):
    class Meta:
        model = CourseCategory
        fields = ["title", "description", "image"]

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if title:
            return title.capitalize()  
        return title


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title", "description", "image", "category", "duration",
            "level", "class_type", "seats", "original_price", "discount_percent"
        ]


# -----------------------------
# 3) Admission Form
# -----------------------------
class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = [
            "student_name", "email", "phone", "address", "dob", "gender",
            "institute", "category", "course"
        ]
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"})
        }


# -----------------------------
# 4) Admission Documents Form
# -----------------------------
class AdmissionDocumentForm(forms.ModelForm):
    class Meta:
        model = AdmissionDocument
        fields = ["file", "doc_type"]


# -----------------------------
# 5) Student Feedback Form
# -----------------------------
class StudentFeedbackForm(forms.ModelForm):
    class Meta:
        model = StudentFeedback
        fields = ["feedback_text"]
        widgets = {
            "feedback_text": forms.Textarea(attrs={"rows": 3, "placeholder": "Write your feedback..."})
        }
