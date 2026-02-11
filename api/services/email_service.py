
from django.core.mail import send_mail
from django.conf import settings

class EmailService:
    @staticmethod
    def send_welcome_email(user):
        send_mail(
            'Welcome to Storage App',
            f'Hi {user.username}, welcome to your new storage solution.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )

    @staticmethod
    def send_verification_email(user, token):
        # Logic to send verification link
        pass
