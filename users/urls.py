from django.urls import path
from .views import RegistrationView, EmailValidationView, VerificationView, LoginView, LogoutView, ChangePasswordView
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name='users'

urlpatterns = [
    path('register', RegistrationView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    # path('profile', ProfileView.as_view(), name='profile'),
    path('password-chage', ChangePasswordView.as_view(), name='password-change'),
    path('profile', views.Profile, name='profile'),    
    path('email-validate', csrf_exempt(EmailValidationView.as_view()), name='email-validate'),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate'),
]