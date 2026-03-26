from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import Lab, Student, AttendanceSession, AttendanceRecord
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seed sample data'
    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@lab.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created: admin / admin123'))
        lab1, _ = Lab.objects.get_or_create(name='Full Stack Development', lab_code='FSD-101', defaults={'location': 'Block B, Room 201', 'capacity': 30})
        lab2, _ = Lab.objects.get_or_create(name='Network Lab', lab_code='NET-201', defaults={'location': 'Block C, Room 101', 'capacity': 25})
        students_data = [
            ('499CS23007', 'Chandan K', 'CS', 4),
            ('499CS23011', 'Hemanth H', 'CS', 4),
            ('499CS23028', 'Rakesh M',  'CS', 4),
            ('499CS23033', 'Siddhartha','CS', 4),
            ('499CS23034', 'Sohaan J',  'CS', 4),
        ]
        students = []
        for roll, name, dept, sem in students_data:
            s, _ = Student.objects.get_or_create(roll_number=roll, defaults={'name': name, 'department': dept, 'semester': sem})
            s.labs.add(lab1, lab2)
            students.append(s)
        admin_user = User.objects.get(username='admin')
        session, _ = AttendanceSession.objects.get_or_create(
            lab=lab1, date=timezone.now().date(), subject='Python Lab',
            defaults={'conducted_by': admin_user}
        )
        statuses = ['Absent', 'Present', 'Present', 'Absent', 'Present']
        for student, status in zip(students, statuses):
            AttendanceRecord.objects.get_or_create(session=session, student=student, defaults={'status': status})
        self.stdout.write(self.style.SUCCESS('Done! Login: admin / admin123'))
        self.stdout.write(self.style.SUCCESS('Student login → Roll: 499CS23028  Name: Rakesh M'))
