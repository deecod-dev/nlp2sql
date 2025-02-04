# dataquery/urls.py
from django.urls import path
from . import views

# # podtgresql
# urlpatterns = [
#     path('', views.home, name='home'),
#     path('process_file/', views.process_file, name='process_file'),
#     path('process-query/', views.query_view, name='process_query'),  # New endpoint
#     path('download/', views.download_result, name='download_result'),
#     path('drop_table/', views.drop_table_view, name='drop_table'),  # Add this line
#     # path('upload/', views.process_file, name='upload_file'),
# ]
from .views import update_settings_variable
# duckdb
urlpatterns = [
    path('', views.home, name='home'),
    path('process_file/', views.process_file, name='process_file'),
    path('process-query/', views.query_view, name='process_query'),  # New endpoint
    path('download/', views.download_result, name='download_result'),
    path("update_settings/", update_settings_variable, name="update_settings"),
    
    # path('drop_table/', views.drop_files, name='drop_table'),  # Add this line
    # path('upload/', views.process_file, name='upload_file'),
]
