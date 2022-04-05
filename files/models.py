from django.db import models
from users.models import CustomUser
from django.utils import timezone
# Create your models here.

class FilePost(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file_upload = models.FileField(upload_to='uploaded_files')
    description = models.TextField()
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user}'