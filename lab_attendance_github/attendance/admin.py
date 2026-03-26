from django.contrib import admin
from .models import Lab, Student, AttendanceSession, AttendanceRecord, Holiday

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ['name','lab_code','location','capacity']
    search_fields = ['name','lab_code']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number','name','department','semester']
    search_fields = ['name','roll_number']
    filter_horizontal = ['labs']

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['date','reason','declared_by']

class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['lab','date','subject','is_active','conducted_by']
    list_filter = ['lab','date','is_active']
    inlines = [AttendanceRecordInline]

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student','session','status','marked_by_student']
    list_filter = ['status','marked_by_student']
