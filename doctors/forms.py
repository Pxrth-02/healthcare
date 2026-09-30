from django import forms
from .models import Doctor


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ('name', 'specialization', 'experience_years', 'age', 'gender', 'phone')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Doctor Full Name'}),
            'specialization': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Cardiology, Pediatrics'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Years of Experience', 'min': '0', 'max': '100'}),
            'age': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Age', 'min': '0', 'max': '150'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
        }

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and (age < 0 or age > 150):
            raise forms.ValidationError('Age must be between 0 and 150.')
        return age

    def clean_experience_years(self):
        exp = self.cleaned_data.get('experience_years')
        if exp is not None and (exp < 0 or exp > 100):
            raise forms.ValidationError('Experience years must be between 0 and 100.')
        return exp
