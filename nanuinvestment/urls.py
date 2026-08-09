"""
URL configuration for nanuinvestment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import path, include
from django.http import HttpResponse
from django.views.decorators.http import condition
from django.conf import settings
from django.conf.urls.static import static
import os

def get_sitemap():
    sitemap_path = os.path.join(os.path.dirname(__file__), '..', 'sitemap.xml')
    with open(sitemap_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_robots():
    robots_path = os.path.join(os.path.dirname(__file__), '..', 'robots.txt')
    with open(robots_path, 'r', encoding='utf-8') as f:
        return f.read()

def sitemap(request):
    return HttpResponse(get_sitemap(), content_type='application/xml')

def robots(request):
    return HttpResponse(get_robots(), content_type='text/plain')

def admin_logout_redirect(request):
    logout(request)
    return redirect('admin:login')

urlpatterns = [
    path('admin/logout/', admin_logout_redirect, name='admin_logout_redirect'),
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
    
    # SEO
    path('sitemap.xml', sitemap, name='sitemap'),
    path('robots.txt', robots, name='robots'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
