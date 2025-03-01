from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment

@shared_task
def send_payment_confirmation(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        send_mail(
            'Payment Confirmation',
            f'Your payment for appointment {payment.appointment.id} has been completed successfully.',
            settings.DEFAULT_FROM_EMAIL,
            [payment.appointment.patient.email],
            fail_silently=False,
        )
    except Payment.DoesNotExist:
        pass
