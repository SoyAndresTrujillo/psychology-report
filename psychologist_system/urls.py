"""
URL configuration for the psychologist_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

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
from accounts.views import HomeView

urlpatterns = [
    # Django admin site, python itself has a built-in admin site
    path('admin/', admin.site.urls),

    # Home page with navigation to all sections
    path('', HomeView.as_view(), name='home'),

    # Accounts section, this call is simple because each app into it, manage its own urls and views
    path('accounts/', include('accounts.urls')),

    # Doctors Offices section, this call is simple because each app into it, manage its own urls and views
    path('offices/', include('offices.urls')),

    # Doctors section, this call is simple because each app into it, manage its own urls and views
    path('doctors/', include('doctors.urls')),

    # Appointments section, this call is simple because each app into it, manage its own urls and views
    path('appointments/', include('appointments.urls')),

    # Polls section, this call is simple because each app into it, manage its own urls and views
    path('polls/', include('polls.urls')),

    # API section, this call is simple because each app into it, manage its own urls and views
    path('api/', include('api.urls'))
]
