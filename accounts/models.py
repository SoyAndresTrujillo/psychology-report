from django.db import models


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
    
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('psychologist', 'Psychologist'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    age = models.PositiveIntegerField(verbose_name="Age")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Gender")
    phone = models.CharField(max_length=20, verbose_name="Phone Number")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Role")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        ordering = ['last_name', 'name']
        indexes = [
            models.Index(fields=['role', 'email']),
            models.Index(fields=['email']),
        ]
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
    
    def __str__(self):
        return f"{self.name} {self.last_name} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the full name of the account holder"""
        return f"{self.name} {self.last_name}"
