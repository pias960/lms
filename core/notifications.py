from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, Payment,Applications
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
@receiver(post_save, sender=Payment)
def send_notification(sender,instance,created, **kwrgs):
    if instance.is_verified and instance.payment_status == 'completed':
        message = f"Your payment for the course '{instance.course.title}' has been verified."
        Notification.objects.create(user=instance.student, message=message)
        
    elif instance.payment_status == 'pending':
        message = f"Your payment for the course '{instance.course.title}' is still pending."
        Notification.objects.create(user=instance.student, message=message)
    elif instance.payment_status == 'failed':
        message = f"Your payment for the course '{instance.course.title}' has failed."
        Notification.objects.create(user=instance.student, message=message)


@receiver(post_save, sender=Applications)
def send_application_email(sender,instance,created, **kwrgs):
    admin = User.objects.get(is_superuser=True)
    if created:
        subject = f"New Application from {instance.email}"
        message = f"A new application for Teacher from  Mr.'{instance.name}' has been submitted."
        Notification.objects.create(user=admin, message=message)
        send_mail(subject, message, settings.EMAIL_HOST_USER, [admin.email])
        
  


