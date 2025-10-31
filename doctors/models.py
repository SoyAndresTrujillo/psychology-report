from django.db import models


class Doctor(models.Model):
    """
    Doctor model for linking psychologists to offices with specialties.
    Follows Single Responsibility Principle - manages doctor profiles only.
    """
    SPECIALTY_CHOICES = [
        ('clinical', 'Clinical Psychology'),
        ('cognitive', 'Cognitive Psychology'),
        ('developmental', 'Developmental Psychology'),
        ('social', 'Social Psychology'),
        ('neuropsychology', 'Neuropsychology'),
        ('counseling', 'Counseling Psychology'),
    ]
    
    account = models.OneToOneField(
        'accounts.Account',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'psychologist'},
        related_name='doctor_profile',
        verbose_name="Psychologist Account"
    )
    doctors_office = models.ForeignKey(
        'offices.DoctorsOffice',
        on_delete=models.CASCADE,
        related_name='doctors',
        verbose_name="Doctor's Office"
    )
    specialty = models.CharField(
        max_length=50,
        choices=SPECIALTY_CHOICES,
        verbose_name="Specialty"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        ordering = ['account__last_name', 'account__name']
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
    
    def __str__(self):
        return f"Dr. {self.account.get_full_name()} - {self.get_specialty_display()}"
