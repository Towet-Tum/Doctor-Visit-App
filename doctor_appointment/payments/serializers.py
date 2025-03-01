from rest_framework import serializers
from .models import Payment
from appointments.models import  Appointment


class PaymentSerializer(serializers.ModelSerializer):
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(),
        source='appointment',
        write_only=True
    )
    appointment_date = serializers.DateTimeField(source='appointment.appointment_date', read_only=True)
    doctor = serializers.CharField(source='appointment.doctor.name', read_only=True)
    patient = serializers.CharField(source='appointment.patient.name', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'appointment_id', 'appointment_date', 'doctor', 'patient', 'amount', 'currency', 'status', 'transaction_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'transaction_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        return Payment.objects.create(**validated_data)
