# Multi-step migration to convert role from CharField to ForeignKey

import django.db.models.deletion
from django.db import migrations, models


def create_initial_roles(apps, schema_editor):
    """Create initial roles from existing ROLE_CHOICES."""
    Role = apps.get_model('accounts', 'Role')
    
    initial_roles = [
        {'code': 'patient', 'name': 'Patient'},
        {'code': 'psychologist', 'name': 'Psychologist'},
        {'code': 'supervisor', 'name': 'Supervisor'},
    ]
    
    for role_data in initial_roles:
        Role.objects.get_or_create(**role_data)


def migrate_role_data(apps, schema_editor):
    """Migrate existing Account.role CharField values to role_new ForeignKey."""
    Account = apps.get_model('accounts', 'Account')
    Role = apps.get_model('accounts', 'Role')
    
    # Create mapping from old string values to new Role instances
    role_mapping = {}
    for code in ['patient', 'psychologist', 'supervisor']:
        try:
            role_mapping[code] = Role.objects.get(code=code)
        except Role.DoesNotExist:
            pass
    
    # Update all accounts
    for account in Account.objects.all():
        if account.role in role_mapping:
            account.role_new = role_mapping[account.role]
            account.save(update_fields=['role_new'])


def reverse_role_data(apps, schema_editor):
    """Reverse migration - copy role_new back to role."""
    Account = apps.get_model('accounts', 'Account')
    
    for account in Account.objects.all():
        if account.role_new:
            account.role = account.role_new.code
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
            index=models.Index(fields=['code'], name='accounts_ro_code_5aeee6_idx'),
        ),
        
        # Step 3: Populate Role table with initial data
        migrations.RunPython(create_initial_roles, migrations.RunPython.noop),
        
        # Step 4: Add temporary role_new ForeignKey field to Account
        migrations.AddField(
            model_name='account',
            name='role_new',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='accounts_temp',
                to='accounts.role',
                verbose_name='Role New',
            ),
        ),
        
        # Step 5: Migrate data from old role CharField to new role_new ForeignKey
        migrations.RunPython(migrate_role_data, reverse_role_data),
        
        # Step 6: Remove old role CharField and index
        migrations.RemoveIndex(
            model_name='account',
            name='accounts_ac_role_026657_idx',
        ),
        migrations.RemoveField(
            model_name='account',
            name='role',
        ),
        
        # Step 7: Rename role_new to role
        migrations.RenameField(
            model_name='account',
            old_name='role_new',
            new_name='role',
        ),
        
        # Step 8: Make role field non-nullable (change from nullable temp field)
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
    ]
