from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status, exceptions
from rest_framework.response import Response

from .serializers import RegisterSerializer, VerifyEmailSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        language_code = self.request.LANGUAGE_CODE
        with transaction.atomic():
            user = serializer.save()
            self._send_activation_email(user, language_code)

    def _send_activation_email(self, user, language_code):
        base64_user_id = urlsafe_base64_encode(force_bytes(user.pk))
        activation_token = default_token_generator.make_token(user)
        activation_link = "%s/accounts/verify-email/%s/%s" % (settings.FRONTEND_URL, base64_user_id, activation_token)

        template_context = {'user': user.username, 'link': activation_link}
        template_dir = language_code + '/mail/registration/'
        plain_text_content = render_to_string(template_dir + 'confirm.txt', template_context)
        html_content = render_to_string(template_dir + 'confirm.html', template_context)
        mail_subject = _('Confirm your email')

        email_message = EmailMultiAlternatives(
            subject=mail_subject,
            body=plain_text_content,
            to=[user.email, ])
        email_message.attach_alternative(html_content, "text/html")
        email_message.send(fail_silently=False)


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.validated_data
        user_is_active = serialized_data.get('is_active')
        if not user_is_active:
            user_id = serialized_data.get('user_id')
            try:
                user = get_user_model().objects.get(pk=user_id)
                user.is_active = True
                user.save()
            except get_user_model().DoesNotExist:
                raise exceptions.ParseError()
        return Response({}, status=status.HTTP_200_OK)
