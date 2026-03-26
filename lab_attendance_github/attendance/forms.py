from django import forms
from .models import Lab, Student, AttendanceSession

class LabForm(forms.ModelForm):
    class Meta:
        model = Lab
        fields = ['name','lab_code','location','capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Full Stack Development'}),
            'lab_code': forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. FSD-101'}),
            'location': forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Block B, Room 201'}),
            'capacity': forms.NumberInput(attrs={'class':'form-control'}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['roll_number','name','email','department','semester','labs']
        widgets = {
            'roll_number': forms.TextInput(attrs={'class':'form-control'}),
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'department': forms.TextInput(attrs={'class':'form-control'}),
            'semester': forms.NumberInput(attrs={'class':'form-control'}),
            'labs': forms.CheckboxSelectMultiple(),
        }

class AttendanceSessionForm(forms.ModelForm):
    class Meta:
        model = AttendanceSession
        fields = ['lab','date','subject','start_time','end_time']
        widgets = {
            'lab': forms.Select(attrs={'class':'form-control'}),
            'date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'subject': forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Python Lab'}),
            'start_time': forms.TimeInput(attrs={'class':'form-control','type':'time'}),
            'end_time': forms.TimeInput(attrs={'class':'form-control','type':'time'}),
        }
