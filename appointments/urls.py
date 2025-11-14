"""URL configuration for appointments app using generic class-based views."""
from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.AppointmentListView.as_view(), name='list'),
    path('create/', views.AppointmentCreateView.as_view(), name='create'),
    path('report/', views.AppointmentReportView.as_view(), name='report'),
]
