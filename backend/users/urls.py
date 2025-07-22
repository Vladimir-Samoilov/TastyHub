from django.urls import path

from .views import AvatarView, SubscribeView, SubscriptionsView

urlpatterns = [
    path(
        'users/<int:id>/subscribe/',
        SubscribeView.as_view(),
        name='subscribe'
    ),
    path(
        'users/subscriptions/',
        SubscriptionsView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/me/avatar/',
        AvatarView.as_view(),
        name='avatar'
    ),
]
