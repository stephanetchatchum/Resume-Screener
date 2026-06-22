from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('job/create/', views.create_job, name='create_job'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/upload/', views.upload_resume, name='upload_resume'),
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('job/<int:job_id>/gmail-auth/', views.gmail_auth, name='gmail_auth'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('job/<int:job_id>/gmail-scan/', views.gmail_scan, name='gmail_scan'),
    path('job/<int:job_id>/candidate/<int:candidate_id>/', views.candidate_detail, name='candidate_detail'),
]