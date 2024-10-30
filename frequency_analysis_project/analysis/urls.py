from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
     path('download/', views.download_analysis_file, name='download_file'),
]
