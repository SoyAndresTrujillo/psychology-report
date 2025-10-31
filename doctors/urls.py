from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.list_doctors_view, name='list'),
    path('create/', views.create_doctor_view, name='create'),
]
