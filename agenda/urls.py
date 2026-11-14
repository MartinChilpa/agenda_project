from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet, BlockedSlotViewSet, CustomerViewSet, ServiceTypeViewSet

router = DefaultRouter()
router.register(r'service-types', ServiceTypeViewSet, basename='service-type')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'blocked-slots', BlockedSlotViewSet, basename='blocked-slot')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]
