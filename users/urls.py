from ast import Pass
from django.urls import path
from .views import RegistrationView, EmailValidationView, VerificationView, LoginView, LogoutView, ChangePasswordView, PasswordResetView, CompletePasswordReset
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name='users'

urlpatterns = [
    path('register', RegistrationView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', views.Profile, name='profile'), 
    path('password-chage', ChangePasswordView.as_view(), name='password-change'),
    path('email-validate', csrf_exempt(EmailValidationView.as_view()), name='email-validate'),
    #for verification to activate account
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate'),

    #password reset request
    path('request-password-reset', PasswordResetView.as_view(), name='password-reset'),

    #link for reseting password
    path('reset-new-password/<uidb64>/<token>', CompletePasswordReset.as_view(), name='reset-new-password'),
 
    
]