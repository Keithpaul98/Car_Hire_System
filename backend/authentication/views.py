from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login, logout
from django.utils import timezone
from django.db.models import Q
from .models import CustomUser, UserSession, UserPreference
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, PasswordChangeSerializer, UserSessionSerializer,
    UserPreferenceSerializer, UserDashboardSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """API view for user registration"""
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Allow GET requests to show the form in browsable API"""
        serializer = self.get_serializer()
        return Response({
            'message': 'User Registration Endpoint',
            'required_fields': {
                'username': 'string (required)',
                'email': 'string (required)',
                'password': 'string (required)',
                'password_confirm': 'string (required)',
                'first_name': 'string (optional)',
                'last_name': 'string (optional)',
                'phone_number': 'string (optional)',
                'date_of_birth': 'date (optional, format: YYYY-MM-DD)'
            },
            'example_request': {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'password_confirm': 'TestPass123!',
                'first_name': 'Test',
                'last_name': 'User',
                'phone_number': '+1234567890'
            }
        })
    
    def create(self, request, *args, **kwargs):
        """Create new user and return tokens"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create user preferences
        UserPreference.objects.create(user=user)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Create user session
        UserSession.objects.create(
            user=user,
            session_key=request.session.session_key or 'api_session',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_type=self.get_device_info(request)
        )
        
        return Response({
            'message': 'User registered successfully',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with additional user data"""
    
    def post(self, request, *args, **kwargs):
        """Login user and return tokens with user data"""
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user from username
            username = request.data.get('username')
            try:
                user = CustomUser.objects.get(
                    Q(username=username) | Q(email=username)
                )
                
                # Update last login
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                
                # Create or update user session
                session, created = UserSession.objects.get_or_create(
                    user=user,
                    device_type=request.META.get('HTTP_USER_AGENT', ''),
                    defaults={
                        'session_key': 'api_session',
                        'ip_address': self.get_client_ip(request),
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'location': 'Unknown'
                    }
                )
                if not created:
                    session.last_activity = timezone.now()
                    session.is_active = True
                    session.save()
                
                # Add user data to response
                response.data['user'] = UserProfileSerializer(user).data
                response.data['message'] = 'Login successful'
                
            except CustomUser.DoesNotExist:
                pass
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(generics.RetrieveUpdateAPIView):
    """API view for user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Return current user"""
        return self.request.user
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method"""
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserProfileUpdateSerializer
        return UserProfileSerializer


class UserDashboardView(generics.RetrieveAPIView):
    """API view for user dashboard data"""
    serializer_class = UserDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Return current user with related data"""
        return self.request.user


class PasswordChangeView(APIView):
    """API view for password change"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserSessionsView(generics.ListAPIView):
    """API view for user sessions"""
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return user's sessions"""
        return UserSession.objects.filter(
            user=self.request.user
        ).order_by('-last_activity')


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """API view for user preferences"""
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create user preferences"""
        preferences, created = UserPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences


class LogoutView(APIView):
    """API view for user logout"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Logout user and deactivate session"""
        try:
            # Deactivate user session
            UserSession.objects.filter(
                user=request.user,
                is_active=True
            ).update(is_active=False)
            
            # Blacklist refresh token if provided
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    pass
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Logout failed'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_verification_status(request):
    """Get user verification status"""
    user = request.user
    return Response({
        'is_verified': user.is_verified,
        'verification_level': user.verification_level,
        'verification_date': user.verification_date,
        'required_documents': [
            'Driver License',
            'Identity Document',
            'Proof of Address'
        ] if not user.is_verified else []
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def request_verification(request):
    """Request account verification"""
    user = request.user
    
    if user.is_verified:
        return Response({
            'message': 'Account is already verified'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Here you would implement document upload and verification logic
    # For now, we'll just update the verification level
    user.verification_level = 'pending'
    user.save()
    
    return Response({
        'message': 'Verification request submitted successfully',
        'status': 'pending'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_username_availability(request):
    """Check if username is available"""
    username = request.GET.get('username')
    if not username:
        return Response({
            'error': 'Username parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    is_available = not CustomUser.objects.filter(username=username).exists()
    
    return Response({
        'username': username,
        'is_available': is_available
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_email_availability(request):
    """Check if email is available"""
    email = request.GET.get('email')
    if not email:
        return Response({
            'error': 'Email parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    is_available = not CustomUser.objects.filter(email=email).exists()
    
    return Response({
        'email': email,
        'is_available': is_available
    })
