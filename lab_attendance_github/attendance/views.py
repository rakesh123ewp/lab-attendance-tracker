from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
import csv
from .models import Lab, Student, AttendanceSession, AttendanceRecord, Holiday
from .forms import LabForm, StudentForm, AttendanceSessionForm

def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('student_id'):
            return redirect('student_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def get_student(request):
    return get_object_or_404(Student, pk=request.session['student_id'])

def student_login(request):
    if request.method == 'POST':
        roll = request.POST.get('roll_number','').strip()
        name = request.POST.get('name','').strip()
        try:
            student = Student.objects.get(roll_number__iexact=roll, name__iexact=name)
            request.session['student_id'] = student.pk
            request.session['student_name'] = student.name
            messages.success(request, f'Welcome, {student.name}!')
            return redirect('student_self_dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Invalid Roll Number or Name. Please try again.')
    return render(request, 'attendance/student_login.html')

def student_logout_view(request):
    request.session.flush()
    return redirect('student_login')

@student_required
def student_self_dashboard(request):
    student = get_student(request)
    records = student.attendance_records.select_related('session__lab').order_by('-session__date')
    total = records.count()
    present = records.filter(status='Present').count()
    percentage = round((present/total)*100,1) if total else 0
    today = timezone.now().date()
    active_sessions = AttendanceSession.objects.filter(is_active=True, date=today, lab__in=student.labs.all())
    return render(request, 'attendance/student_self_dashboard.html', {
        'student': student, 'records': records, 'total': total,
        'present': present, 'absent': total-present,
        'percentage': percentage, 'active_sessions': active_sessions,
    })

@student_required
def student_mark_self(request, session_pk):
    student = get_student(request)
    session = get_object_or_404(AttendanceSession, pk=session_pk, is_active=True)
    if not student.labs.filter(pk=session.lab.pk).exists():
        messages.error(request, 'You are not enrolled in this lab.')
        return redirect('student_self_dashboard')
    record, _ = AttendanceRecord.objects.get_or_create(session=session, student=student)
    if record.status == 'Present':
        messages.info(request, 'Already marked Present!')
        return redirect('student_self_dashboard')
    if request.method == 'POST':
        record.status = 'Present'
        record.marked_by_student = True
        record.save()
        messages.success(request, f'Attendance marked Present!')
        return redirect('student_self_dashboard')
    return render(request, 'attendance/student_mark_self.html', {'session': session, 'student': student})

@login_required
def dashboard(request):
    today = timezone.now().date()
    recent_sessions = AttendanceSession.objects.select_related('lab','conducted_by')[:5]
    holidays = Holiday.objects.filter(date__gte=today).order_by('date')[:5]
    return render(request, 'attendance/dashboard.html', {
        'total_labs': Lab.objects.count(),
        'total_students': Student.objects.count(),
        'today_sessions': AttendanceSession.objects.filter(date=today).count(),
        'total_sessions': AttendanceSession.objects.count(),
        'recent_sessions': recent_sessions,
        'holidays': holidays, 'today': today,
    })

@login_required
def holiday_list(request):
    return render(request, 'attendance/holiday_list.html', {'holidays': Holiday.objects.all().order_by('-date')})

@login_required
def holiday_create(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        reason = request.POST.get('reason','').strip()
        if date:
            h, created = Holiday.objects.get_or_create(date=date, defaults={'reason': reason, 'declared_by': request.user})
            if created: messages.success(request, f'{date} marked as Holiday!')
            else: messages.warning(request, f'{date} is already a holiday.')
        return redirect('holiday_list')
    return render(request, 'attendance/holiday_form.html')

@login_required
def holiday_delete(request, pk):
    h = get_object_or_404(Holiday, pk=pk)
    if request.method == 'POST':
        h.delete()
        messages.success(request, 'Holiday removed.')
        return redirect('holiday_list')
    return render(request, 'attendance/confirm_delete.html', {'object': h, 'type': 'Holiday'})

@login_required
def lab_list(request):
    return render(request, 'attendance/lab_list.html', {'labs': Lab.objects.annotate(student_count=Count('students'))})

@login_required
def lab_create(request):
    form = LabForm(request.POST or None)
    if form.is_valid(): form.save(); messages.success(request,'Lab created!'); return redirect('lab_list')
    return render(request, 'attendance/lab_form.html', {'form': form, 'title': 'Add Lab'})

@login_required
def lab_edit(request, pk):
    lab = get_object_or_404(Lab, pk=pk)
    form = LabForm(request.POST or None, instance=lab)
    if form.is_valid(): form.save(); messages.success(request,'Lab updated!'); return redirect('lab_list')
    return render(request, 'attendance/lab_form.html', {'form': form, 'title': 'Edit Lab'})

@login_required
def lab_delete(request, pk):
    lab = get_object_or_404(Lab, pk=pk)
    if request.method == 'POST': lab.delete(); messages.success(request,'Lab deleted.'); return redirect('lab_list')
    return render(request, 'attendance/confirm_delete.html', {'object': lab, 'type': 'Lab'})

@login_required
def student_list(request):
    q = request.GET.get('q','')
    students = Student.objects.filter(Q(name__icontains=q)|Q(roll_number__icontains=q)) if q else Student.objects.all()
    return render(request, 'attendance/student_list.html', {'students': students, 'q': q})

@login_required
def student_create(request):
    form = StudentForm(request.POST or None)
    if form.is_valid(): form.save(); messages.success(request,'Student added!'); return redirect('student_list')
    return render(request, 'attendance/student_form.html', {'form': form, 'title': 'Add Student'})

@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid(): form.save(); messages.success(request,'Student updated!'); return redirect('student_list')
    return render(request, 'attendance/student_form.html', {'form': form, 'title': 'Edit Student'})

@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST': student.delete(); messages.success(request,'Student deleted.'); return redirect('student_list')
    return render(request, 'attendance/confirm_delete.html', {'object': student, 'type': 'Student'})

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    records = student.attendance_records.select_related('session__lab').order_by('-session__date')
    total = records.count(); present = records.filter(status='Present').count()
    return render(request, 'attendance/student_detail.html', {
        'student': student, 'records': records, 'total': total,
        'present': present, 'percentage': round((present/total)*100,1) if total else 0
    })

@login_required
def session_list(request):
    sessions = AttendanceSession.objects.select_related('lab','conducted_by')
    lab_filter = request.GET.get('lab'); date_filter = request.GET.get('date')
    if lab_filter: sessions = sessions.filter(lab_id=lab_filter)
    if date_filter: sessions = sessions.filter(date=date_filter)
    return render(request, 'attendance/session_list.html', {
        'sessions': sessions, 'labs': Lab.objects.all(),
        'lab_filter': lab_filter, 'date_filter': date_filter,
    })

@login_required
def session_create(request):
    form = AttendanceSessionForm(request.POST or None, initial={'date': timezone.now().date()})
    if form.is_valid():
        date = form.cleaned_data['date']
        if Holiday.objects.filter(date=date).exists():
            h = Holiday.objects.get(date=date)
            messages.error(request, f'{date} is a Holiday: {h.reason}')
            return render(request, 'attendance/session_form.html', {'form': form, 'title': 'New Session'})
        session = form.save(commit=False); session.conducted_by = request.user; session.save()
        for student in session.lab.students.all():
            AttendanceRecord.objects.get_or_create(session=session, student=student)
        messages.success(request,'Session created!')
        return redirect('mark_attendance', pk=session.pk)
    return render(request, 'attendance/session_form.html', {'form': form, 'title': 'New Session'})

@login_required
def session_toggle_active(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    if request.method == 'POST':
        session.is_active = not session.is_active; session.save()
        messages.success(request, f'Session {"OPEN for students" if session.is_active else "CLOSED"}.')
    return redirect('session_detail', pk=session.pk)

@login_required
def mark_attendance(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    for student in session.lab.students.all():
        AttendanceRecord.objects.get_or_create(session=session, student=student)
    if request.method == 'POST':
        present_ids = request.POST.getlist('present')
        for record in session.records.all():
            record.status = 'Present' if str(record.student.pk) in present_ids else 'Absent'; record.save()
        messages.success(request,'Attendance saved!'); return redirect('session_detail', pk=session.pk)
    records = session.records.select_related('student').order_by('student__roll_number')
    return render(request, 'attendance/mark_attendance.html', {'session': session, 'records': records})

@login_required
def ajax_update_record(request):
    if request.method == 'POST':
        record = get_object_or_404(AttendanceRecord, pk=request.POST.get('record_id'))
        status = request.POST.get('status')
        if status not in ['Present','Absent']: return JsonResponse({'success': False})
        record.status = status; record.save()
        s = record.session
        return JsonResponse({'success': True, 'status': record.status,
            'present_count': s.present_count(), 'absent_count': s.absent_count(), 'percentage': s.attendance_percentage()})
    return JsonResponse({'success': False})

@login_required
def session_detail(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    records = session.records.select_related('student').order_by('student__roll_number')
    return render(request, 'attendance/session_detail.html', {'session': session, 'records': records})

@login_required
def session_delete(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    if request.method == 'POST': session.delete(); messages.success(request,'Session deleted.'); return redirect('session_list')
    return render(request, 'attendance/confirm_delete.html', {'object': session, 'type': 'Session'})

@login_required
def reports(request):
    labs = Lab.objects.all(); selected_lab = request.GET.get('lab')
    start_date = request.GET.get('start_date'); end_date = request.GET.get('end_date')
    sessions = AttendanceSession.objects.select_related('lab')
    if selected_lab: sessions = sessions.filter(lab_id=selected_lab)
    if start_date: sessions = sessions.filter(date__gte=start_date)
    if end_date: sessions = sessions.filter(date__lte=end_date)
    return render(request, 'attendance/reports.html', {
        'labs': labs, 'sessions': sessions, 'selected_lab': selected_lab,
        'start_date': start_date, 'end_date': end_date,
    })

@login_required
def export_csv(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    records = session.records.select_related('student').order_by('student__roll_number')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{session.lab.lab_code}_{session.date}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Roll No','Student Name','Department','Semester','Status','Marked By'])
    for r in records:
        writer.writerow([r.student.roll_number, r.student.name, r.student.department,
                         r.student.semester, r.status, 'Student' if r.marked_by_student else 'Teacher'])
    return response
