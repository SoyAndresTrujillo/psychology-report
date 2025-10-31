from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Appointment
from .forms import AppointmentForm


def create_appointment_view(request):
    """Create a new appointment"""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(
                request,
                f'Appointment created for {appointment.date} at {appointment.time}!'
            )
            return redirect('appointments:list')
    else:
        form = AppointmentForm()
    
    return render(request, 'appointments/create.html', {'form': form})


def list_appointments_view(request):
    """List all appointments"""
    appointments = Appointment.objects.all().select_related(
        'patient', 'psychologist'
    ).order_by('-date', '-time')
    
    context = {
        'appointments': appointments,
        'total_count': appointments.count(),
        'scheduled_count': appointments.filter(status='scheduled').count(),
        'completed_count': appointments.filter(status='completed').count(),
    }
    return render(request, 'appointments/list.html', context)


def appointment_report_view(request):
    """Generate appointment report with full details"""
    appointments = Appointment.objects.select_related(
        'patient',
        'psychologist',
        'psychologist__doctor_profile__doctors_office'
    ).order_by('-date', '-time')
    
    return render(request, 'appointments/report.html', {'appointments': appointments})
