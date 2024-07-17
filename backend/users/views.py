from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet as DjoserViewSet
from users.serializers import AvatarSerializer

User = get_user_model()


class UserViewSet(DjoserViewSet):
    @action(
        methods=('get',),
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        methods=('put', 'delete'),
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            if serializer.is_valid():
                user.avatar = serializer.validated_data['avatar']
                user.save()
                return Response({'avatar': user.avatar.url}, status=200)
            else:
                return Response(serializer.errors, status=400)

        elif request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=204)
