from rest_framework import serializers
from doctors.models import Doctor
from patients.models import Patient
from .models import PatientDoctorMapping


class DoctorNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = (
            'id',
            'name',
            'specialization',
            'experience_years',
            'age',
            'gender',
            'phone',
        )


class PatientNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'name', 'email')


class MappingReadSerializer(serializers.ModelSerializer):
    patient = PatientNestedSerializer(read_only=True)
    doctor = DoctorNestedSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ('id', 'patient', 'doctor', 'assigned_at')


class MappingCreateSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())

    class Meta:
        model = PatientDoctorMapping
        fields = ('id', 'patient', 'doctor', 'assigned_at')
        read_only_fields = ('id', 'assigned_at')

    def validate_patient(self, value):
        request = self.context.get('request')
        if not request or value.created_by != request.user:
            raise serializers.ValidationError('Patient does not exist or does not belong to your account.')
        return value

    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError('This doctor is already assigned to this patient.')

        return attrs

    def to_representation(self, instance):
        return MappingReadSerializer(instance).data
