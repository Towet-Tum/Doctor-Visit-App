from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Appointment, Waitlist

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('status', 'created_at', 'updated_at')
    
    def validate_appointment_date(self, value):
        now = timezone.now()
        if value < now:
            raise serializers.ValidationError("Appointment date must be in the future.")
        if value > now + timedelta(days=15):
            raise serializers.ValidationError("Appointment must be within 15 days from now.")
        return value
    
    def create(self, validated_data):
        # After a successful payment in your payment app, you would confirm the appointment.
        # Here, we set the appointment status to 'CONFIRMED' by default.
        validated_data['status'] = 'CONFIRMED'
        appointment = Appointment.objects.create(**validated_data)
        return appointment

class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waitlist
        fields = '__all__'
        read_only_fields = ('patient', 'created_at')