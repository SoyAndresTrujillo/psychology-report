# Data migration to populate Role table and migrate existing Account data
from django.db import migrations


def create_initial_roles(apps, schema_editor):
    """Create initial roles from existing ROLE_CHOICES."""
    Role = apps.get_model('accounts', 'Role')
    
    # Create the three existing roles
    initial_roles = [
        {'code': 'patient', 'name': 'Patient'},
        {'code': 'psychologist', 'name': 'Psychologist'},
        {'code': 'supervisor', 'name': 'Supervisor'},
    ]
    
    for role_data in initial_roles:
        Role.objects.get_or_create(**role_data)


def migrate_account_roles(apps, schema_editor):
    """Migrate existing Account.role CharField values to Role ForeignKey."""
    Account = apps.get_model('accounts', 'Account')
    Role = apps.get_model('accounts', 'Role')
    
    # Get all role instances
    patient_role = Role.objects.get(code='patient')
    psychologist_role = Role.objects.get(code='psychologist')
    supervisor_role = Role.objects.get(code='supervisor')
    
    # Map old role string values to new Role instances
    role_mapping = {
        'patient': patient_role,
        'psychologist': psychologist_role,
        'supervisor': supervisor_role,
    }
    
    # Update all accounts
    for account in Account.objects.all():
        if hasattr(account, 'role') and account.role:
            # If role is already a ForeignKey (migration already applied)
            if hasattr(account.role, 'code'):
                continue
            # If role is still a CharField
            role_obj = role_mapping.get(account.role)
            if role_obj:
                account.role = role_obj
                account.save(update_fields=['role'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_role_remove_account_accounts_ac_role_026657_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(create_initial_roles, migrations.RunPython.noop),
        migrations.RunPython(migrate_account_roles, migrations.RunPython.noop),
    ]
