from django.urls import path

from .views import * 
from django.contrib.auth.decorators import  login_required
from django.contrib.auth.views import PasswordChangeDoneView,PasswordResetConfirmView,PasswordResetDoneView,PasswordChangeView ,PasswordResetCompleteView,PasswordResetView
urlpatterns = [
    path('reg/', registration, name='reg'),
    #for user login
    path('login/', user_login, name='login'),
    #for check the email
    path('activate/<str:uidb64>/<str:token>/', activision_check, name='activate'),
    #for logout user
    path('logout/', user_logout, name="logout"),

     ########password change done url###########
    path("passwordchangedone/", PasswordChangeDoneView.as_view(template_name='dashboard/passwordchangedone.html'), 
         name="passswordchangedone"),

    ########password change url###########
    path('password_change/',login_required( PasswordChangeView.as_view(template_name='account/passwordchange.html',
              form_class=PasswordChangeForm, success_url='passswordchangedone')), name='password_change'),
    

    path('password_reset/',PasswordResetView.as_view(template_name='account/passwordreset.html',
              form_class=passwordresetform, ), name='password-reset'),
            
    path("password_reset/done/",PasswordResetDoneView.as_view(template_name='account/passwordresetdone.html'), 
    name="password_reset_done"),


     path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='account/passwordresetconfirm.html',
              form_class=setpasswordform, ), name='password_reset_confirm'),

     path("password_reset_complete/", PasswordResetCompleteView.as_view(template_name='account/passwordresetcomplete.html'), 
    name="password_reset_complete"),
   

]