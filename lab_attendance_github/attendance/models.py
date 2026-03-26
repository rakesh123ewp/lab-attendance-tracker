from django.db import models
from django.contrib.auth.models import User

class Lab(models.Model):
    name = models.CharField(max_length=100)
    lab_code = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.name} ({self.lab_code})"
    class Meta: ordering = ['name']

class Student(models.Model):
    roll_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    department = models.CharField(max_length=100, blank=True)
    semester = models.PositiveIntegerField(default=1)
    labs = models.ManyToManyField(Lab, related_name='students', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.roll_number} - {self.name}"
    class Meta: ordering = ['roll_number']

class Holiday(models.Model):
    date = models.DateField(unique=True)
    reason = models.CharField(max_length=200)
    declared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.date} - {self.reason}"
    class Meta: ordering = ['-date']

class AttendanceSession(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateField()
    subject = models.CharField(max_length=100, blank=True)
    conducted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.lab} - {self.date} - {self.subject}"
    def total_students(self): return self.records.count()
    def present_count(self): return self.records.filter(status='Present').count()
    def absent_count(self): return self.records.filter(status='Absent').count()
    def attendance_percentage(self):
        total = self.total_students()
        return round((self.present_count()/total)*100,1) if total else 0
    class Meta: ordering = ['-date','-created_at']

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [('Present','Present'),('Absent','Absent')]
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Absent')
    marked_by_student = models.BooleanField(default=False)
    remarks = models.CharField(max_length=200, blank=True)
    marked_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"{self.student.name} - {self.session.date} - {self.status}"
    class Meta:
        unique_together = ['session','student']
        ordering = ['student__roll_number']
