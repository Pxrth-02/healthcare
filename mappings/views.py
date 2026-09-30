from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from patients.models import Patient
from .forms import AssignDoctorForm
from .models import PatientDoctorMapping
from .serializers import MappingCreateSerializer, MappingReadSerializer


# ==============================================================================
# API Views (JWT Authenticated)
# ==============================================================================

class MappingListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MappingCreateSerializer
        return MappingReadSerializer

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related('doctor', 'patient')


class MappingSharedDetailView(APIView):
    """
    Handles the project's shared URL parameter convention:
    - GET /api/mappings/<pk>/    -> pk represents patient_id (returns mappings for this patient)
    - DELETE /api/mappings/<pk>/ -> pk represents mapping_id (deletes this specific mapping)
    Both operations require the associated patient to belong to request.user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor', 'patient')
        serializer = MappingReadSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        mapping = get_object_or_404(PatientDoctorMapping, pk=pk, patient__created_by=request.user)
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# Browser UI Views (Session Authenticated)
# ==============================================================================

class MappingListView(LoginRequiredMixin, View):
    """
    Overview of all active assignments across all of the current user's patients.
    """
    def get(self, request):
        mappings = PatientDoctorMapping.objects.filter(
            patient__created_by=request.user
        ).select_related('patient', 'doctor')
        return render(request, 'mappings/mapping_list.html', {'mappings': mappings})


class PatientMappingManageView(LoginRequiredMixin, View):
    """
    Focused view to manage doctor assignments for a specific patient of the current user.
    """
    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id, created_by=request.user)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')
        form = AssignDoctorForm(patient=patient)
        return render(request, 'mappings/patient_mapping.html', {
            'patient': patient,
            'mappings': mappings,
            'form': form,
        })

    def post(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id, created_by=request.user)
        form = AssignDoctorForm(patient=patient, data=request.POST)
        if form.is_valid():
            doctor = form.cleaned_data['doctor']
            PatientDoctorMapping.objects.create(patient=patient, doctor=doctor)
            messages.success(request, f'Dr. {doctor.name} was successfully assigned to {patient.name}.')
            return redirect('patient-mapping-manage', patient_id=patient.id)

        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')
        return render(request, 'mappings/patient_mapping.html', {
            'patient': patient,
            'mappings': mappings,
            'form': form,
        })


class MappingDeleteView(LoginRequiredMixin, View):
    """
    Confirmation and deletion of a doctor assignment.
    """
    def get(self, request, pk):
        mapping = get_object_or_404(PatientDoctorMapping, pk=pk, patient__created_by=request.user)
        return render(request, 'mappings/mapping_confirm_delete.html', {'mapping': mapping})

    def post(self, request, pk):
        mapping = get_object_or_404(PatientDoctorMapping, pk=pk, patient__created_by=request.user)
        patient_id = mapping.patient.id
        doc_name = mapping.doctor.name
        patient_name = mapping.patient.name
        mapping.delete()
        messages.success(request, f'Assignment between {patient_name} and Dr. {doc_name} was removed.')
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('patient-mapping-manage', patient_id=patient_id)
