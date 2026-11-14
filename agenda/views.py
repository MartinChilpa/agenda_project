from datetime import date

from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from .models import Appointment, BlockedSlot, Customer, ServiceType
from .permissions import IsProvider
from .serializers import (
    AppointmentSerializer,
    BlockedSlotSerializer,
    CustomerSerializer,
    ServiceTypeSerializer,
)


class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.filter(is_active=True)
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsProvider]

    def get_queryset(self):
        return ServiceType.objects.filter(provider=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('id')
    serializer_class = CustomerSerializer
    permission_classes = [IsProvider]

    def get_queryset(self):
        return Customer.objects.filter(provider=self.request.user).order_by('id')

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class BlockedSlotViewSet(viewsets.ModelViewSet):
    queryset = BlockedSlot.objects.all().order_by('date', 'start_time')
    serializer_class = BlockedSlotSerializer
    permission_classes = [IsProvider]

    def get_queryset(self):
        return BlockedSlot.objects.filter(provider=self.request.user).order_by('date', 'start_time')

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by('date', 'start_time')
    serializer_class = AppointmentSerializer
    permission_classes = [IsProvider]

    def get_queryset(self):
        appointments = Appointment.objects.filter(
            provider=self.request.user,
        ).select_related('service_type').order_by('date', 'start_time')

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        parsed_start = self._parse_date('start_date', start_date) if start_date is not None else None
        parsed_end = self._parse_date('end_date', end_date) if end_date is not None else None

        if parsed_start and parsed_end and parsed_start > parsed_end:
            raise ValidationError({'end_date': 'Debe ser igual o posterior a start_date.'})
        if parsed_start:
            appointments = appointments.filter(date__gte=parsed_start)
        if parsed_end:
            appointments = appointments.filter(date__lte=parsed_end)
        return appointments

    @staticmethod
    def _parse_date(field_name, value):
        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError({field_name: 'Usa el formato YYYY-MM-DD.'}) from exc

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)
