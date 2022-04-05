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

from .models import CustomUser, Profile


from .utils import accout_activation_token
from .forms import RegistrationForm, ProfileUpdateForm, UserUpdateForm
# from .utils import accout_activation_token
from validate_email import validate_email
import json

# Create your views here.


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

                email.send(fail_silently=True)
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


# class ProfileView(View):
#     def get(self, request):
#         user = CustomUser.objects.filter(user=request.user)
#         context = {'user':user}
#         return render(request, 'users/profile.html', context)
    
#     def post(self, request):
#         user = CustomUser.objects.filter(user=request.user)
#         profile = Profile.objects.filter(user=request.user)
#         context = {'user':user, 'profile':profile}
#         if request.method =="POST":
#             first_name = request.POST['first_name']
#             last_name = request.POST['last_name']
#             image = request.FILES['image']

#             if not first_name:
#                 messages.error(request, 'First name is missing.')
#                 return render(request, 'users/profile.html', context)

#             if not last_name:
#                 messages.error(request, 'Last name is missing.')
#                 return render(request, 'users/profile.html', context)
            
#             user.first_name = first_name
#             user.last_name = last_name
#             profile.image = image
#             user.save()
#             profile.save()        
#             messages.success(request, 'Profile is updated.')
#             return redirect('files:home')
            
#         return render(request, 'users/profile.html', context)
            


            