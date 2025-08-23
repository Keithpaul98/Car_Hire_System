from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer, BookingQuoteSerializer


# Create your views here.

class IsStaffOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.customer_id == request.user.id


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().select_related('vehicle', 'customer')
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff:
            return qs
        return qs.filter(customer=user)

    def get_serializer_class(self):
        if self.action in ['create']:
            return BookingCreateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['post'], url_path='quote')
    def quote(self, request):
        serializer = BookingQuoteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.validated_data['vehicle']
        pickup = serializer.validated_data['pickup_date']
        ret = serializer.validated_data['return_date']
        addon_ids = serializer.validated_data.get('addon_ids', [])
        pricing = serializer.create_pricing(vehicle, pickup, ret, addon_ids)
        return Response({
            'vehicle': str(vehicle.id),
            'total_days': pricing['total_days'],
            'daily_rate': str(pricing['daily_rate']),
            'addons_total': str(pricing['addons_total']),
            'subtotal': str(pricing['subtotal']),
            'tax_amount': str(pricing['tax_amount']),
            'discount_amount': str(pricing['discount_amount']),
            'security_deposit': str(pricing['security_deposit']),
            'total_amount': str(pricing['total_amount']),
        })

    @action(detail=True, methods=['post'], url_path='cancel', permission_classes=[permissions.IsAuthenticated, IsStaffOrOwner])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if not booking.can_be_cancelled():
            return Response({'detail': 'Booking cannot be cancelled at this stage'}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.save(update_fields=['status', 'cancelled_at'])
        return Response({'detail': 'Booking cancelled successfully'})
