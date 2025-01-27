from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import threading

class MailThread(threading.Thread):
    def __init__(self,email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send()

def send_activiton_email(recepient_email, activistion_url):
    subject = 'Account Activision'
    from_email = settings.EMAIL_HOST_USER
    to_email = [recepient_email]
    html_content = render_to_string('account/active_email.html', {'activition':activistion_url})
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject,text_content,from_email,to_email)
    email.attach_alternative(html_content,'text/html')
    MailThread(email).start()

