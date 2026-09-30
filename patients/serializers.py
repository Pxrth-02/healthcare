from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Patient
        fields = (
            'id',
            'name',
            'email',
            'age',
            'gender',
            'phone',
            'created_by',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def validate_age(self, value):
        if value < 0 or value > 150:
            raise serializers.ValidationError('Age must be between 0 and 150.')
        return value

    def validate_gender(self, value):
        valid_choices = [choice[0] for choice in Patient.GENDER_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Gender must be one of: {', '.join(valid_choices)}.")
        return value
