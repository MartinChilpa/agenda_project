from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Appointment, BlockedSlot, Customer, ServiceType


class ServiceTypeSerializer(serializers.ModelSerializer):
    provider = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ServiceType
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    provider = serializers.PrimaryKeyRelatedField(read_only=True)
    trust_score = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = '__all__'


class BlockedSlotSerializer(serializers.ModelSerializer):
    provider = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = BlockedSlot
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    provider = serializers.PrimaryKeyRelatedField(read_only=True)
    service_name = serializers.CharField(source='service_type.name', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['service_type'].queryset = ServiceType.objects.filter(
                provider=request.user,
                is_active=True,
            )

    def validate(self, attrs):
        instance = self.instance or Appointment()
        for field, value in attrs.items():
            setattr(instance, field, value)

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            instance.provider = request.user

        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc

        return attrs
