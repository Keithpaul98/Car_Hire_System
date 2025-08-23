from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from .models import Booking, BookingAddOn, BookingAddOnAssignment
from vehicles.models import Vehicle


class BookingQuoteSerializer(serializers.Serializer):
    vehicle_id = serializers.UUIDField()
    pickup_date = serializers.DateTimeField()
    return_date = serializers.DateTimeField()
    pickup_location = serializers.CharField(max_length=200)
    return_location = serializers.CharField(max_length=200)
    addon_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)

    def validate(self, attrs):
        pickup = attrs['pickup_date']
        ret = attrs['return_date']
        if ret <= pickup:
            raise serializers.ValidationError({'return_date': 'Return date must be after pickup date'})
        # Ensure future pickup
        if pickup <= timezone.now():
            raise serializers.ValidationError({'pickup_date': 'Pickup must be in the future'})
        # Check vehicle exists and is active
        try:
            vehicle = Vehicle.objects.get(id=attrs['vehicle_id'], is_active=True)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError({'vehicle_id': 'Vehicle not found or inactive'})
        # Check availability (no overlapping active bookings)
        overlapping = Booking.objects.filter(
            vehicle=vehicle,
        ).exclude(status__in=['cancelled', 'completed', 'no_show']).filter(
            pickup_date__lt=ret,
            return_date__gt=pickup,
        ).exists()
        if overlapping:
            raise serializers.ValidationError('Vehicle not available for the selected period')
        attrs['vehicle'] = vehicle
        return attrs

    def create_pricing(self, vehicle: Vehicle, pickup, ret, addon_ids=None):
        days = max(1, (ret - pickup).days)
        daily_rate = vehicle.daily_rate
        addons_total = Decimal('0')
        addons = []
        if addon_ids:
            valid_addons = list(BookingAddOn.objects.filter(id__in=addon_ids, is_active=True))
            for addon in valid_addons:
                addons.append(addon)
                if addon.pricing_type == 'per_day':
                    addons_total += addon.price * days
                elif addon.pricing_type == 'per_booking':
                    addons_total += addon.price
                elif addon.pricing_type == 'percentage':
                    addons_total += (daily_rate * days) * (addon.price / Decimal('100'))
        subtotal = (daily_rate * days) + addons_total
        tax_amount = Decimal('0')
        discount_amount = Decimal('0')
        security_deposit = vehicle.security_deposit or Decimal('0')
        total_amount = subtotal + tax_amount - discount_amount + security_deposit
        return {
            'daily_rate': daily_rate,
            'total_days': days,
            'addons_total': addons_total,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'discount_amount': discount_amount,
            'security_deposit': security_deposit,
            'total_amount': total_amount,
            'addons': addons,
        }


class BookingCreateSerializer(BookingQuoteSerializer):
    special_requests = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        vehicle = validated_data['vehicle']
        pickup = validated_data['pickup_date']
        ret = validated_data['return_date']
        addon_ids = validated_data.get('addon_ids', [])
        pricing = self.create_pricing(vehicle, pickup, ret, addon_ids)

        user = self.context['request'].user
        booking = Booking.objects.create(
            customer=user,
            vehicle=vehicle,
            pickup_date=pickup,
            return_date=ret,
            pickup_location=validated_data['pickup_location'],
            return_location=validated_data['return_location'],
            status='pending',
            payment_status='pending',
            daily_rate=pricing['daily_rate'],
            total_days=pricing['total_days'],
            subtotal=pricing['subtotal'],
            tax_amount=pricing['tax_amount'],
            discount_amount=pricing['discount_amount'],
            additional_fees=Decimal('0'),
            security_deposit=pricing['security_deposit'],
            total_amount=pricing['total_amount'],
            special_requests=validated_data.get('special_requests', ''),
        )

        # Assign add-ons if any
        addon_ids = addon_ids or []
        if addon_ids:
            addons = pricing['addons']
            for addon in addons:
                unit_price = addon.price
                total_price = unit_price if addon.pricing_type != 'per_day' else unit_price * pricing['total_days']
                BookingAddOnAssignment.objects.create(
                    booking=booking,
                    addon=addon,
                    quantity=1,
                    unit_price=unit_price,
                    total_price=total_price,
                )
        return booking


class BookingSerializer(serializers.ModelSerializer):
    vehicle_display = serializers.CharField(source='vehicle.get_display_name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'customer', 'vehicle', 'vehicle_display',
            'pickup_date', 'return_date', 'pickup_location', 'return_location',
            'status', 'payment_status', 'daily_rate', 'total_days', 'subtotal',
            'tax_amount', 'discount_amount', 'additional_fees', 'security_deposit',
            'total_amount', 'created_at'
        ]
        read_only_fields = [
            'id', 'booking_reference', 'customer', 'status', 'payment_status',
            'daily_rate', 'total_days', 'subtotal', 'tax_amount', 'discount_amount',
            'additional_fees', 'security_deposit', 'total_amount', 'created_at'
        ]
