from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription, User
from .serializers import (AvatarUpdateSerializer, SubscriptionSerializer,
                          UserSerializer)

MAX_PAGE_SIZE = 100


class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        data = {'user': user.id, 'author': author.id}
        serializer = SubscriptionSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
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
    max_page_size = MAX_PAGE_SIZE


class SubscriptionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        authors = User.objects.filter(subscribers__user=user)
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
        return Response(
            {'avatar': serializer.data['avatar']},
            status=status.HTTP_200_OK
        )

    def put(self, request):
        user = request.user
        serializer = AvatarUpdateSerializer(
            user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'avatar': serializer.data['avatar']},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=True)
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
