from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.list_polls_view, name='list'),
    path('create/', views.create_poll_view, name='create'),
    path('<int:poll_id>/', views.poll_detail_view, name='detail'),
]
