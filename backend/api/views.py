from django.db.models.aggregates import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views
from recipes.models import (AmountIngredients, Ingredient, IsFavorite,
                            IsInShoppingCartModel, Recipes, Tags)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User

from .filters import NameSearchFilter, RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          MyUserSerializer, RecipeReadSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          TagsSerializer)


class MyUserViewSet(views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (NameSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class AddAndDeleteRecipeView(APIView):
    def add_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipes, pk=pk)
        user = self.request.user
        if model.objects.filter(recipe=recipe, user=user).exists():
            return Response({'errors': 'Рецепт уже добавлен'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(recipe=recipe, user=user)
        serializer = ShortRecipeSerializer(
            recipe,
            context={'request': request}
        )
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def del_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipes, pk=pk)
        user = self.request.user
        if not model.objects.filter(user=user, recipe=recipe).exists():
            return Response({'errors': 'Рецепт отсутствует'},
                            status=status.HTTP_400_BAD_REQUEST)
        obj = get_object_or_404(model, recipe=recipe, user=user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet,
                    AddAndDeleteRecipeView):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = [
        method for method in viewsets.ModelViewSet.http_method_names if method not in ['put']
    ]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['post', ],
            permission_classes=[IsAuthenticated])
    def add_favorite(self, request, pk):
        return self.add_recipe(IsFavorite, request, pk)

    @action(detail=True,
            methods=['delete', ],
            permission_classes=[IsAuthenticated])
    def del_favorite(self, request, pk=None):
        return self.del_recipe(IsFavorite, request, pk)

    @action(detail=True,
            methods=['post', ],
            permission_classes=[IsAuthenticated])
    def add_shopping_cart(self, request, pk=None):
        return self.add_recipe(IsInShoppingCartModel, request, pk)

    @action(detail=True,
            methods=['delete', ],
            permission_classes=[IsAuthenticated])
    def del_shopping_cart(self, request, pk=None):
        return self.del_recipe(IsInShoppingCartModel, request, pk)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = AmountIngredients.objects.filter(
            recipe__shopping_cart__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum('amount'))
        text = ''
        for ingredient in ingredients:
            text += (f'•  {ingredient["ingredient__name"]}'
                     f'({ingredient["ingredient__measurement_unit"]})'
                     f'— {ingredient["amount"]}\n')
        headers = {
            'Content-Disposition': 'attchment; filename=shoping_cart.txt'}
        return HttpResponse(
            text, content_type='text/plain; charset=UTF-8', headers=headers)
