from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngridientViewSet, MyUserViewSet, RecipeViewSet, TagsViewSet

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('users', MyUserViewSet)
v1_router.register('ingredients', IngridientViewSet, basename='ingredients')
v1_router.register('tags', TagsViewSet, basename='tags')
v1_router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
