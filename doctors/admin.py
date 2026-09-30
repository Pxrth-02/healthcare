from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'experience_years', 'age', 'gender', 'phone', 'created_by', 'created_at')
    list_filter = ('specialization', 'gender', 'created_at')
    search_fields = ('name', 'specialization', 'phone')
    readonly_fields = ('created_at', 'updated_at')
