from django.db import models
import fitz
from register.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Books(models.Model):
    name = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    image = models.ImageField(upload_to='author/')
    pdfText = models.FileField(upload_to='pdfs/')
    rate = models.IntegerField(null=True, blank=True)
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
        for i in word:
            pagetext += i
            if len(pagetext) >= 20:
                objPages = Pages.objects.create(book_id=self, text=pagetext, pagenumber=page)
                objPages.save()
                pagetext = ''
                page += 1
        page = len(Pages.objects.filter(book_id=self))
        self.page = page
        self.save()


class Pages(models.Model):
    book_id = models.ForeignKey(Books, on_delete=models.CASCADE)
    text = models.TextField()
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

    class Meta:
        unique_together = ('user_id', 'book_id')