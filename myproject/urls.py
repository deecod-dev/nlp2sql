"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# from django.http import HttpResponse
# def home_view(request):
#     return HttpResponse("Welcome to the home page!")

from django.shortcuts import render
def home_view(request):
    return render(request, 'dataquery/home.html')  # Renders home.html

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dataquery/', include('dataquery.urls')),
    # path('', home_view),  # Add this line to map the root URL to the home_view
    path('', include('dataquery.urls')),
]


from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Now, uploaded files will be accessible via URLs like:
# http://127.0.0.1:8000/media/uploads/your_uploaded_file.csv