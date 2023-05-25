from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngridientViewSet, MyUserViewSet, RecipeViewSet, TagsViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', MyUserViewSet)
router.register(r'ingredients', IngridientViewSet, basename='ingredients')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

