from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Appointment, Waitlist
from django.utils.dateparse import parse_datetime

@shared_task
def notify_availability(doctor_id, appointment_date_iso):
    appointment_date = parse_datetime(appointment_date_iso)
    # Query waitlist for patients interested in the specific date.
    waitlist_entries = Waitlist.objects.filter(
        doctor_id=doctor_id, 
        desired_date=appointment_date.date()
    )
    for entry in waitlist_entries:
        send_mail(
            'Appointment Slot Available',
            f'Dear {entry.patient.username},\n\nA slot has opened up on {appointment_date} with your desired doctor. Please log in to book your appointment.',
            settings.DEFAULT_FROM_EMAIL,
            [entry.patient.email],
            fail_silently=False,
        )

@shared_task
def notify_reschedule(appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        send_mail(
            'Appointment Rescheduled',
            f'Your appointment with Dr. {appointment.doctor} has been rescheduled to {appointment.appointment_date}.',
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.email],
            fail_silently=False,
        )
    except Appointment.DoesNotExist:
        pass

@shared_task
def notify_doctor_cancellation(appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        send_mail(
            'Appointment Canceled by Doctor',
            f'Your appointment with Dr. {appointment.doctor} on {appointment.appointment_date} has been canceled by the doctor.',
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.email],
            fail_silently=False,
        )
    except Appointment.DoesNotExist:
        pass
