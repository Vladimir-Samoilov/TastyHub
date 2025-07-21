from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

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
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

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
        if self.action in ('list', 'retrieve'):
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        read_serializer = RecipeReadSerializer(
            serializer.instance, context={'request': request}
        )
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class RecipeImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)
        serializer = RecipeReadSerializer(recipe, context={'request': request})
        return Response({'image': serializer.data['image']}, status=200)

    def put(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)
        image = request.data.get('image')
        if not image:
            return Response({'errors': 'No file provided'}, status=400)
        recipe.image = image
        recipe.save()
        serializer = RecipeReadSerializer(recipe, context={'request': request})
        return Response({'image': serializer.data['image']}, status=200)

    def delete(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)
        image_name = str(recipe.image)
        if image_name and not image_name.startswith('data:image'):
            recipe.image.delete(save=True)
        recipe.image = None
        recipe.save()
        return Response(status=204)
