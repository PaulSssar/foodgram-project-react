from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингридиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Tags(models.Model):
    name = models.CharField(
        'Название',
        max_length=200
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        null=True
    )
    slug = models.SlugField(
        'Слаг',
        max_length=200
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор',
    )
    name = models.CharField(
        'Название',
        max_length=200,
    )
    image = models.ImageField(
        'Картинка',
        upload_to='uploads/%Y/%m/%d/'
    )
    description = models.TextField(
        'Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты блюда',
        related_name='recipe',
        through='recipes.AmountIngredients',
    )
    tags = models.ForeignKey(
        Tags,
        verbose_name='Тег',
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipe'
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                1,
                'Время приготовлениядолжно быть не мене 1 минуты'
            ),
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class AmountIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        related_name='amount',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Название ингридиента'
    )
    amount = models.IntegerField(
        'Количество ингридиента'
    )

    class Meta:
        verbose_name = 'Количество ингридиентов'
        verbose_name_plural = 'Количество ингридиентов'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'рецепт:{self.recipe} ингредиент:{self.ingredient}'


class IsInShoppingCartModel(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Рецепт в покупках'
        verbose_name_plural = 'Рецепты в покупках'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_is_in_shopping_cart'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в покупках или нет у {self.user}'


class IsFavorite(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_is_favorite'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в избрангом или нет у {self.user}'
