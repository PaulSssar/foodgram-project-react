from django.shortcuts import HttpResponse
from .serializers import IngredientSerializer, AmountIngredientsSerializer, TagsSerializer, RecipeSerializer
from recipes.models import Ingredient, AmountIngredients, Tags, Recipes, IsFavorite
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


def get_shopping_list_data(author):
    return RecipeIngredient.objects.filter(
        recipe__shopping_cart__author=author
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(
        amounts=Sum('amount', distinct=True)
    ).order_by('amounts')


def generate_shopping_list_response(data):
    today = date.today().strftime("%d-%m-%Y")
    shopping_list = f'Список покупок на: {today}\n\n'
    for ingredient in data:
        shopping_list += (
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}) — '
            f'{ingredient["amounts"]}\n'
        )
    return HttpResponse(shopping_list,
                        content_type='text/plain; charset=utf-8')

class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            if Favorite.objects.filter(author=user,
                                       recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteSerializer(data={
                'recipe': recipe.id,
                'author': user.id
            })
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if not Favorite.objects.filter(author=user,
                                       recipe=recipe).exists():
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        get_object_or_404(Favorite, author=user, recipe=recipe).delete()
        return Response({'message': 'Рецепт удалён из избранного'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            if ShoppingCart.objects.filter(author=user,
                                           recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(data={
                'recipe': recipe.id,
                'author': user.id
            })
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if not ShoppingCart.objects.filter(author=user,
                                           recipe=recipe).exists():
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        get_object_or_404(ShoppingCart, author=user, recipe=recipe).delete()
        return Response({'message': 'Рецепт удалён из списка покупок'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        author = get_object_or_404(User, id=self.request.user.pk)
        if author.shopping_cart.exists():
            data = get_shopping_list_data(author)
            response = generate_shopping_list_response(data)
            filename = 'shopping_list.txt'
            response['Content-Disposition'] = (f'attachment; '
                                               f'filename={filename}')
            return response
        return Response({'message': 'Список покупок пуст'},
                        status=status.HTTP_404_NOT_FOUND)



