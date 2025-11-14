"""Serializers for transforming Django models to MongoDB documents."""
from datetime import datetime
from typing import Dict, Any


class AccountSerializer:
    """Serialize Django Account model to MongoDB document format.
    
    Transforms Account model instances into MongoDB-compatible dictionaries
    with flattened structure and additional metadata fields.
    """
    
    @staticmethod
    def serialize(account_instance) -> Dict[str, Any]:
        """Convert Django Account model instance to MongoDB document.
        
        Args:
            account_instance: Account model instance from Django ORM
            
        Returns:
            dict: MongoDB document with account data
            
        Document Structure:
            {
                'django_id': int,           # Primary key from Django
                'name': str,
                'last_name': str,
                'email': str,
                'age': int,
                'gender': str,
                'phone': str,
                'role': str,
                'doctor_profile': dict,     # Optional, only for psychologists
                'updated_at': datetime,
                'sync_version': int         # For tracking document updates
            }
        """
        data = {
            'django_id': account_instance.id,
            'name': account_instance.name,
            'last_name': account_instance.last_name,
            'full_name': account_instance.get_full_name(),
            'email': account_instance.email,
            'age': account_instance.age,
            'gender': account_instance.gender,
            'gender_display': account_instance.get_gender_display(),
            'phone': account_instance.phone,
            'role': account_instance.role,
            'role_display': account_instance.get_role_display(),
            'updated_at': datetime.utcnow(),
            'sync_version': 1,
        }
        
        # Include doctor profile data for psychologists
        if account_instance.role == 'psychologist':
            try:
                doctor = account_instance.doctor_profile
                data['doctor_profile'] = {
                    'django_doctor_id': doctor.id,
                    'specialty': doctor.specialty,
                    'specialty_display': doctor.get_specialty_display(),
                    'office': {
                        'django_office_id': doctor.doctors_office.id,
                        'name': doctor.doctors_office.name,
                        'address': doctor.doctors_office.address,
                        'phone': doctor.doctors_office.phone,
                    }
                }
            except Exception as e:
                # If doctor profile doesn't exist yet, mark as incomplete
                data['doctor_profile'] = None
                data['doctor_profile_incomplete'] = True
        
        return data


class AppointmentSerializer:
    """Serialize Django Appointment model to MongoDB document format."""
    
    @staticmethod
    def serialize(appointment_instance) -> Dict[str, Any]:
        """Convert Django Appointment model instance to MongoDB document.
        
        Args:
            appointment_instance: Appointment model instance from Django ORM
            
        Returns:
            dict: MongoDB document with appointment data
        """
        data = {
            'django_id': appointment_instance.id,
            'patient': {
                'django_id': appointment_instance.patient.id,
                'name': appointment_instance.patient.get_full_name(),
                'email': appointment_instance.patient.email,
            },
            'psychologist': {
                'django_id': appointment_instance.psychologist.id,
                'name': appointment_instance.psychologist.get_full_name(),
                'email': appointment_instance.psychologist.email,
            },
            'date': appointment_instance.date.isoformat(),
            'time': appointment_instance.time.isoformat(),
            'status': appointment_instance.status,
            'status_display': appointment_instance.get_status_display(),
            'notes': appointment_instance.notes,
            'updated_at': datetime.utcnow(),
            'sync_version': 1,
        }
        
        return data
