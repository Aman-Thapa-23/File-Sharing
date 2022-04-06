from django.db import models
from users.models import CustomUser
from django.utils import timezone
# Create your models here.

class FilePost(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file_upload = models.FileField(upload_to='uploaded_files', verbose_name='File Name')
    description = models.TextField()
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user}'


class ShareFile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Shared To')
    file = models.ForeignKey(FilePost, on_delete = models.CASCADE, verbose_name='Shared By')
    status = models.BooleanField(default = False)
    shared_at = models.DateTimeField(auto_now_add=True)