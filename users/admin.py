from django.contrib import admin
from .models import CustomUser, Profile
# Register your models here.

from django.contrib import admin


@admin.register(CustomUser)
class AdminUser(admin.ModelAdmin):
    ordering = ['email']
    list_display=['first_name','last_name','email', 'is_staff', 'is_active']

admin.site.register(Profile)