from rest_framework import serializers
from .models import CustomUser, PatientProfile, DoctorProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'role')
    
    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'patient')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ['specialty', 'experience_years', 'max_appointments', 'current_appointments']

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'medical_history']

class CustomUserSerializer(serializers.ModelSerializer):
    # Include profile data based on role. They are read-only here.
    doctor_profile = DoctorProfileSerializer(read_only=True)
    patient_profile = PatientProfileSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'doctor_profile', 'patient_profile']
