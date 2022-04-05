from django import forms
from .models import CustomUser, Profile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField()

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password is too short")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data("password"))
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields =  ['first_name', 'last_name']
   

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
    
    def save(self, user=None):
        user_profile = super(ProfileUpdateForm, self).save(commit=False)
        if user:
            user_profile.user = user
        user_profile.save()
        return user_profile
    
    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = False
    
  