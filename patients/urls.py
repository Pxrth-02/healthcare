from django.urls import path
from . import views

urlpatterns = [
    # Browser UI Routes
    path('patients/', views.PatientListView.as_view(), name='patient-list'),
    path('patients/create/', views.PatientCreateView.as_view(), name='patient-create'),
    path('patients/<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient-edit'),
    path('patients/<int:pk>/delete/', views.PatientDeleteView.as_view(), name='patient-delete'),

    # API Routes
    path('api/patients/', views.PatientListCreateAPIView.as_view(), name='api-patient-list-create'),
    path('api/patients/<int:pk>/', views.PatientDetailAPIView.as_view(), name='api-patient-detail'),
]
