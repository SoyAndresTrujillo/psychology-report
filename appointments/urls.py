from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.list_appointments_view, name='list'),
    path('create/', views.create_appointment_view, name='create'),
    path('report/', views.appointment_report_view, name='report'),
]
