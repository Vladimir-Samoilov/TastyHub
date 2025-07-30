from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe,
    ShoppingCart, Tag
)
from recipes.permissions import IsAuthorOrReadOnly
from recipes.serializers import (
    IngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer,
    ShortRecipeSerializer, TagSerializer
)

from .filters import RecipeFilter
from .utils import generate_shopping_cart_content


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            return queryset.filter(name__istartswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self._handle_custom_action(
            model=Favorite,
            serializer_class=ShortRecipeSerializer,
            request=request,
            pk=pk
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self._handle_custom_action(
            model=ShoppingCart,
            serializer_class=ShortRecipeSerializer,
            request=request,
            pk=pk
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__shopping_cart__user=user
            )
            .values(
                'ingredient__name',
                'ingredient__measurement_unit'
            )
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        content = generate_shopping_cart_content(ingredients)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    def _handle_custom_action(self, model, serializer_class, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            obj, created = model.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not created:
                return Response(
                    {'errors': 'Уже добавлено.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = serializer_class(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            deleted, _ = model.objects.filter(
                user=user, recipe=recipe
            ).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Не найдено в списке.'},
                status=status.HTTP_400_BAD_REQUEST
            )

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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        read_serializer = RecipeReadSerializer(
            serializer.instance, context={'request': request}
        )
        return Response(read_serializer.data)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        url_name='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        link = request.build_absolute_uri(f'/recipes/{recipe.id}/')
        return Response({'short-link': link}, status=status.HTTP_200_OK)


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
