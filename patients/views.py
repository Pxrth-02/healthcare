from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from rest_framework import generics, permissions

from .forms import PatientForm
from .models import Patient
from .serializers import PatientSerializer


# ==============================================================================
# API Views (JWT Authenticated)
# ==============================================================================

class PatientListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)


# ==============================================================================
# Browser UI Views (Session Authenticated)
# ==============================================================================

class PatientListView(LoginRequiredMixin, View):
    def get(self, request):
        patients = Patient.objects.filter(created_by=request.user)
        return render(request, 'patients/patient_list.html', {'patients': patients})


class PatientCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = PatientForm()
        return render(request, 'patients/patient_form.html', {
            'form': form,
            'title': 'Add Patient',
            'button_text': 'Save Patient',
        })

    def post(self, request):
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            messages.success(request, f'Patient "{patient.name}" created successfully.')
            return redirect('patient-list')
        return render(request, 'patients/patient_form.html', {
            'form': form,
            'title': 'Add Patient',
            'button_text': 'Save Patient',
        })


class PatientUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        form = PatientForm(instance=patient)
        return render(request, 'patients/patient_form.html', {
            'form': form,
            'title': 'Edit Patient',
            'button_text': 'Update Patient',
            'patient': patient,
        })

    def post(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f'Patient "{patient.name}" updated successfully.')
            return redirect('patient-list')
        return render(request, 'patients/patient_form.html', {
            'form': form,
            'title': 'Edit Patient',
            'button_text': 'Update Patient',
            'patient': patient,
        })


class PatientDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        return render(request, 'patients/patient_confirm_delete.html', {'patient': patient})

    def post(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        name = patient.name
        patient.delete()
        messages.success(request, f'Patient record for "{name}" was successfully deleted.')
        return redirect('patient-list')
