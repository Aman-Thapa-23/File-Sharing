from django.contrib import admin
from .models import FilePost, ShareFile
# Register your models here.

@admin.register(ShareFile)
class ShareFiletAdmin(admin.ModelAdmin):
    ordering = ['shared_at']
    list_display = ['user', 'file', 'status', 'shared_at']


@admin.register(FilePost)
class FilePostAdmin(admin.ModelAdmin):
    ordering = ['uploaded_at']
    list_display = ['user', 'title', 'uploaded_at', 'file_upload']
