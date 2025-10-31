from django.db import models
from django.core.exceptions import ValidationError


class Appointment(models.Model):
    """
    Appointment model for managing appointment scheduling.
    Follows Single Responsibility Principle - manages appointments only.
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    patient = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='patient_appointments',
        verbose_name="Patient"
    )
    psychologist = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'psychologist'},
        related_name='psychologist_appointments',
        verbose_name="Psychologist"
    )
    date = models.DateField(verbose_name="Appointment Date")
    time = models.TimeField(verbose_name="Appointment Time")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name="Status"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        ordering = ['-date', '-time']
        unique_together = ['psychologist', 'date', 'time']
        indexes = [
            models.Index(fields=['date', 'psychologist']),
            models.Index(fields=['patient', 'status']),
        ]
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
    
    def __str__(self):
        return f"{self.patient.get_full_name()} with {self.psychologist.get_full_name()} on {self.date}"
    
    def clean(self):
        """Validate that patient and psychologist are different"""
        if self.patient_id == self.psychologist_id:
            raise ValidationError("Patient and psychologist cannot be the same person")
