from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    # Browser UI Routes
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='root'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # API Authentication Routes
    path('api/auth/register/', views.RegisterAPIView.as_view(), name='api-register'),
    path('api/auth/login/', views.LoginAPIView.as_view(), name='api-login'),
]
