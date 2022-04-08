from django.urls import path
from .views import FileListView, UploadFileView, FileUpdateView, FileDeleteView, FileSearch
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name='files'


urlpatterns = [
    path('', views.index, name='base-home'),
    path('home', FileListView.as_view(), name='home'),
    path('add-file', UploadFileView.as_view(), name='add-file'),
    path('<int:id>/update-file', FileUpdateView.as_view(), name='update-file'),
    path('<int:id>/delete-file', FileDeleteView.as_view(), name='delete-file'),
    path('search-files', csrf_exempt(FileSearch.as_view()), name='search-files'),
    path('share-file/<pk>/', views.file_share, name='share-file'),
    path('received-files/', views.user_share_file_list, name='user-share-file-list'),
    path('my-shared-files/', views.my_shared_files_list, name='my-shared-files')
]