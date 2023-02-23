from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        user = get_user_model().objects.get(pk=request.user.pk)
        return Response({'username': user.username, 'email': user.email})
