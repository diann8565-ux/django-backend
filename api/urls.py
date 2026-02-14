
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api.views.user import ProfileViewSet
from api.views.storage import StorageCredentialViewSet
from api.views.category import CategoryViewSet
from api.views.file import FileViewSet
from api.views.log import ActivityLogViewSet
from api.views.apikey import ApiKeyViewSet
from api.views.auth import DevLoginView, ChangePasswordView, CustomTokenObtainPairView
from api.views.misc import AIProxyView, HealthCheckView
from api.views.external import ExternalUploadView

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'storage_credentials', StorageCredentialViewSet, basename='storage_credential')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'files', FileViewSet, basename='file')
router.register(r'activity_logs', ActivityLogViewSet, basename='activity_log')
router.register(r'api_keys', ApiKeyViewSet, basename='api_key')

urlpatterns = [
    path('health', HealthCheckView.as_view(), name='health'),
    path('auth/login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/dev-login', DevLoginView.as_view(), name='dev_login'),
    path('auth/password', ChangePasswordView.as_view(), name='change_password'),
    path('auth/me', ProfileViewSet.as_view({'get': 'me'}), name='me'),
    path('ai/generate', AIProxyView.as_view(), name='ai_generate'),
    path('external/upload', ExternalUploadView.as_view(), name='external_upload'),
    path('', include(router.urls)),
]
