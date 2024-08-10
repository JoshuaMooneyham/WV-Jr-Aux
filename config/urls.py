"""
URL configuration for config project.

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
from django.urls import path, re_path, include
from django.views.static import serve
from app.views import *

urlpatterns = [
    path("", home, name = "home"),
    path('admin/', admin.site.urls),
    # path('login/', loginPage, name="login"),
    path('logout/', logoutUser, name="logout"),
    path('about/', aboutUs, name="about"),
    path('projects/', projectsPage, name="projects"),
    path('contact/', contactUs, name="contact"),
    path('auction/', include('auction.urls')),

    # ==={ File Serving }=== #
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]