from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser, UserSession, UserPreference


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'date_of_birth'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_email(self, value):
        """Check if email already exists"""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    
    def validate_username(self, value):
        """Check if username already exists"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Authenticate user credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('Account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'profile_picture', 'address',
            'city', 'country', 'postal_code', 'is_verified', 'date_joined'
        ]
        read_only_fields = ['id', 'username', 'is_verified', 'date_joined']
    
    def get_full_name(self, obj):
        """Get user's full name"""
        return f"{obj.first_name} {obj.last_name}".strip()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'profile_picture', 'address', 'city', 'country', 'postal_code'
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Invalid phone number format")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate password change"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        """Check if old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user sessions"""
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'device_info', 'ip_address', 'location',
            'is_active', 'created_at', 'last_activity'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity']


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user preferences"""
    
    class Meta:
        model = UserPreference
        fields = [
            'id', 'language', 'timezone', 'currency', 'notifications_email',
            'notifications_sms', 'notifications_push', 'marketing_emails',
            'theme', 'date_format', 'time_format'
        ]
        read_only_fields = ['id']


class UserDashboardSerializer(serializers.ModelSerializer):
    """Serializer for user dashboard data"""
    full_name = serializers.SerializerMethodField()
    total_bookings = serializers.SerializerMethodField()
    active_bookings = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    preferences = UserPreferenceSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'full_name', 'email', 'profile_picture',
            'is_verified', 'total_bookings', 'active_bookings', 'total_spent',
            'preferences', 'date_joined'
        ]
    
    def get_full_name(self, obj):
        """Get user's full name"""
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def get_total_bookings(self, obj):
        """Get total number of bookings"""
        return obj.bookings.count()
    
    def get_active_bookings(self, obj):
        """Get number of active bookings"""
        return obj.bookings.filter(status__in=['confirmed', 'active']).count()
    
    def get_total_spent(self, obj):
        """Get total amount spent"""
        from django.db.models import Sum
        total = obj.bookings.filter(
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total']
        return float(total) if total else 0.0
