from django.db import models


class DoctorsOffice(models.Model):
    """
    DoctorsOffice model for managing doctor's office locations.
    Follows Single Responsibility Principle - manages office information only.
    """
    name = models.CharField(max_length=200, verbose_name="Office Name")
    address = models.TextField(verbose_name="Address")
    phone = models.CharField(max_length=20, verbose_name="Phone Number")
    email = models.EmailField(verbose_name="Email Address")
    psychologist = models.ForeignKey(
        'accounts.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'psychologist'},
        related_name='managed_offices',
        verbose_name="Managing Psychologist"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Doctor's Office"
        verbose_name_plural = "Doctors' Offices"
    
    def __str__(self):
        return self.name
