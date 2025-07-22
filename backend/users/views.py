from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser, Subscription
from .serializers import SubscriptionSerializer, UserSerializer


class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Уже подписаны'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(
            author, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        deleted, _ = Subscription.objects.filter(
            user=user, author=author
        ).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Подписка не найдена'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = 100


class SubscriptionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        authors = CustomUser.objects.filter(subscribers__user=user)
        paginator = LimitPagination()
        page = paginator.paginate_queryset(authors, request, view=self)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


class AvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response({'avatar': serializer.data['avatar']}, status=200)

    def put(self, request):
        user = request.user
        avatar = request.data.get('avatar')
        if not avatar:
            return Response({'errors': 'No file provided'}, status=400)
        user.avatar = avatar
        user.save()
        serializer = UserSerializer(user, context={'request': request})
        return Response({'avatar': serializer.data['avatar']}, status=200)

    def delete(self, request):
        user = request.user
        avatar_name = str(user.avatar)
        if avatar_name and not avatar_name.startswith('data:image'):
            user.avatar.delete(save=True)
        user.avatar = None
        user.save()
        return Response(status=204)
