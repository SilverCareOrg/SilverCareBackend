from django.db import models
from enum import Enum
import os

class CategoryType(Enum):
    PRODUCTS_USE = (0, "Utilizarea produselor")
    PHYSICAL_EXERCISES = (1, "Exerciții fizice")
    ONLINE_SERVICES = (2, "Servicii online")
    LEGALS = (3, "Drepturi legale")
    PHYSICAL_HEALTH = (4, "Sănătate fizică")
    MENTAL_HEALTH = (5, "Sănătate mentală")
    WEBINARS = (6, "Resurse webinarii")
    SELF_CARE = (7, "Îngrijirea pe termen lung")

    def get_types():
        return [category.value for category in CategoryType]

class ArticleImage(models.Model):
    id = models.CharField(max_length=37, primary_key=True)
    position = models.IntegerField()
    article = models.ForeignKey("article.Article", on_delete=models.SET_NULL, null=True)
    is_main_image = models.BooleanField(default=False)

class ArticleText(models.Model):
    text_id = models.CharField(max_length=37, primary_key=True)
    text = models.CharField(max_length=1000)
    position = models.IntegerField()
    article = models.ForeignKey("article.Article", on_delete=models.SET_NULL, null=True)
    article_image = models.OneToOneField(ArticleImage, on_delete=models.CASCADE)

CATEGORY_CHOICES = [(tag.value[0], tag.value[1]) for tag in CategoryType]

class Article(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    reading_time = models.IntegerField()
    category = models.IntegerField(choices=CATEGORY_CHOICES)

    def add_image(self, image_id, position, is_main_image=False, image_data=None):
        if image_data is None:
            raise Exception("No image data provided")
        
        image = ArticleImage(id=image_id, position=position, article=self, is_main_image=is_main_image)
        image.save()
        
        # Save image with the id
        f = open(os.path.join(os.path.dirname(__file__), 'images/' + image_id + "." + str(image_data).split('.')[-1]), 'wb')
        f.write(image_data.read())
        f.close()

    def add_text(self, id, position, text_data, image_data):
        if text_data is None:
            raise Exception("No text provided")
        
        text = ArticleText(text_id=id, position=position, article=self, text=text_data)
        
        if image_data is not None:
            self.add_image(id, position, False, image_data)
            text.article_image = ArticleImage.objects.get(id=id)
            text.save()
            
