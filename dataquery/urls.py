# dataquery/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('process_file/', views.process_file, name='process_file'),
    path('process-query/', views.query_view, name='process_query'),  # New endpoint
    path('download/', views.download_result, name='download_result'),
    # path('upload/', views.process_file, name='upload_file'),
]
