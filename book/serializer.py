from rest_framework import serializers
from .models import *

class GetPageSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Pages
        fields = '__all__'


class LastPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastPage
        fields = '__all__'


class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = '__all__'


class ReadBookSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=False)
    book_id = serializers.CharField(required=False)
    pagenumber = serializers.IntegerField() 
    want_continue = serializers.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')], required=False)

    class Meta:
        model = Pages
        fields = '__all__'

    def create(self, validated_data):
        book_id = self.context['pk']
        user = self.context['request'].user
        pagenumber = validated_data.get('pagenumber')
        want_continue = validated_data.get('want_continue')
        objBook = Books.objects.get(id=book_id)
        try:
            objLastPage = LastPage.objects.get(book_id=objBook, user_id=user)
        except LastPage.DoesNotExist:
            objLastPage = LastPage.objects.create(book_id=objBook, user_id=user, pagenumber=1)

        objPage = Pages.objects.get(book_id=objBook, pagenumber=pagenumber)
        if want_continue is not None:
            if want_continue == 'Yes':
                return Pages.objects.get(book_id=objBook, pagenumber=objLastPage.pagenumber)
            if want_continue == 'No':
                objLastPage.pagenumber = pagenumber
                objLastPage.save()
                return objPage
            
        elif pagenumber == objLastPage.pagenumber - 1 and objLastPage.pagenumber != 2 or pagenumber == objLastPage.pagenumber + 1:
            objLastPage.pagenumber = pagenumber
            objLastPage.save()
        if objLastPage.pagenumber == objLastPage.pagenumber:
            objLastPage.pagenumber == objLastPage.pagenumber + 1
            objLastPage.save()
            return Pages.objects.get(book_id=objBook, pagenumber=pagenumber)