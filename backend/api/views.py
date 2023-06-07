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
from users.models import Follow, User

from .filters import NameSearchFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          MyUserSerializer, RecipeReadSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          TagsSerializer)


class MyUserViewSet(views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset,
                                         many=True,
                                         context={'request': request}
                                         )
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         context={'request': request}
                                         )
        return Response(serializer.data)

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

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user.id == author.id:
                return Response({'detail': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(author=author, user=user).exists():
                return Response({'detail': 'Вы уже подписаны!'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(author,
                                          context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Follow.objects.filter(user=user, author=author).exists():
                return Response({'errors': 'Вы не подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            subscription = get_object_or_404(Follow,
                                             user=user,
                                             author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
        method for method in viewsets.ModelViewSet.http_method_names
        if method not in ['put']
    ]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(IsFavorite, request, pk)
        if request.method == 'DELETE':
            return self.del_recipe(IsFavorite, request, pk)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_recipe(IsInShoppingCartModel, request, pk)
        if request.method == 'DELETE':
            return self.del_recipe(IsInShoppingCartModel, request, pk)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
