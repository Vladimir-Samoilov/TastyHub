from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from rest_framework import serializers

from .models import CustomUser, Subscription


class UserCreateSerializer(DjoserUserCreateSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta(DjoserUserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password', 'avatar'
        )


class UserSerializer(DjoserUserSerializer):
    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'is_subscribed', 'avatar'
        )

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )

    def to_representation(self, instance):
        print('Custom UserSerializer in action!')
        return super().to_representation(instance)


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )

    def get_recipes(self, obj):
        from api.serializers import ShortRecipeSerializer
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
