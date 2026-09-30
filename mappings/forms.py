from django import forms
from doctors.models import Doctor
from .models import PatientDoctorMapping


class AssignDoctorForm(forms.Form):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        label='Select Doctor',
        empty_label='-- Choose a Doctor to Assign --',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, patient=None, *args, **kwargs):
        self.patient = patient
        super().__init__(*args, **kwargs)
        self.fields['doctor'].label_from_instance = (
            lambda obj: f"Dr. {obj.name} - {obj.specialization} ({obj.experience_years} yr{'s' if obj.experience_years != 1 else ''} exp)"
        )

    def clean_doctor(self):
        doctor = self.cleaned_data.get('doctor')
        if self.patient and doctor:
            if PatientDoctorMapping.objects.filter(patient=self.patient, doctor=doctor).exists():
                raise forms.ValidationError(f"Dr. {doctor.name} is already assigned to this patient.")
        return doctor
