from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Recipe, Tag, Ingredient, Favorite, ShoppingCart
)
from .serializers import (
    RecipeReadSerializer, RecipeWriteSerializer, TagSerializer,
    IngredientSerializer, FavoriteSerializer, ShoppingCartSerializer
)
from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        return self._handle_custom_action(
            model=Favorite, serializer_class=FavoriteSerializer,
            request=request, pk=pk
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self._handle_custom_action(
            model=ShoppingCart, serializer_class=ShoppingCartSerializer,
            request=request, pk=pk
        )

    def _handle_custom_action(self, model, serializer_class, request, pk):
        user = request.user
        recipe = Recipe.objects.get(pk=pk)
        if request.method == 'POST':
            obj, created = model.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not created:
                return Response({'errors': 'Уже добавлено.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = serializer_class(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            deleted, _ = model.objects.filter(
                user=user, recipe=recipe
            ).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Не найдено в списке.'},
                            status=status.HTTP_400_BAD_REQUEST)
