from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet as DjoserViewSet
from users.serializers import AvatarSerializer, ExtendedCustomUserSerializer
from users.models import Subscription

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
            return Response(serializer.errors, status=400)

        user.avatar = None
        user.save()
        return Response(status=204)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=ExtendedCustomUserSerializer,
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        user = request.user

        subscriptions = Subscription.objects.filter(follower=user).values_list(
            'following', flat=True
        )
        following_users = User.objects.filter(id__in=subscriptions)

        paginator = self.paginator
        result_page = paginator.paginate_queryset(following_users, request)

        serializer = self.get_serializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        serializer_class=ExtendedCustomUserSerializer,
        url_path='subscribe',
    )
    def subscribe(self, request, id):
        user = request.user
        author = self.get_object()
        subcription = Subscription.objects.filter(
            follower=user, following=author
        ).first()

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'detail': 'Нельзя подписаться на самого себя'},
                    status=400
                )

            if subcription:
                return Response(
                    {'detail': 'Вы уже подписаны на этого автора'}, status=400
                )

            Subscription.objects.create(follower=user, following=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=201)

        if subcription:
            subcription.delete()
            return Response(status=204)
        return Response(
            {'detail': 'Вы не подписаны на этого автора'}, status=400
        )
