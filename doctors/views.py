from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Doctor
from .forms import DoctorForm


def create_doctor_view(request):
    """Create a new doctor profile"""
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f'Doctor profile created for {doctor.account.get_full_name()}!')
            return redirect('doctors:list')
    else:
        form = DoctorForm()
    
    return render(request, 'doctors/create.html', {'form': form})


def list_doctors_view(request):
    """List all doctors"""
    doctors = Doctor.objects.all().select_related('account', 'doctors_office')
    return render(request, 'doctors/list.html', {'doctors': doctors})
