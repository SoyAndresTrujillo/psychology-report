from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.list_accounts_view, name='list'),
    path('create/', views.create_account_view, name='create'),
    path('<int:account_id>/', views.account_detail_view, name='detail'),
]
