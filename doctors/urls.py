from django.urls import path
from . import views

urlpatterns = [
    # Browser UI Routes
    path('doctors/', views.DoctorListView.as_view(), name='doctor-list'),
    path('doctors/create/', views.DoctorCreateView.as_view(), name='doctor-create'),
    path('doctors/<int:pk>/edit/', views.DoctorUpdateView.as_view(), name='doctor-edit'),
    path('doctors/<int:pk>/delete/', views.DoctorDeleteView.as_view(), name='doctor-delete'),

    # API Routes
    path('api/doctors/', views.DoctorListCreateAPIView.as_view(), name='api-doctor-list-create'),
    path('api/doctors/<int:pk>/', views.DoctorDetailAPIView.as_view(), name='api-doctor-detail'),
]
