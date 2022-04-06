from pydoc import render_doc
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import CustomUser, Profile

import threading

from .utils import accout_activation_token
from .forms import RegistrationForm, ProfileUpdateForm, UserUpdateForm
# from .utils import accout_activation_token
from validate_email import validate_email
import json

# Create your views here.

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send(fail_silently=False)
class EmailValidationView(View):
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        email = data['email']
        print(email)

        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)

        if CustomUser.objects.filter(email=email).exists():
            print(email)
            return JsonResponse({'email_error': 'sorry email is already in use. Please use another one'}, status=409)

        return JsonResponse({'email_valid': True})


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=id)

            if not accout_activation_token.check_token(user, token):
                return redirect('users:login' + '?message= User is already activated.')

            if user.is_active:
                return redirect('users:login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully.')
            return redirect('users:login')

        except Exception as ex:
            pass

        return redirect('users:login')

class RegistrationView(View):
    def get(self, request):
        return render(request, 'users/register.html')
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        context ={'form': form, 'fieldvalues': request.POST }

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if not CustomUser.objects.filter(email=email).exists():
                if len(password) < 8:
                    messages.error(request, 'Password is too short.')
                    return render(request, 'users/register.html', context)
                
                user = CustomUser.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password,is_superuser = False)
                user.set_password(password)
                user.is_active = False
                user.save()

                # path_to_view to verify the user
                # - getting domain we are on
                # - relative url to verification
                # - encode uid
                # - token

                current_site = get_current_site(request)
                email_body = {
                    'user': user,
                    'domain': current_site.domain, 
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': accout_activation_token.make_token(user)
                }
                link = reverse('users:activate', kwargs={
                               'uidb64': email_body['uid'], 'token': email_body['token']})

                activate_url = 'http://'+current_site.domain+link

                email_subject = "Activate your account"
                email_body = f"Hi, {user.first_name} {user.last_name}. Please click this link to verify your account\n" + activate_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'noreply@gmail.com',
                    [email],
                )

                EmailThread(email).start()
                messages.success(request, "Account successfully created. Please check your email to activate your account")
                return render(request, 'users/register.html')

        return render(request, 'users/register.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')
    
    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']

        if email and password:
            user = authenticate(request, email=email, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"welcome {user.first_name} {user.last_name}, you are now logged in.")
                    return redirect('files:home')

                messages.error(request, "Account is not active. please check your email.")
                return render(request, 'users/login.html')

            messages.error(request, "Invalid credentials. Try again.")
            return render(request, 'users/login.html')
        
        messages.error(request, "Please fill up the fields.")
        return render(request, 'users/login.html')


def Profile(request):
    if request.method=="POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES , instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('users:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)

class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users:profile')


@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('users:login')

class PasswordResetView(View):
    def get(self, request):
        return render(request, 'users/password_reset.html')
    
    def post(self, request):
        email = request.POST['email']

        context = {
            'values': request.POST
        }

        if not validate_email(email=email):
            messages.error(request, "Please enter a valid email")
            return render(request, 'users/password_reset.html', context)
        
        current_site = get_current_site(request)
        user = CustomUser.objects.filter(email=email)
        if user.exists():
            email_contents = {
                'user': user[0], # to get first user to verify
                'domain': current_site.domain, 
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0])
            }
            link = reverse('users:reset-new-password', kwargs={'uidb64': email_contents['uid'], 'token': email_contents['token']})
            reset_url = 'http://'+current_site.domain+link
            email_subject = "Password Reset Instructions"
            email_body = f"Hi there, please click this link to reset your password\n" + reset_url
            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@gmail.com',
                [email],               
                )
            EmailThread(email).start()
        messages.success(request, 'We have sent you an email to reset your password.')
        
        return render(request, 'users/password_reset.html') 
            

class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Link is already expired. Please request a new one.')
                return render(request, 'users/password_reset.html', context)
        except Exception as identifier:
            messages.info(request, 'Something went wrong, try again.')

        return render(request, 'users/set_new_password.html', context)

    def post(self, request, uidb64, token):

        context = {
            'uidb64': uidb64,
            'token': token
        }

        password = request.POST['password']
        password1 = request.POST['password1']

        if password != password1:
            messages.error(request, 'Password do not match.') 
            return render(request, 'users/set_new_password.html', context)

        if len(password) < 8:
            messages.error(request, 'Password is too short.')
            return render(request, 'users/set_new_password.html', context)


        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully. Now, you can use new password to login.')
            return redirect('users:login')
        except Exception as identifier:
            messages.info(request, 'Something went wrong, try again.')
        
        return render(request, 'users/set_new_password.html', context)
        
