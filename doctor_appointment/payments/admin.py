from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'amount', 'currency', 'status', 'transaction_id', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('appointment__doctor__name', 'appointment__patient__name', 'transaction_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Payment, PaymentAdmin)
