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
        merged = list(zip(texts, paragraph_images))
        print(merged)
        for i, (text, image) in enumerate(merged):
            article.add_text(
                id=str(uuid.uuid4()),
                position=i,
                text_data=text["text"],
                image_data=image
            )

        article.save()
        return JsonResponse("Article added successfully!", safe=False, status=200)
        # except Exception as e:
        #     return JsonResponse(str(e), safe=False, status=400)


@api_view(['GET'])
def get_articles_types(request):
    return JsonResponse(CategoryType.get_types(), safe=False, status=200)

    
    

