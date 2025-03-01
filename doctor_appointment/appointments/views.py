from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Appointment
from .serializers import AppointmentSerializer, WaitlistSerializer
from rest_framework import generics

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Assuming your user model has an attribute "is_doctor" to differentiate roles.
        if getattr(user, "is_doctor", False):
            # For doctors, return appointments where they are the assigned doctor.
            return Appointment.objects.filter(doctor=user).select_related('patient')
        # For patients, return appointments where they are the patient.
        return Appointment.objects.filter(patient=user).select_related('doctor')
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        # For patients: ensure cancellation is only allowed more than 3 days before the appointment.
        if not appointment.can_cancel():
            return Response({"detail": "Cannot cancel appointment within 3 days of the scheduled time."},
                            status=status.HTTP_400_BAD_REQUEST)
        appointment.status = 'CANCELED'
        appointment.save()
        # Trigger Celery task to notify waitlisted patients about the available slot.
        from .tasks import notify_availability
        notify_availability.delay(appointment.doctor.id, appointment.appointment_date.isoformat())
        return Response({"detail": "Appointment canceled successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
        new_date = request.data.get('appointment_date')
        if not new_date:
            return Response({"detail": "New appointment date is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_date_parsed = timezone.datetime.fromisoformat(new_date)
            if timezone.is_naive(new_date_parsed):
                new_date_parsed = timezone.make_aware(new_date_parsed)
        except Exception:
            return Response({"detail": "Invalid date format. Use ISO format."}, status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        if new_date_parsed < now:
            return Response({"detail": "New appointment date must be in the future."}, status=status.HTTP_400_BAD_REQUEST)
        if new_date_parsed > now + timedelta(days=15):
            return Response({"detail": "New appointment date must be within 15 days."}, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.appointment_date = new_date_parsed
        appointment.status = 'RESCHEDULED'
        appointment.save()
        from .tasks import notify_reschedule
        notify_reschedule.delay(appointment.id)
        return Response({"detail": "Appointment rescheduled successfully."}, status=status.HTTP_200_OK)
    
    # Doctor-specific actions
    @action(detail=True, methods=['post'])
    def doctor_cancel(self, request, pk=None):
        appointment = self.get_object()
        if request.user != appointment.doctor:
            return Response({"detail": "Only the assigned doctor can perform this action."},
                            status=status.HTTP_403_FORBIDDEN)
        appointment.status = 'CANCELED'
        appointment.save()
        from .tasks import notify_doctor_cancellation
        notify_doctor_cancellation.delay(appointment.id)
        return Response({"detail": "Appointment canceled by doctor."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def doctor_bulk_cancel(self, request):
        if not getattr(request.user, "is_doctor", False):
            return Response({"detail": "Only doctors can perform bulk cancellation."},
                            status=status.HTTP_403_FORBIDDEN)
        # Optional filters: patient_id and/or a specific date.
        patient_id = request.data.get('patient_id')
        cancel_date = request.data.get('cancel_date')
        qs = Appointment.objects.filter(doctor=request.user)
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        if cancel_date:
            qs = qs.filter(appointment_date__date=cancel_date)
        appointments = list(qs)
        count = qs.update(status='CANCELED')
        from .tasks import notify_doctor_cancellation
        for appointment in appointments:
            notify_doctor_cancellation.delay(appointment.id)
        return Response({"detail": f"Canceled {count} appointments."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def doctor_reschedule(self, request, pk=None):
        appointment = self.get_object()
        if request.user != appointment.doctor:
            return Response({"detail": "Only the assigned doctor can reschedule this appointment."},
                            status=status.HTTP_403_FORBIDDEN)
        new_date = request.data.get('appointment_date')
        if not new_date:
            return Response({"detail": "New appointment date is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_date_parsed = timezone.datetime.fromisoformat(new_date)
            if timezone.is_naive(new_date_parsed):
                new_date_parsed = timezone.make_aware(new_date_parsed)
        except Exception:
            return Response({"detail": "Invalid date format. Use ISO format."}, status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        if new_date_parsed < now:
            return Response({"detail": "New appointment date must be in the future."}, status=status.HTTP_400_BAD_REQUEST)
        if new_date_parsed > now + timedelta(days=15):
            return Response({"detail": "New appointment date must be within 15 days."}, status=status.HTTP_400_BAD_REQUEST)
        appointment.appointment_date = new_date_parsed
        appointment.status = 'RESCHEDULED'
        appointment.save()
        from .tasks import notify_reschedule
        notify_reschedule.delay(appointment.id)
        return Response({"detail": "Appointment rescheduled by doctor."}, status=status.HTTP_200_OK)


class WaitlistEntryCreateView(generics.CreateAPIView):
    serializer_class = WaitlistSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)