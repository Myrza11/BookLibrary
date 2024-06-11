from django.db import models
import fitz
from register.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework.response import Response
from django.core.files.base import ContentFile
from gtts import gTTS
import os
from BookLibrary import settings
from urllib.parse import urljoin
# Create your models here.

class Books(models.Model):
    name = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    image = models.ImageField(upload_to='author/')
    pdfText = models.FileField(upload_to='pdfs/')
    rate = models.IntegerField(null=True, blank=True)
    peoplerate = models.IntegerField(null=True, blank=True)
    page = models.IntegerField(null=True, blank=True)

    def get_word(self, text):
        doc = fitz.open(text)
        text = ''
        for page in doc:
            text += page.get_text()
        return text

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        text = self.get_word(self.pdfText.path)
        word = text.split()
        pagetext = ''
        page = 1
        pages_to_save = []
        for i in word:
            pagetext += i
            if len(pagetext) >= 500:
                file_name = f'{self.name}_{page}.mp3'
                audio_url = self.create_audio(pagetext, file_name)
                objPages = Pages(book_id=self, text=pagetext, pagenumber=page, audio=audio_url)
                pages_to_save.append(objPages)
                pagetext = ''
                page += 1
        Pages.objects.bulk_create(pages_to_save)

        page_count = len(pages_to_save)
        self.page = page_count
        super().save(*args, **kwargs)
    
    def create_audio(self, text, file_name):

        tts = gTTS(text=text, lang='en') 
        audio_directory = os.path.join(settings.MEDIA_ROOT, 'audio')
        print('hello')
        if not os.path.exists(audio_directory):
            os.makedirs(audio_directory)
        
        audio_file_path = os.path.join('audio', file_name)
        print('heloooooo')
        audio_url = urljoin(settings.MEDIA_URL, f'audio/{file_name}')
        print(audio_url)
        absolute_file_path = os.path.join(settings.MEDIA_ROOT, audio_file_path)
        print('world')
        tts.save(absolute_file_path)
        return audio_url



class Pages(models.Model):
    book_id = models.ForeignKey(Books, on_delete=models.CASCADE)
    text = models.TextField()
    audio = models.URLField(editable=False)
    pagenumber = models.IntegerField()


class LastPage(models.Model):
    book_id = models.ForeignKey(Books, on_delete=models.CASCADE)
    pagenumber = models.IntegerField()
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    

class Favorite(models.Model):
    book_id = models.ForeignKey(Books, on_delete=models.CASCADE)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class BookRating(models.Model):
    book_id = models.ForeignKey(Books, on_delete=models.CASCADE)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

