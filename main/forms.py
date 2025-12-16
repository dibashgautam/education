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
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


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
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    CLASS_TYPE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('both', 'Online + Offline'),
    ]

    level = forms.ChoiceField(choices=LEVEL_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    class_type = forms.ChoiceField(choices=CLASS_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Course
        fields = [
            "title", "description", "image", "duration",
            "level", "class_type", "seats", "original_price", "discount_percent"
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control','placeholder': 'Enter course title'}),
            'description': forms.Textarea(attrs={'class':'form-control','placeholder': 'Write course description...'}),
            'image': forms.ClearableFileInput(attrs={'class':'form-control'}),
            'duration': forms.TextInput(attrs={'class':'form-control','placeholder': 'e.g., 3 months'}),
            'seats': forms.NumberInput(attrs={'class':'form-control','placeholder': 'Number of seats'}),
            'original_price': forms.NumberInput(attrs={'class':'form-control','placeholder': 'Original price'}),
            'discount_percent': forms.NumberInput(attrs={'class':'form-control','placeholder': 'Discount %'}),
        }

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
