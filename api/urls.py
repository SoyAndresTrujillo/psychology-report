from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('polls/create', views.create_poll_api, name='create_poll'),
    path('offices/create', views.create_office_api, name='create_office'),
    path('doctors/create', views.create_doctor_api, name='create_doctor'),
    path('accounts/create', views.create_account_api, name='create_account'),
    path('appointment-report', views.appointment_report_api, name='appointment_report'),
    path('appointments/create', views.create_appointment_api, name='create_appointment'),
]
