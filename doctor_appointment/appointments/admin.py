

from django.contrib import admin
from .models import Appointment

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'appointment_date', 'status')
    list_filter = ('doctor', 'status', 'appointment_date')
    search_fields = ('doctor__name', 'patient__name', 'appointment_date')
    ordering = ('-appointment_date',)
    date_hierarchy = 'appointment_date'
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Appointment, AppointmentAdmin)
