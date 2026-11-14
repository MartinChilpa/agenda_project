from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ServiceType(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='service_types',
    )
    name = models.CharField(max_length=100)
    default_duration_min = models.PositiveIntegerField(default=30)
    color_code = models.CharField(max_length=20, default='#4F46E5')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customers',
    )
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def trust_score(self):
        appointments = Appointment.objects.filter(
            provider_id=self.provider_id,
            customer=self.name,
        )
        appointment_count = appointments.count()
        if appointment_count == 0:
            return 'Excelente'
        no_shows = appointments.filter(status='NO_SHOW').count()
        cancelled = appointments.filter(status='CANCELLED').count()

        if no_shows == 0 and cancelled <= 1:
            return 'Excelente'
        if no_shows <= 1 and cancelled <= 3:
            return 'Regular'
        return 'Riesgo'

    def __str__(self):
        return self.name


class BlockedSlot(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_slots',
    )
    date = models.DateField(null=True, blank=True)
    all_day = models.BooleanField(default=False)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({'end_time': 'La hora de fin debe ser posterior a la hora de inicio.'})

        if self.date and self.all_day:
            return

    def __str__(self):
        return self.reason or 'Bloqueo'


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmada'),
        ('CANCELLED', 'Cancelada'),
        ('NO_SHOW', 'No asistió'),
        ('COMPLETED', 'Completada'),
    )

    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
    )
    customer = models.CharField(max_length=200, blank=True, default='')
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        errors = {}

        if self.service_type_id and self.provider_id and self.service_type.provider_id != self.provider_id:
            errors['service_type'] = 'El servicio no pertenece a este profesional.'

        if errors:
            raise ValidationError(errors)

        if self.end_time <= self.start_time:
            raise ValidationError({'end_time': 'La hora de fin debe ser posterior a la hora de inicio.'})

        if self.date and self.provider_id:
            blocked_slots = BlockedSlot.objects.filter(provider_id=self.provider_id, date=self.date)
            if blocked_slots.filter(all_day=True).exists():
                raise ValidationError({'date': 'Ese día está bloqueado para agendamiento.'})

            slot_start = datetime.combine(self.date, self.start_time)
            slot_end = datetime.combine(self.date, self.end_time)
            for blocked_slot in blocked_slots.exclude(start_time=None).exclude(end_time=None):
                blocked_start = datetime.combine(self.date, blocked_slot.start_time)
                blocked_end = datetime.combine(self.date, blocked_slot.end_time)
                if slot_start < blocked_end and slot_end > blocked_start:
                    raise ValidationError({'date': 'El rango de la cita se solapa con un bloque horario.'})

        overlapping = Appointment.objects.filter(
            provider_id=self.provider_id,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )

        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError({'start_time': 'Ya existe una cita solapada en ese horario.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.customer} - {self.service_type} - {self.date}'
