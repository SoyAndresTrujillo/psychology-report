from django.urls import path
from . import views

app_name = 'offices'

urlpatterns = [
    path('', views.list_offices_view, name='list'),
    path('create/', views.create_office_view, name='create'),
]
