from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Doctor
        fields = (
            'id',
            'name',
            'age',
            'gender',
            'specialization',
            'phone',
            'experience_years',
            'created_by',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def validate_age(self, value):
        if value < 0 or value > 150:
            raise serializers.ValidationError('Age must be between 0 and 150.')
        return value

    def validate_experience_years(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('Experience years must be between 0 and 100.')
        return value

    def validate_gender(self, value):
        valid_choices = [choice[0] for choice in Doctor.GENDER_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Gender must be one of: {', '.join(valid_choices)}.")
        return value
