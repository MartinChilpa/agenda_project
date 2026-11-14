from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LoginView, LogoutView, RegisterView, SessionView, UserViewSet, csrf_token_view

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('csrf/', csrf_token_view, name='csrf-token'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('session/', SessionView.as_view(), name='session'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
]
