import paypalrestsdk
from django.conf import settings
from rest_framework import status, views
from rest_framework.response import Response
from .models import Payment
from appointments.models import Appointment
from .serializers import PaymentSerializer

# Configure the PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # "sandbox" or "live"
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

class CreatePaymentView(views.APIView):
    """
    Create a PayPal payment for a given appointment.
    Expected payload: { "appointment_id": int, "amount": "decimal", "currency": "USD" }
    """
    def post(self, request, *args, **kwargs):
        appointment_id = request.data.get("appointment_id")
        amount = request.data.get("amount")
        currency = request.data.get("currency", "USD")
        
        # Validate appointment existence
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Create a PayPal payment object
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri('/payments/execute/'),
                "cancel_url": request.build_absolute_uri('/payments/cancel/')
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Appointment Payment (ID: {appointment.id})",
                        "sku": f"appointment_{appointment.id}",
                        "price": str(amount),
                        "currency": currency,
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(amount),
                    "currency": currency
                },
                "description": f"Payment for appointment ID {appointment.id}"
            }]
        })

        if payment.create():
            # Save the payment record with a pending status and store the PayPal payment ID
            payment_record = Payment.objects.create(
                appointment=appointment,
                amount=amount,
                currency=currency,
                status='PENDING',
                transaction_id=payment.id
            )
            # Find the approval URL from the PayPal response
            for link in payment.links:
                if link.method == "REDIRECT" and link.rel == "approval_url":
                    approval_url = str(link.href)
                    return Response({"approval_url": approval_url}, status=status.HTTP_201_CREATED)
            return Response({"detail": "Approval URL not found."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Payment creation failed.", "error": payment.error},
                            status=status.HTTP_400_BAD_REQUEST)


class ExecutePaymentView(views.APIView):
    """
    Execute a PayPal payment after the payer approves it.
    Expected payload: { "paymentId": "string", "PayerID": "string" }
    """
    def post(self, request, *args, **kwargs):
        payment_id = request.data.get("paymentId")
        payer_id = request.data.get("PayerID")
        if not payment_id or not payer_id:
            return Response({"detail": "Payment ID and Payer ID are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            # Update the Payment record in our database
            try:
                payment_record = Payment.objects.get(transaction_id=payment_id)
                payment_record.status = 'COMPLETED'
                payment_record.save()
                # Optionally, update the related appointment status here
            except Payment.DoesNotExist:
                pass
            return Response({"detail": "Payment executed successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Payment execution failed.", "error": payment.error},
                            status=status.HTTP_400_BAD_REQUEST)


class CancelPaymentView(views.APIView):
    """
    Handle canceled payments.
    """
    def get(self, request, *args, **kwargs):
        return Response({"detail": "Payment canceled."}, status=status.HTTP_200_OK)
