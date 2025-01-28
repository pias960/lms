from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name 


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    image = models.ImageField(upload_to='course_images/')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='courses'
    )
    duration = models.CharField(max_length=100, blank=True, null=True)
    prerequisites = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_free = models.BooleanField(default=False)
    


    def save(self, *args, **kwargs):
        self.is_free = self.price == 0.0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='enrollments'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


class CourseMaterial(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='materials'
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_materials/')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Assignment(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='assignments'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name='submissions'
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='submissions'
    )
    file = models.FileField(upload_to='assignment_submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.assignment.title} - {self.student.username}"


from django.core.mail import send_mail
from django.conf import settings

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('bank', 'Bank Transfer'),
        ('bkash', 'Bkash'),
        ('nagad', 'Nagad'),
        ('cash', 'Cash'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='payments'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='payments'
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    payment_date = models.DateField(auto_now_add=True)
    
    receipt = models.ImageField(upload_to='receipts/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')

    def save(self, *args, **kwargs):
        
        if self.is_verified and self.payment_status == 'completed':
            # Enroll the student
            Enrollment.objects.get_or_create(student=self.student, course=self.course)

            # Send Email Logic 
            subject = 'Your Payment is Verified!'
            message = f"""
Dear {self.student.first_name},

We are pleased to inform you that your payment for the course "{self.course.title}" has been successfully verified.

You can now access the course materials and enjoy learning.

Thank you for choosing us!

Best regards,
Imran Faragi pias
            """
            recipient_email = self.student.email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False,
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.payment_status}"


class CourseComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    ratings = models.IntegerField()

    def __str__(self):
        return self.comment

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)