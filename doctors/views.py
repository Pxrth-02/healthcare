from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from rest_framework import generics, permissions

from .forms import DoctorForm
from .models import Doctor
from .permissions import IsCreatorOrReadOnly
from .serializers import DoctorSerializer


# ==============================================================================
# API Views (JWT Authenticated)
# ==============================================================================

class DoctorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]


# ==============================================================================
# Browser UI Views (Session Authenticated)
# ==============================================================================

class DoctorListView(LoginRequiredMixin, View):
    def get(self, request):
        doctors = Doctor.objects.all()
        return render(request, 'doctors/doctor_list.html', {'doctors': doctors})


class DoctorCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = DoctorForm()
        return render(request, 'doctors/doctor_form.html', {
            'form': form,
            'title': 'Add Doctor',
            'button_text': 'Save Doctor',
        })

    def post(self, request):
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.created_by = request.user
            doctor.save()
            messages.success(request, f'Doctor record for "{doctor.name}" created successfully.')
            return redirect('doctor-list')
        return render(request, 'doctors/doctor_form.html', {
            'form': form,
            'title': 'Add Doctor',
            'button_text': 'Save Doctor',
        })


class DoctorUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        if doctor.created_by != request.user:
            raise PermissionDenied("You do not have permission to edit this doctor record.")

        form = DoctorForm(instance=doctor)
        return render(request, 'doctors/doctor_form.html', {
            'form': form,
            'title': 'Edit Doctor',
            'button_text': 'Update Doctor',
            'doctor': doctor,
        })

    def post(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        if doctor.created_by != request.user:
            raise PermissionDenied("You do not have permission to edit this doctor record.")

        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Doctor record for "{doctor.name}" updated successfully.')
            return redirect('doctor-list')
        return render(request, 'doctors/doctor_form.html', {
            'form': form,
            'title': 'Edit Doctor',
            'button_text': 'Update Doctor',
            'doctor': doctor,
        })


class DoctorDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        if doctor.created_by != request.user:
            raise PermissionDenied("You do not have permission to delete this doctor record.")

        return render(request, 'doctors/doctor_confirm_delete.html', {'doctor': doctor})

    def post(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        if doctor.created_by != request.user:
            raise PermissionDenied("You do not have permission to delete this doctor record.")

        name = doctor.name
        doctor.delete()
        messages.success(request, f'Doctor record for "{name}" was successfully deleted.')
        return redirect('doctor-list')
