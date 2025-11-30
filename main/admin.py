from django.contrib import admin
from .models import (
    Student, Profile, Institute, CourseCategory, Course,
    Admission, AdmissionDocument, StudentFeedback
)

# Register your models here.


# -----------------------------
# Student
# -----------------------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')


# -----------------------------
# Profile
# -----------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone')
    search_fields = ('user__username', 'full_name', 'user__email')


# -----------------------------
# Institute
# -----------------------------
@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'owner__user__username', 'email')


# -----------------------------
# CourseCategory
# -----------------------------
@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'institute')
    search_fields = ('title', 'institute__name')


# -----------------------------
# Course
# -----------------------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'institute', 'category', 'level', 'class_type', 'original_price', 'discount_percent', 'discount_price')
    list_filter = ('level', 'class_type')
    search_fields = ('title', 'institute__name', 'category__title')


# -----------------------------
# Admission
# -----------------------------
@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'email', 'course', 'institute', 'status', 'is_paid', 'amount', 'created_at')
    list_filter = ('status', 'is_paid', 'institute')
    search_fields = ('student_name', 'email', 'course__title', 'institute__name')


# -----------------------------
# AdmissionDocument
# -----------------------------
@admin.register(AdmissionDocument)
class AdmissionDocumentAdmin(admin.ModelAdmin):
    list_display = ('admission', 'doc_type', 'file')
    search_fields = ('admission__student_name', 'doc_type')


# -----------------------------
# StudentFeedback
# -----------------------------
@admin.register(StudentFeedback)
class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'feedback_text', 'created_at')
    search_fields = ('student__username', 'feedback_text')
