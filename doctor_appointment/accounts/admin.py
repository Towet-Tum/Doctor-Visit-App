from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DoctorProfile, PatientProfile

class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Doctor Profile'
    fk_name = 'user'

class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    verbose_name_plural = 'Patient Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Dynamically include the inline based on the user's role.
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        if obj.role == 'doctor':
            return [DoctorProfileInline(self.model, self.admin_site)]
        elif obj.role == 'patient':
            return [PatientProfileInline(self.model, self.admin_site)]
        return []

admin.site.register(CustomUser, CustomUserAdmin)
