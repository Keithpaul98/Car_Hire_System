from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # User sessions and preferences
    path('sessions/', views.UserSessionsView.as_view(), name='sessions'),
    path('preferences/', views.UserPreferencesView.as_view(), name='preferences'),
    
    # Verification endpoints
    path('verification/status/', views.user_verification_status, name='verification_status'),
    path('verification/request/', views.request_verification, name='request_verification'),
    
    # Utility endpoints
    path('check-username/', views.check_username_availability, name='check_username'),
    path('check-email/', views.check_email_availability, name='check_email'),
]
