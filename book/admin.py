from django.contrib import admin
from book.models import *
# Register your models here.
admin.site.register(Books)
admin.site.register(Pages)
admin.site.register(LastPage)