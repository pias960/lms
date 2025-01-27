from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm ,UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm,SetPasswordForm



class RegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=150, help_text="Username or email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set custom labels for fields
        self.fields['username'].label = 'Username/Email'
        self.fields['password'].label = 'Password'
        self.fields['username'].widget.attrs['placeholder'] = 'Enter Username or Email'

    def clean_username(self):
        username_email = self.cleaned_data.get('username')
        
        # Try to get user by either email or username
        try:
            user = User.objects.get(email=username_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username_email)
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid username or email")

        # Return the username/email if it's valid
        return user.username


class passwordChangeForm(PasswordChangeForm):
    PasswordChangeForm.base_fields['old_password'].widget.attrs['class'] = 'form-control'
    PasswordChangeForm.base_fields['new_password1'].widget.attrs['class'] = 'form-control'
    PasswordChangeForm.base_fields['new_password2'].widget.attrs['class'] = 'form-control'
    
class setpasswordform(SetPasswordForm):
    PasswordChangeForm.base_fields['new_password1'].widget.attrs['class'] = 'form-control'
    PasswordChangeForm.base_fields['new_password2'].widget.attrs['class'] = 'form-control'
    
class passwordresetform(PasswordResetForm):
    PasswordResetForm.base_fields['email'].widget.attrs['class'] = 'form-control'


    
    
        
    

   