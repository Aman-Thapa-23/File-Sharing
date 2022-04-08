from django import forms
from .models import FilePost,ShareFile

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FilePost
        fields = ('title', 'file_upload', 'description')
    
    def __init__(self, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.fields['file_upload'].label = False
        


class FileShareForm(forms.ModelForm):
    class Meta:
        model = ShareFile
        fields = ('user',)
    
    def __init__(self, *args, **kwargs):
        super(FileShareForm, self).__init__(*args, **kwargs)
        self.fields['user'].label = False