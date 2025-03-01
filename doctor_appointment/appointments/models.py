from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELED', 'Canceled'),
        ('RESCHEDULED', 'Rescheduled'),
    ]
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="doctor_appointments"
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="patient_appointments"
    )
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('doctor', 'appointment_date')
        indexes = [
            models.Index(fields=['doctor', 'appointment_date']),
        ]
    
    def clean(self):
        # Validate that the appointment is scheduled within the next 15 days.
        now = timezone.now()
        if self.appointment_date > now + timedelta(days=15):
            raise ValidationError("Appointment must be scheduled within 15 days.")
        if self.appointment_date < now:
            raise ValidationError("Appointment date must be in the future.")
        
        # Enforce doctor's limit: maximum 30 confirmed appointments per day.
        if self.status == 'CONFIRMED':
            confirmed_count = Appointment.objects.filter(
                doctor=self.doctor, 
                status='CONFIRMED', 
                appointment_date__date=self.appointment_date.date()
            ).exclude(id=self.id).count()
            if confirmed_count >= 30:
                raise ValidationError("Doctor has reached the maximum number of appointments for this day.")
    
    def can_cancel(self):
        # Allow cancellation only if more than 3 days remain until the appointment.
        return self.appointment_date - timezone.now() > timedelta(days=3)
    
    def __str__(self):
        return f"Appointment {self.id} - Doctor: {self.doctor} Patient: {self.patient}"



class Waitlist(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="waitlist_entries"
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="patient_waitlist_entries"
    )
    desired_date = models.DateField()  # Date for which the patient wants an appointment
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('doctor', 'patient', 'desired_date')
    
    def __str__(self):
        return f"Waitlist Entry - Doctor: {self.doctor} Patient: {self.patient} on {self.desired_date}"
