from rest_framework import serializers
from recipes.models import Ingredient, AmountIngredients, Recipes, Tags, IsFavorite, IsInShoppingCartModel
from drf_extra_fields.fields import Base64ImageField


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class AmountIngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmountIngredients
        fields = '__all__'


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('__all__')

    def get_is_in_shopping_cart(self, obj):
        return IsInShoppingCartModel.objects.filter(
            recipe=obj, user=self.context.get('request').user
        ).exists()

    def get_is_favorited(self, obj):
        return IsFavorite.objects.filter(
            recipe=obj, user=self.context.get('request').user
        ).exists()
