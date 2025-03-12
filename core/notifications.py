from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, Payment


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





