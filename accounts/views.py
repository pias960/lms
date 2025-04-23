from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import *
from django.contrib import messages
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .utils import send_activiton_email
from django.contrib.auth import authenticate,login , logout
from django.contrib.auth.forms import PasswordChangeForm,SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
# Create your views here.

def registration(request):
    if request.method == 'POST':
        fm = RegistrationForm(request.POST)
        if fm.is_valid():
            user = fm.save(commit = False)
            user.set_password(fm.cleaned_data['password1'])
            user.is_active = False
            user.save()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activition_link = reverse('activate',kwargs={'uidb64': uidb64, 'token': token})
            activition_url = f'{settings.SITE_DOMAIN}{activition_link}'
            send_activiton_email(user.email, activition_url)
            messages.success(request, 'Registration successful')
            return redirect('check_activision_email')
    else:
        fm = RegistrationForm()
    return render(request, 'accounts/registration.html',{'form' : fm} )
# Replace with your actual User model path



def activision_check(request, uidb64, token):
    try:
        # Decode the user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        # Check if the user is already active
        if user.is_active:
            messages.warning(request, 'Your account is already activated.')
            return redirect('login')
        
        # Validate the token
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('activation_success')
        
        else:
            messages.error(request, 'Invalid activation link.')
            return redirect('signup')  # Redirect to a relevant page like signup or home
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid activation link.')
        return redirect('signup')  # Redirect to a relevant page like signup or home

  # Replace `account.models` with your app name

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import CustomAuthenticationForm

def user_login(request):
    form = None
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']  # Get the username (either from email or actual username)
            password = form.cleaned_data['password']  # Get password from the form submission
            # Authenticate the user using the username
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')  # Redirect to a success page after login
    return render(request, 'accounts/login.html', {'form': form})




@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')




def user_logout(request):
    logout(request)
    return redirect('home') 

def activition_success(request):
    return render(request, 'accounts/activation_success.html')


def activision_email_check(request):
    return render(request, 'accounts/activation_email_check.html')
    

    
    
     # Redirect to a page where you want to redirect after logout.
