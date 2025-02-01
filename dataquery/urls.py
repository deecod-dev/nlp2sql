# dataquery/urls.py
from django.urls import path
from . import views
from .views import home


urlpatterns = [
    path('run_query/', views.run_query, name='run_query'),
    path('', home, name='home'),
]
