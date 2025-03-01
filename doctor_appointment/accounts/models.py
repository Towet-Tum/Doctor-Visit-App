from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')

    @property
    def is_doctor(self):
        return self.role == 'doctor'
    
    @property
    def is_patient(self):
        return self.role == 'patient'

class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    specialty = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField()
    max_appointments = models.PositiveIntegerField(default=30)
    current_appointments = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"DoctorProfile of {self.user.username}"


class PatientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    medical_history = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"PatientProfile of {self.user.username}"