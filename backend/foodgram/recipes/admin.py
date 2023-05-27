from django.contrib import admin

from .models import (AmountIngredients, Ingredient, IsFavorite,
                     IsInShoppingCartModel, Recipes, Tags)

admin.site.register(Ingredient)
admin.site.register(AmountIngredients)
admin.site.register(Recipes)
admin.site.register(Tags)
admin.site.register(IsInShoppingCartModel)
admin.site.register(IsFavorite)


