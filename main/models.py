from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# -----------------------------
# 1) Student Model
# -----------------------------
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')

    def __str__(self):
        return self.user.username


# -----------------------------
# 2) Profile Model
# -----------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, )
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


# -----------------------------
# 3) Institute Model
# -----------------------------
class Institute(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    owner = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='institutes')
    name = models.CharField(max_length=200)
    description = models.TextField()
    estd = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    profile_logo = models.ImageField(upload_to='institute/logo/')
    background_image = models.ImageField(upload_to='institute/background/')
    signature = models.ImageField(upload_to='institute/signature/', blank=True, null=True)
    stamp = models.ImageField(upload_to='institute/stamp/', blank=True, null=True)
    register_number = models.CharField(max_length=100)
    register_image = models.ImageField(upload_to='institute/register_docs/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    admin_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# -----------------------------
# 4) CourseCategory Model
# -----------------------------
class CourseCategory(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="categories")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category/images/')

    def __str__(self):
        return f"{self.title} - {self.institute.name}"


# -----------------------------
# 5) Course Model
# -----------------------------
class Course(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="courses")
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='course/images/')
    duration = models.CharField(max_length=100)
    level = models.CharField(
        max_length=50,
        choices=[("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")]
    )
    class_type = models.CharField(
        max_length=20,
        choices=[("online", "Online"), ("offline", "Offline"), ("both", "Online + Offline")]
    )
    seats = models.PositiveIntegerField(default=0)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.discount_percent > 0:
            discount_amount = (self.original_price * self.discount_percent) / 100
            self.discount_price = self.original_price - discount_amount
        else:
            self.discount_price = self.original_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.institute.name})"


# -----------------------------
# 6) Admission Model
# -----------------------------
class Admission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # personal details
    student_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=20,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        null=True,
        blank=True
    )

    # course info
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    # admission status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # payment fields
    is_paid = models.BooleanField(default=False)
    esewa_pid = models.CharField(max_length=200, null=True, blank=True)
    esewa_ref_id = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.course.title}"


# -----------------------------
# 7) AdmissionDocument Model
# -----------------------------
class AdmissionDocument(models.Model):
    admission = models.ForeignKey(
        Admission, on_delete=models.CASCADE, related_name="documents"
    )
    file = models.FileField(upload_to="admission_docs/")
    doc_type = models.CharField(
        max_length=50,
        choices=[('photo', 'Photo'), ('marksheet', 'Marksheet'), ('id_card', 'ID Card'), ('other', 'Other')]
    )

    def __str__(self):
        return f"{self.doc_type} - {self.admission.student_name}"
    

# -----------------------------------
# Enrollment
# -----------------------------------
from django.db.models.signals import post_save
from django.dispatch import receiver

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.course}"

# -----------------------------------
# Signal to auto-create Enrollment when Admission is accepted
# -----------------------------------
@receiver(post_save, sender=Admission)
def create_enrollment_on_approval(sender, instance, created, **kwargs):
    if not instance.user:
        return
    if not hasattr(instance.user, "student_profile"):
        return
    if instance.status == "accepted":
        student = instance.user.student_profile
        course = instance.course
        institute = instance.institute
        if not Enrollment.objects.filter(student=student, course=course).exists():
            Enrollment.objects.create(
                student=student,
                course=course,
                institute=institute
            )



# -----------------------------
# 8) StudentFeedback Model
# -----------------------------
class StudentFeedback(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} Feedback"


# -----------------------------
# 9) Signals to auto-create Profile
# -----------------------------
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
