from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.conf import settings
from api.utils.validators import sanitize_api_key
from api.models import StorageCredential
from api.services.storage_service import StorageService
import random

class ExternalUploadView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        auth = request.headers.get('Authorization', '')
        if not settings.EXTERNAL_UPLOAD_API_KEY:
            return Response({'error': 'EXTERNAL_UPLOAD_API_KEY not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not auth.startswith('Bearer '):
            return Response({'error': 'Missing Bearer token'}, status=status.HTTP_401_UNAUTHORIZED)
        token = sanitize_api_key(auth.replace('Bearer ', ''))
        if token != sanitize_api_key(settings.EXTERNAL_UPLOAD_API_KEY):
            return Response({'error': 'Invalid API key'}, status=status.HTTP_403_FORBIDDEN)

        upfile = request.FILES.get('file')
        if not upfile:
            return Response({'error': 'file is required (multipart/form-data)'}, status=status.HTTP_400_BAD_REQUEST)
        file_bytes = upfile.read()
        file_name = upfile.name

        provider = request.data.get('provider')
        qs = StorageCredential.objects.filter(is_active=True)
        if provider:
            qs = qs.filter(provider=provider)
        creds = list(qs)
        if not creds:
            return Response({'error': 'No active storage credentials'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        random.shuffle(creds)

        errors = []
        for cred in creds:
            try:
                if cred.provider == 'imagekit':
                    res = StorageService.upload_imagekit(cred, file_bytes, file_name)
                elif cred.provider == 'cloudinary':
                    res = StorageService.upload_cloudinary(cred, file_bytes, file_name)
                else:
                    raise Exception(f'Unsupported provider {cred.provider}')
                return Response({'success': True, 'data': res, 'provider': cred.name}, status=status.HTTP_200_OK)
            except Exception as e:
                errors.append({'provider': cred.name, 'error': str(e)})
                continue

        return Response({'success': False, 'errors': errors}, status=status.HTTP_502_BAD_GATEWAY)
