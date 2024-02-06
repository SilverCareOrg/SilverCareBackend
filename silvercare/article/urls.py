from django.urls import path
from .views import CreateArticle, get_articles_types

urlpatterns = [
    path('create_article', CreateArticle.as_view(), name='create_article'),
    path('get_articles_types', get_articles_types),
]