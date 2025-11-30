from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


from django.conf import settings
from django.conf.urls.static import static

app_name = "main"

urlpatterns = [
    # -----------------------------
    # Home & Search
    # -----------------------------
    path("", views.home, name="home"),
    path('ajax-search/', views.ajax_search, name='ajax_search'),

    # -----------------------------
    # Courses
    # -----------------------------
    path('courses/', views.course, name='course'),
    path("courses/", views.course, name="course_list"),
    path("courses/<int:id>/", views.course_detail, name="course_detail"),

    # -----------------------------
    # Profile
    # -----------------------------
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("student/profile/", views.student_profile, name="student_profile"),


    # -----------------------------
    # Authentication
    # -----------------------------
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    # Password reset views
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='main/auth/password_reset.html'), 
         name='password_reset'),

    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='main/auth/password_reset_done.html'), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
     auth_views.PasswordResetConfirmView.as_view(template_name='main/auth/password_reset_confirm.html', success_url=reverse_lazy('main:password_reset_complete') ), 
     name='password_reset_confirm'),


    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='main/auth/password_reset_complete.html'), 
         name='password_reset_complete'),

    # -----------------------------
    # Institute Application & Dashboard
    # -----------------------------
    path("institute/apply/", views.apply_institute, name="apply_institute"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('dashboard/<int:category_id>/', views.dashboard, name='dashboard'),

    path("institute/edit/<int:institute_id>/", views.edit_institute, name="edit_institute"),
    path('institute/<int:pk>/', views.InstituteDetailView.as_view(), name='institute_detail'),

    path('remove-student/<int:student_id>/', views.remove_student_from_course, name='remove_student_from_course'),



    # -----------------------------
    # Student Management
    # -----------------------------
    path("student/manage/<int:admission_id>/", views.manage_student, name="manage_student"),

    # -----------------------------
    # CourseCategory CRUD
    # -----------------------------
    path("category/add/", views.add_category, name="add_category"),
    path("category/list/", views.category_list, name="category_list"),
    path("category/<int:pk>/", views.category_list_stu, name="category_list"),

    path("category/edit/<int:category_id>/", views.edit_category, name="edit_category"),
    path("category/delete/<int:category_id>/", views.delete_category, name="delete_category"),

    # -----------------------------
    # Course CRUD
    # -----------------------------
    path("course/add/", views.add_course, name="add_course"),
    path("course/add/<int:category_id>/", views.add_course, name="add_course_by_category"),
    path("course/list/<int:category_id>/", views.course_list, name="course_list"),
    path("course/view/<int:course_id>/", views.view_course, name="view_course"),
    path("course/edit/<int:course_id>/", views.edit_course, name="edit_course"),
    path("course/delete/<int:course_id>/", views.delete_course, name="delete_course"),

    # -----------------------------
    # Payments (Mock eSewa)
    # -----------------------------
    path("payment/<int:admission_id>/", views.payment_page, name="payment_page"),
    path("esewa/<int:admission_id>/pay/", views.esewa_payment, name="esewa_payment"),
    path("esewa/<int:admission_id>/success/", views.esewa_success_mock, name="esewa_success"),
    path("esewa/<int:admission_id>/fail/", views.esewa_fail_mock, name="esewa_fail"),

    # -----------------------------
    # Admission Form
    # -----------------------------
    path("admission/form/", views.admission_form, name="admission_form"),


    # -----------------------------
    # Offer Letter PDF
    # -----------------------------
    path("admission/<int:admission_id>/offer-letter/download/", views.download_offer_letter, name="download_offer_letter"),

    # -----------------------------
    # AJAX Dynamic Loading
    # -----------------------------
    path("ajax/load-categories/", views.load_categories, name="ajax_load_categories"),
    path("ajax/load-courses/", views.load_courses, name="ajax_load_courses"),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
