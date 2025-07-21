from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404

from .models import CustomUser, Subscription
from .serializers import SubscriptionSerializer


class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Уже подписаны'},
                status=status.HTTP_400_BAD_REQUEST
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
            status=status.HTTP_400_BAD_REQUEST
        )


class SubscriptionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        authors = CustomUser.objects.filter(subscribers__user=user)
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    def paginate_queryset(self, queryset):
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 6
        return paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 6
        return paginator.get_paginated_response(data)
