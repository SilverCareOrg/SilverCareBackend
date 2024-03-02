from django.urls import path
from .views import CreateArticle, EditArticle, get_articles_types,\
    get_articles,\
    get_article,\
    delete_article,\
    set_article_visibility

urlpatterns = [
    path('create_article', CreateArticle.as_view(), name='create_article'),
    path('edit_article', EditArticle.as_view(), name='edit_article'),
    path('get_articles_types', get_articles_types),
    path('get_articles', get_articles),
    path('get_article', get_article),
    path('delete_article', delete_article),
    path('set_article_visibility', set_article_visibility),
]