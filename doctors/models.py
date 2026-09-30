from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Doctor(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0, message='Age cannot be negative.'),
            MaxValueValidator(150, message='Age cannot exceed 150.'),
        ]
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    specialization = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    experience_years = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0, message='Experience cannot be negative.'),
            MaxValueValidator(100, message='Experience cannot exceed 100 years.'),
        ]
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctors'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
