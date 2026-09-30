from django.urls import path
from . import views

urlpatterns = [
    # Browser UI Routes
    path('mappings/', views.MappingListView.as_view(), name='mapping-list'),
    path('patients/<int:patient_id>/mappings/', views.PatientMappingManageView.as_view(), name='patient-mapping-manage'),
    path('mappings/<int:pk>/delete/', views.MappingDeleteView.as_view(), name='mapping-delete'),

    # API Routes
    path('api/mappings/', views.MappingListCreateAPIView.as_view(), name='api-mapping-list-create'),
    path('api/mappings/<int:pk>/', views.MappingSharedDetailView.as_view(), name='api-mapping-detail'),
]
