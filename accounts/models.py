from django.db import models
from django.utils.text import slugify


class Role(models.Model):
    """Role model for managing dynamic user roles.
    
    Allows administrators to create custom roles dynamically.
    Follows Single Responsibility Principle - manages role definitions only.
    """
    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Role Code",
        help_text="Unique code identifier (auto-generated from name)"
    )
    name = models.CharField(
        max_length=100, 
        verbose_name="Role Name",
        help_text="Display name for the role"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
        ]
        verbose_name = "Role"
        verbose_name_plural = "Roles"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate code from name if not provided."""
        if not self.code:
            self.code = slugify(self.name).replace('-', '_')
        super().save(*args, **kwargs)


class Account(models.Model):
    """
    Account model for managing patients and psychologists.
    Follows Single Responsibility Principle - manages user identity and role only.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    age = models.PositiveIntegerField(verbose_name="Age")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Gender")
    phone = models.CharField(max_length=20, verbose_name="Phone Number")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='accounts',
        verbose_name="Role",
        help_text="User role (dynamically managed)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        ordering = ['last_name', 'name']
        indexes = [
            models.Index(fields=['email']),
        ]
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
    
    def __str__(self):
        return f"{self.name} {self.last_name} ({self.role.name if self.role else 'No Role'})"
    
    def get_full_name(self):
        """Return the full name of the account holder"""
        return f"{self.name} {self.last_name}"
