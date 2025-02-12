from django.db import models
from django.contrib.auth.models import User,Group
from django.db.models.signals import post_save
from django.dispatch import receiver
import re
from django.core.exceptions import ValidationError
from django.utils import timezone


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
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    duration = models.CharField(max_length=100, blank=True, null=True)
    prerequisites = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_free = models.BooleanField(default=False)
    rating = models.CharField(default=4, max_length=1,blank=True, null=True)
    tags = models.CharField(max_length=25, default='',blank=True, null=True)
    url = models.URLField(max_length=200, null=True, blank=True, help_text='')

   

    def save(self, *args, **kwargs):
        self.is_free = self.price == 0.0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title






import re
from django.core.exceptions import ValidationError

def PhoneNumberValidator(value):
    if not re.match(r'^\+880-1[0-9]{8}$', value):
        raise ValidationError('Invalid phone number format.')
    




from django.contrib.auth.models import Group
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    number = models.CharField(
        max_length=11,
        validators=[RegexValidator(r'^\d{11}$', message="Enter a valid 11-digit phone number.")],
        blank=True,
        null=True
    )
    address = models.CharField(max_length=200, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=16, blank=True, null=True)
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # Check if user is a teacher
        if self.is_teacher:
            group, created = Group.objects.get_or_create(name='Teachers')  
            self.user.groups.add(group)
            
            # Ensure the TeacherProfile exists
            TeacherAccount.objects.get_or_create(user=self.user)

        super().save(*args, **kwargs)  # Save Profile instance


   
    
# signal for automate Profile
@receiver(post_save, sender=User)
def _post_save_receiver(sender, instance,created,**kwargs):
    if created:
        Profile.objects.create(user=instance)



    
    
    


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
    image = models.ImageField(upload_to='Video_Thumbnail')
    description = models.TextField(max_length=40,null=True, blank=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(blank=True, null=True)
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
    
     

    def assignment_expiry(self):
        if self.due_date.date() < timezone.now().date():
            self.delete()  # শুধুমাত্র self.delete() কল করলেই হবে

        





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
            # Update teacher's balance
            teacher = self.course.teacher  # Assuming 'teacher' is linked in Course model
            if hasattr(teacher, 'teacherprofile'):  # Ensure teacher has a profile
                teacher.teacheraccount.balance += self.course.price
                teacher.teacheraccount.save()  # Save the updated balance


            
            # Send Payment Success Email
            subject = 'Your Payment is Verified!'
            message = f"""
    Dear {self.student.username},

    We are pleased to inform you that your payment for the course "{self.course.title}" has been successfully verified.

    You can now access the course materials and enjoy learning.

    Thank you for choosing us!

    Best regards,
    Imran Faragi Pias
            """
            recipient_email = self.student.email
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email], fail_silently=False)

        elif self.is_verified and self.payment_status == 'failed':
            # Send Payment Failure Email
            subject = 'Your Payment Failed!'
            message = f"""
    Dear {self.student.username},

    We regret to inform you that your payment for the course "{self.course.title}" has failed.

    Please try again or contact our customer support team for further assistance.

    Best regards,
    Imran Faragi Pias
            """



            recipient_email = self.student.email
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email], fail_silently=False)

        super().save(*args, **kwargs)  # Save the Payment object

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


class TeacherAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Earnings

    def __str__(self):
        return self.user.username
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)  # To track if the user has seen it
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:30]}"