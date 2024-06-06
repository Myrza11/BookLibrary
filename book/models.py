from django.db import models
import fitz
from register.models import CustomUser
# Create your models here.

class Books(models.Model):
    name = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    image = models.ImageField(upload_to='author/')
    pdfText = models.FileField(upload_to='pdfs/')

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
        for i in word:
            pagetext += i
            if len(pagetext) >= 20:
                a = Pages.objects.create(book_id=self, text=pagetext, pagenumber=page)
                a.save()
                pagetext = ''
                page += 1


class Pages(models.Model):
    book_id = models.ForeignKey(Books, on_delete=models.CASCADE)
    text = models.TextField()
    pagenumber = models.IntegerField()


class LastPage(models.Model):
    book_id = models.ForeignKey(Books, on_delete=models.CASCADE)
    pagenumber = models.IntegerField()
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    