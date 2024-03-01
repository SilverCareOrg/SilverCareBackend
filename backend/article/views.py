from django.views.decorators.csrf import csrf_exempt
from .models import Article, ArticleImage, ArticleText, CategoryType
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from login.utils import get_user_from_token_request
import uuid
import json

class CreateArticle(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        user = get_user_from_token_request(request)
        
        if not user.is_staff:
            return JsonResponse({'message': 'You are not authorized to add services'}, status=400)

        data = request.data
        # try:
        article = Article.objects.create(
            title=data.get("title"),
            author=data.get("author"),
            reading_time=data.get("reading_time"),
            category=data.get("category"),
            description=data.get("description")
        )

        main_image = request.FILES.get('image')
        article.add_image(
            image_id=str(uuid.uuid4()),
            position=-1,
            is_main_image=True,
            image_data=main_image
        )

        texts = json.loads(data.get("paragraphText"))
        paragraph_images = request.FILES.getlist('paragraphImage')
        image_indexes = [int(x) for x in data.get("imageIndexes").split(",")]
        for i in range(len(texts)):
            try:
                try:
                    pos = image_indexes.index(i)
                except:
                    pos = -1

                article.add_text(
                    id=str(uuid.uuid4()),
                    position=i,
                    text_data=texts[i]["text"],
                    image_data=paragraph_images[pos] if pos != -1 else None
                )
            except Exception as e:
                return JsonResponse(str(e), safe=False, status=400)

        article.save()
        return JsonResponse("Article added successfully!", safe=False, status=200)

class EditArticle(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        user = get_user_from_token_request(request)
        
        if not user.is_staff:
            return JsonResponse({'message': 'You are not authorized to add services'}, status=400)

        data = request.data
        article = Article.objects.get(id=data.get("id"))
        if article is None:
            return JsonResponse("Article not found", safe=False, status=400)
        
        # try:
        for x in ["title", "author", "reading_time", "category", "description"]:
            if x in data:
                setattr(article, x, data.get(x))

        article.save()

        main_image = request.FILES.get('image')
        if main_image:
            ArticleImage.objects.update_or_create(
                article=article,
                is_main_image=True,
                defaults={
                    "position": -1,
                    "id": str(uuid.uuid4()),
                    "image_data": main_image
                }
            )

        texts = json.loads(data.get("paragraphText"))
        paragraph_images = request.FILES.getlist('paragraphImage')
        image_indexes = [int(x) for x in data.get("imageIndexes").split(",")]
        
        # First delete all texts and images associated with the current article
        # Delete Texts first
        texts = article.articletext_set.all()
        for text in texts:
            text.delete()
            
        # Delete Images
        images = article.articleimage_set.all()
        for image in images:
            image.delete()
            
        for i in range(len(texts)):
            try:
                try:
                    pos = image_indexes.index(i)
                except:
                    pos = -1

                article.add_text(
                    id=str(uuid.uuid4()),
                    position=i,
                    text_data=texts[i]["text"],
                    image_data=paragraph_images[pos] if pos != -1 else None
                )
            except Exception as e:
                return JsonResponse(str(e), safe=False, status=400)

        article.save()
        return JsonResponse("Article edited successfully!", safe=False, status=200)

@api_view(['GET'])
def get_articles_types(request):
    return JsonResponse(CategoryType.get_types(), safe=False, status=200)

@api_view(['GET'])
def get_articles(request):
    inf_limit = int(request.GET.get('inf_limit', 0))
    sup_limit = int(request.GET.get('sup_limit', 10))
    category = request.GET.get('category', None)

    if sup_limit < inf_limit:
        inf_limit, sup_limit = sup_limit, inf_limit
    
    if sup_limit > inf_limit + 20:
        sup_limit = inf_limit + 20
    
    
    if category is not None:
        articles = Article.objects.filter(category=category)[int(inf_limit):int(sup_limit)]
    else:
        articles = Article.objects.all()[int(inf_limit):int(sup_limit)]  
    
    return JsonResponse([{
        "id": article.id,
        "title": article.title,
        "author": article.author,
        "description": article.description,
        "reading_time": article.reading_time,
        "category": article.category,
        "main_image": article.articleimage_set.get(is_main_image=True).id
    } for article in articles], safe=False, status=200)
    
@api_view(['GET'])
def get_article(request):
    try:
        article_id = request.GET.get('id', None)
        if article_id is None:
            return JsonResponse("No id provided", safe=False, status=400)

        article = Article.objects.get(id=article_id)
        main_image = article.articleimage_set.get(is_main_image=True).id
        texts = article.articletext_set.all()
        texts_json = []

        for text in texts:
            image = text.article_image.id if text.article_image else None
            texts_json.append({
                "id": text.text_id,
                "text": text.text,
                "image": image,
                "position": text.position,
            })

        return JsonResponse({
            "title": article.title,
            "author": article.author,
            "description": article.description,
            "reading_time": article.reading_time,
            "category": article.category,
            "main_image": main_image,
            "texts": texts_json
        }, safe=False, status=200)
    except Article.DoesNotExist:
        return JsonResponse("Article not found", safe=False, status=400)

@api_view(['GET'])
def delete_article(request):
    user = get_user_from_token_request(request)
    if not user.is_staff:
        return JsonResponse({'message': 'You are not authorized to delete articles'}, status=400)

    article = Article.objects.get(id=request.GET.get("id"))
    
    # Delete Texts first
    texts = article.articletext_set.all()
    for text in texts:
        text.delete()
        
    # Delete Images
    images = article.articleimage_set.all()
    for image in images:
        image.delete()
    
    article.delete()
    return JsonResponse("Article deleted successfully!", safe=False, status=200)
    

