# Generated manually for dynamic role management
# This migration creates Role model and migrates Account.role from CharField to ForeignKey

from django.db import migrations, models
import django.db.models.deletion


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
    
    # Map old role string values to new Role instances
    role_mapping = {}
    for role_code in ['patient', 'psychologist', 'supervisor']:
        try:
            role_mapping[role_code] = Role.objects.get(code=role_code)
        except Role.DoesNotExist:
            pass
    
    # Update all accounts to use the new role_temp ForeignKey field
    for account in Account.objects.all():
        old_role = account.role
        if old_role in role_mapping:
            account.role_temp = role_mapping[old_role]
            account.save(update_fields=['role_temp'])


def reverse_migrate_account_roles(apps, schema_editor):
    """Reverse migration - copy role_temp back to role CharField."""
    Account = apps.get_model('accounts', 'Account')
    
    for account in Account.objects.all():
        if account.role_temp:
            account.role = account.role_temp.code
            account.save(update_fields=['role'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_account_role'),
    ]

    operations = [
        # Step 1: Create Role model
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Unique code identifier (auto-generated from name)', max_length=50, unique=True, verbose_name='Role Code')),
                ('name', models.CharField(help_text='Display name for the role', max_length=100, verbose_name='Role Name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles',
                'ordering': ['name'],
            },
        ),
        
        # Step 2: Add index to Role model
        migrations.AddIndex(
            model_name='role',
            index=models.Index(fields=['code'], name='accounts_ro_code_0e8f3b_idx'),
        ),
        
        # Step 3: Create initial roles
        migrations.RunPython(create_initial_roles, migrations.RunPython.noop),
        
        # Step 4: Add temporary role field to Account (ForeignKey)
        migrations.AddField(
            model_name='account',
            name='role_temp',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='accounts_temp',
                to='accounts.role',
                verbose_name='Role Temp',
            ),
        ),
        
        # Step 5: Migrate data from old role CharField to new role_temp ForeignKey
        migrations.RunPython(migrate_account_roles, reverse_migrate_account_roles),
        
        # Step 6: Remove old role CharField
        migrations.RemoveField(
            model_name='account',
            name='role',
        ),
        
        # Step 7: Rename role_temp to role
        migrations.RenameField(
            model_name='account',
            old_name='role_temp',
            new_name='role',
        ),
        
        # Step 8: Make role field non-nullable
        migrations.AlterField(
            model_name='account',
            name='role',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='accounts',
                to='accounts.role',
                verbose_name='Role',
                help_text='User role (dynamically managed)'
            ),
        ),
        
        # Step 9: Update Account Meta to remove old index
        migrations.AlterModelOptions(
            name='account',
            options={'ordering': ['last_name', 'name'], 'verbose_name': 'Account', 'verbose_name_plural': 'Accounts'},
        ),
    ]
