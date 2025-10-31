from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from accounts.models import Account
from offices.models import DoctorsOffice
from doctors.models import Doctor
from appointments.models import Appointment


def api_response(success, message, data=None, errors=None):
    """Unified API response format"""
    response = {
        'success': success,
        'message': message
    }
    if data is not None:
        response['data'] = data
    if errors is not None:
        response['errors'] = errors
    return response


@csrf_exempt
@require_http_methods(["POST"])
def create_account_api(request):
    """API endpoint to create an account"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'last_name', 'age', 'gender', 'phone', 'email', 'role']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse(
                api_response(False, 'Missing required fields', errors={'missing': missing_fields}),
                status=400
            )
        
        # Create account
        account = Account.objects.create(
            name=data['name'],
            last_name=data['last_name'],
            age=data['age'],
            gender=data['gender'],
            phone=data['phone'],
            email=data['email'],
            role=data['role']
        )
        
        # If psychologist, create doctor profile
        if account.role == 'psychologist' and 'doctors_office_id' in data and 'specialty' in data:
            try:
                office = DoctorsOffice.objects.get(id=data['doctors_office_id'])
                Doctor.objects.create(
                    account=account,
                    doctors_office=office,
                    specialty=data['specialty']
                )
            except DoctorsOffice.DoesNotExist:
                pass
        
        return JsonResponse(
            api_response(True, 'Account created successfully', {
                'id': account.id,
                'name': account.get_full_name(),
                'email': account.email,
                'role': account.role
            }),
            status=201
        )
    
    except json.JSONDecodeError:
        return JsonResponse(
            api_response(False, 'Invalid JSON', errors={'json': 'Request body is not valid JSON'}),
            status=400
        )
    except Exception as e:
        return JsonResponse(
            api_response(False, 'Error creating account', errors={'error': str(e)}),
            status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def create_office_api(request):
    """API endpoint to create a doctor's office"""
    try:
        data = json.loads(request.body)
        
        required_fields = ['name', 'address', 'phone', 'email']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse(
                api_response(False, 'Missing required fields', errors={'missing': missing_fields}),
                status=400
            )
        
        office = DoctorsOffice.objects.create(
            name=data['name'],
            address=data['address'],
            phone=data['phone'],
            email=data['email'],
            psychologist_id=data.get('psychologist_id')
        )
        
        return JsonResponse(
            api_response(True, 'Office created successfully', {
                'id': office.id,
                'name': office.name
            }),
            status=201
        )
    
    except Exception as e:
        return JsonResponse(
            api_response(False, 'Error creating office', errors={'error': str(e)}),
            status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def create_doctor_api(request):
    """API endpoint to create a doctor profile"""
    try:
        data = json.loads(request.body)
        
        required_fields = ['account_id', 'doctors_office_id', 'specialty']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse(
                api_response(False, 'Missing required fields', errors={'missing': missing_fields}),
                status=400
            )
        
        account = Account.objects.get(id=data['account_id'])
        office = DoctorsOffice.objects.get(id=data['doctors_office_id'])
        
        doctor = Doctor.objects.create(
            account=account,
            doctors_office=office,
            specialty=data['specialty']
        )
        
        return JsonResponse(
            api_response(True, 'Doctor profile created successfully', {
                'id': doctor.id,
                'name': doctor.account.get_full_name(),
                'specialty': doctor.specialty
            }),
            status=201
        )
    
    except Account.DoesNotExist:
        return JsonResponse(
            api_response(False, 'Account not found', errors={'account_id': 'Account does not exist'}),
            status=404
        )
    except DoctorsOffice.DoesNotExist:
        return JsonResponse(
            api_response(False, 'Office not found', errors={'doctors_office_id': 'Office does not exist'}),
            status=404
        )
    except Exception as e:
        return JsonResponse(
            api_response(False, 'Error creating doctor profile', errors={'error': str(e)}),
            status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def create_appointment_api(request):
    """API endpoint to create an appointment"""
    try:
        data = json.loads(request.body)
        
        required_fields = ['patient_id', 'psychologist_id', 'date', 'time']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse(
                api_response(False, 'Missing required fields', errors={'missing': missing_fields}),
                status=400
            )
        
        patient = Account.objects.get(id=data['patient_id'], role='patient')
        psychologist = Account.objects.get(id=data['psychologist_id'], role='psychologist')
        
        appointment = Appointment.objects.create(
            patient=patient,
            psychologist=psychologist,
            date=data['date'],
            time=data['time'],
            status=data.get('status', 'scheduled')
        )
        
        return JsonResponse(
            api_response(True, 'Appointment created successfully', {
                'id': appointment.id,
                'patient': patient.get_full_name(),
                'psychologist': psychologist.get_full_name(),
                'date': str(appointment.date),
                'time': str(appointment.time),
                'status': appointment.status
            }),
            status=201
        )
    
    except Account.DoesNotExist:
        return JsonResponse(
            api_response(False, 'Account not found', errors={'error': 'Patient or psychologist not found'}),
            status=404
        )
    except Exception as e:
        return JsonResponse(
            api_response(False, 'Error creating appointment', errors={'error': str(e)}),
            status=500
        )


@require_http_methods(["GET"])
def appointment_report_api(request):
    """API endpoint for appointment report with full details"""
    try:
        appointments = Appointment.objects.select_related(
            'patient',
            'psychologist',
            'psychologist__doctor_profile__doctors_office'
        ).all()
        
        report_data = []
        for appointment in appointments:
            office_name = None
            office_address = None
            
            try:
                if hasattr(appointment.psychologist, 'doctor_profile'):
                    office_name = appointment.psychologist.doctor_profile.doctors_office.name
                    office_address = appointment.psychologist.doctor_profile.doctors_office.address
            except:
                pass
            
            report_data.append({
                'appointment_id': appointment.id,
                'patient_name': appointment.patient.get_full_name(),
                'patient_email': appointment.patient.email,
                'patient_phone': appointment.patient.phone,
                'psychologist_name': appointment.psychologist.get_full_name(),
                'psychologist_email': appointment.psychologist.email,
                'psychologist_phone': appointment.psychologist.phone,
                'office_name': office_name,
                'office_address': office_address,
                'date': str(appointment.date),
                'time': str(appointment.time),
                'status': appointment.status
            })
        
        return JsonResponse(
            api_response(True, 'Report generated successfully', {'appointments': report_data}),
            status=200
        )
    
    except Exception as e:
        return JsonResponse(
            api_response(False, 'Error generating report', errors={'error': str(e)}),
            status=500
        )

@csrf_exempt
@require_http_methods(["POST"])
def create_poll_api(request):
    try:
        data = json.loads(request.body)
        
        required_fields = ['description', 'rate']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse(
                api_response(False, 'Missing required fields', errors={'missing': missing_fields}),
                status=400
            )
        
        poll = Polls.objects.create(
            description=data['description'],
            rate=data['rate']
        )
        
        return JsonResponse(
            api_response(True, 'Poll created successfully', {
                'id': poll.id,
                'description': poll.description,
                'rate': poll.rate
            }),
            status=201
        )
    except Exception as e:
        return JsonResponse(
            api_response(False, 'Error creating poll', errors={'error': str(e)}),
            status=500
        )
    