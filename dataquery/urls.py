# dataquery/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('process_file/', views.process_file, name='process_file'),
    path('process-query/', views.query_view, name='process_query'),  # New endpoint
]
