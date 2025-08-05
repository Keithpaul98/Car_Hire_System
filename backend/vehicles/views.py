from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import (
    Vehicle, VehicleCategory, VehicleBrand, VehicleModel, 
    VehicleFeature, VehicleImage, VehicleMaintenanceRecord
)
from .serializers import (
    VehicleSerializer, VehicleCategorySerializer, VehicleBrandSerializer,
    VehicleModelSerializer, VehicleFeatureSerializer, VehicleImageSerializer,
    VehicleMaintenanceRecordSerializer, VehicleSearchSerializer
)


class VehicleListView(generics.ListCreateAPIView):
    """API view for listing and creating vehicles"""
    queryset = Vehicle.objects.filter(is_active=True).select_related(
        'model__brand', 'model__category'
    ).prefetch_related('feature_assignments__feature', 'images')
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'fuel_type', 'transmission', 'seating_capacity', 'model__category']
    search_fields = ['model__brand__name', 'model__name', 'license_plate', 'color']
    ordering_fields = ['daily_rate', 'year', 'current_mileage', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter vehicles based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by availability
        available_only = self.request.query_params.get('available_only', None)
        if available_only == 'true':
            queryset = queryset.filter(status='available')
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if min_price:
            queryset = queryset.filter(daily_rate__gte=min_price)
        if max_price:
            queryset = queryset.filter(daily_rate__lte=max_price)
        
        # Filter by location
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(current_location__icontains=location)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the created_by field to current user"""
        serializer.save(created_by=self.request.user)


class VehicleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting a specific vehicle"""
    queryset = Vehicle.objects.filter(is_active=True).select_related(
        'model__brand', 'model__category'
    ).prefetch_related('feature_assignments__feature', 'images')
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        """Set the updated_by field to current user"""
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete by setting is_active to False"""
        instance.is_active = False
        instance.save()


class VehicleCategoryListView(generics.ListCreateAPIView):
    """API view for vehicle categories"""
    queryset = VehicleCategory.objects.filter(is_active=True)
    serializer_class = VehicleCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['sort_order', 'name']


class VehicleBrandListView(generics.ListCreateAPIView):
    """API view for vehicle brands"""
    queryset = VehicleBrand.objects.filter(is_active=True)
    serializer_class = VehicleBrandSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['name']


class VehicleModelListView(generics.ListCreateAPIView):
    """API view for vehicle models"""
    queryset = VehicleModel.objects.filter(is_active=True).select_related('brand', 'category')
    serializer_class = VehicleModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['brand', 'category', 'is_active']
    ordering = ['brand__name', 'name']


class VehicleFeatureListView(generics.ListCreateAPIView):
    """API view for vehicle features"""
    queryset = VehicleFeature.objects.filter(is_active=True)
    serializer_class = VehicleFeatureSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_premium', 'is_active']
    ordering = ['category', 'name']


class VehicleSearchView(APIView):
    """Advanced vehicle search with multiple criteria"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Search vehicles with complex criteria"""
        serializer = VehicleSearchSerializer(data=request.data)
        if serializer.is_valid():
            # Get search criteria
            criteria = serializer.validated_data
            
            # Build query
            queryset = Vehicle.objects.filter(is_active=True).select_related(
                'model__brand', 'model__category'
            ).prefetch_related('feature_assignments__feature', 'images')
            
            # Apply filters
            if criteria.get('brand'):
                queryset = queryset.filter(model__brand__name__icontains=criteria['brand'])
            
            if criteria.get('model'):
                queryset = queryset.filter(model__name__icontains=criteria['model'])
            
            if criteria.get('category'):
                queryset = queryset.filter(model__category__name__icontains=criteria['category'])
            
            if criteria.get('fuel_type'):
                queryset = queryset.filter(fuel_type=criteria['fuel_type'])
            
            if criteria.get('transmission'):
                queryset = queryset.filter(transmission=criteria['transmission'])
            
            if criteria.get('min_seats'):
                queryset = queryset.filter(seating_capacity__gte=criteria['min_seats'])
            
            if criteria.get('max_seats'):
                queryset = queryset.filter(seating_capacity__lte=criteria['max_seats'])
            
            if criteria.get('min_price'):
                queryset = queryset.filter(daily_rate__gte=criteria['min_price'])
            
            if criteria.get('max_price'):
                queryset = queryset.filter(daily_rate__lte=criteria['max_price'])
            
            if criteria.get('available_only'):
                queryset = queryset.filter(status='available')
            
            if criteria.get('features'):
                for feature in criteria['features']:
                    queryset = queryset.filter(feature_assignments__feature__name__icontains=feature)
            
            # Apply ordering
            order_by = criteria.get('order_by', '-created_at')
            queryset = queryset.order_by(order_by)
            
            # Paginate results
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = VehicleSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = VehicleSerializer(queryset, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VehicleImageListView(generics.ListCreateAPIView):
    """API view for vehicle images"""
    serializer_class = VehicleImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter images by vehicle"""
        vehicle_id = self.kwargs.get('vehicle_id')
        return VehicleImage.objects.filter(vehicle_id=vehicle_id)
    
    def perform_create(self, serializer):
        """Set vehicle and uploaded_by fields"""
        vehicle_id = self.kwargs.get('vehicle_id')
        serializer.save(vehicle_id=vehicle_id, uploaded_by=self.request.user)


class VehicleMaintenanceListView(generics.ListCreateAPIView):
    """API view for vehicle maintenance records"""
    serializer_class = VehicleMaintenanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter maintenance records by vehicle"""
        vehicle_id = self.kwargs.get('vehicle_id')
        return VehicleMaintenanceRecord.objects.filter(vehicle_id=vehicle_id).order_by('-scheduled_date')
    
    def perform_create(self, serializer):
        """Set vehicle and created_by fields"""
        vehicle_id = self.kwargs.get('vehicle_id')
        serializer.save(vehicle_id=vehicle_id, created_by=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vehicle_availability_check(request, vehicle_id):
    """Check vehicle availability for a specific date range"""
    try:
        vehicle = get_object_or_404(Vehicle, id=vehicle_id, is_active=True)
        
        # Get date range from query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'error': 'start_date and end_date parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if vehicle is available for the date range
        from datetime import datetime
        from bookings.models import Booking
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Check for conflicting bookings
        conflicting_bookings = Booking.objects.filter(
            vehicle=vehicle,
            status__in=['confirmed', 'active'],
            pickup_date__lt=end_dt,
            return_date__gt=start_dt
        )
        
        is_available = conflicting_bookings.count() == 0 and vehicle.status == 'available'
        
        return Response({
            'vehicle_id': vehicle_id,
            'is_available': is_available,
            'start_date': start_date,
            'end_date': end_date,
            'conflicting_bookings_count': conflicting_bookings.count()
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vehicle_statistics(request):
    """Get vehicle fleet statistics"""
    total_vehicles = Vehicle.objects.filter(is_active=True).count()
    available_vehicles = Vehicle.objects.filter(is_active=True, status='available').count()
    rented_vehicles = Vehicle.objects.filter(is_active=True, status='rented').count()
    maintenance_vehicles = Vehicle.objects.filter(is_active=True, status='maintenance').count()
    
    # Category breakdown
    from django.db.models import Count
    category_breakdown = Vehicle.objects.filter(is_active=True).values(
        'model__category__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Brand breakdown
    brand_breakdown = Vehicle.objects.filter(is_active=True).values(
        'model__brand__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    return Response({
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'rented_vehicles': rented_vehicles,
        'maintenance_vehicles': maintenance_vehicles,
        'utilization_rate': (rented_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0,
        'category_breakdown': list(category_breakdown),
        'brand_breakdown': list(brand_breakdown)
    })
