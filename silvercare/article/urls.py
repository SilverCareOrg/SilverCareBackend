from django.urls import path
from .views import CreateArticle, get_articles_types,\
    get_articles,\
    get_article,\
    delete_article

urlpatterns = [
    path('create_article', CreateArticle.as_view(), name='create_article'),
    path('get_articles_types', get_articles_types),
    path('get_articles', get_articles),
    path('get_article', get_article),
    path('delete_article', delete_article),
]