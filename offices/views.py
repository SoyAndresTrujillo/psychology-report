from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DoctorsOffice
from .forms import DoctorsOfficeForm


def create_office_view(request):
    """Create a new doctor's office"""
    if request.method == 'POST':
        form = DoctorsOfficeForm(request.POST)
        if form.is_valid():
            office = form.save()
            messages.success(request, f'Office "{office.name}" created successfully!')
            return redirect('offices:list')
    else:
        form = DoctorsOfficeForm()
    
    return render(request, 'offices/create.html', {'form': form})


def list_offices_view(request):
    """List all doctor's offices"""
    offices = DoctorsOffice.objects.all().select_related('psychologist')
    return render(request, 'offices/list.html', {'offices': offices})
