"""URL configuration for accounts app using generic class-based views.

Note: URL parameter changed from <int:account_id> to <int:pk>
to match Django generic view conventions.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.AccountListView.as_view(), name='list'),
    path('create/', views.AccountCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AccountDetailView.as_view(), name='detail'),
    path('create_role/', views.RoleCreateView.as_view(), name='create_role'),
]
