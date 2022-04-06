from msilib.schema import CustomAction
from urllib import request
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.decorators import login_required
from .models import FilePost,ShareFile
from users.models import CustomUser
from .forms import FileUploadForm,FileShareForm 
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import json
# Create your views here.


def index(requst):
    return render(requst, 'base.html')

class FileSearch(View):
    def post(self, request):
        search_str = json.loads(request.body).get('searchText')
        files = FilePost.objects.filter(title__startswith=search_str, user=request.user) | FilePost.objects.filter(
            uploaded_at__startswith=search_str, user=request.user)
        
        data = files.values()
  
        return JsonResponse(list(data), safe=False)

@method_decorator(login_required(login_url='/users/login'), name='dispatch')
class FileListView(View):
    def get(self, request):
        files = FilePost.objects.filter(user = request.user).order_by('-uploaded_at')
        paginator = Paginator(files, 7)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'files': files, 'page_obj':page_obj }

        return render(request, 'files/my_files/files_list.html', context)

@method_decorator(login_required(login_url='/users/login'), name='dispatch')
class UploadFileView(View):
    def get(self, request):
        return render(request, 'files/my_files/add_file.html')
    
    def post(self, request):
        if request.method == "POST":
            title = request.POST['title']
            description = request.POST['description']
            file_upload = request.FILES['file_upload']

            context ={ 'values': request.POST }

            if not title:
                messages.error(request, 'File title is required')
                return render(request, 'files/my_files/add_file.html', context)

            if not description:
                messages.error(request, 'File description is required')
                return render(request, 'files/my_files/add_file.html', context)
            
            if not file_upload:
                messages.error(request, 'File is required')
                return render(request, 'files/my_files/add_file.html', context)
            
            FilePost.objects.create(user=request.user, title=title, description=description, file_upload=file_upload)
            messages.success(request, 'File is added successfully.')
            return redirect('files:home')

        return render(request, 'files/my_files/add_file.html')

class FileUpdateView(View):
    def get(self, request, id):
        file = FilePost.objects.get(pk=id)
        form = FileUploadForm(instance = file)
        context = {'form':form,'file':file}
        return render(request, 'files/my_files/file_update.html', context)
    
    def post(self, request, id):
        file = FilePost.objects.get(pk=id)
        form = FileUploadForm(instance=file)
        context = {'file':file}
        if request.method == "POST":
            form = FileUploadForm(request.POST, request.FILES, instance=file)
            if form.is_valid():
                form.save()
                messages.success(request, 'File is updated.')
                return redirect('files:home')

        return render(request, 'files/my_files/file_update.html', context)

class FileDeleteView(View):
    def post(self, request, id):
        file = get_object_or_404(FilePost, pk=id)
        context = {'file': file}
        if request.method == "POST":
            file.delete()
            messages.success(request, 'File is successfully deleted')
            return redirect('files:home')
        return render(request, 'files/my_files/file_delete..html', context)


def file_share(request,pk):
    print("Inside file share")
    share_form = FileShareForm()
    file_instance = get_object_or_404(FilePost,pk = pk)
    if request.method == 'POST':
        share_form = FileShareForm(request.POST,request.FILES)

        print("inside post")
        user = request.POST['user']
        user_instance = get_object_or_404(CustomUser, pk= user)
        print(user,"-------Inside post---------")
 
        if share_form.is_valid():
            print("Inside form valid")
            instance = share_form.save(commit=False)
            instance.file = file_instance
            instance.user = user_instance
            instance.status = True
            instance.save()
            return redirect('files:home')

    context = {
        'form':share_form,
        'file_instance':file_instance
    }
    return render(request, 'files/shared_files/file_share.html', context)


def user_share_file_list(request):
    files = ShareFile.objects.filter(user__pk = request.user.id)
    print(files)
    context = {
        'files':files
    }
    return render(request, 'files/shared_files/user_file_list.html', context)