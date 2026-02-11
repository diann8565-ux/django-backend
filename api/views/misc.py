
from rest_framework import views, permissions, status
from rest_framework.response import Response
from api.services.ai_service import AIService

class AIProxyView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Expecting messages or prompt in body
            messages = request.data.get('messages')
            if not messages:
                # If simplified prompt is sent
                prompt = request.data.get('prompt')
                if prompt:
                    messages = [{"role": "user", "content": prompt}]
                else:
                    return Response({'error': 'No messages or prompt provided'}, status=status.HTTP_400_BAD_REQUEST)

            response = AIService.generate_response(messages)
            return Response(response)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthCheckView(views.APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({'status': 'ok', 'service': 'django-storage'})
