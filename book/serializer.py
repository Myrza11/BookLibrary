from rest_framework import serializers
from .models import *
from django.core.validators import MinValueValidator, MaxValueValidator
from collections import defaultdict
from django.db.models import Count, F, Q


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

        try:
            objPage = Pages.objects.get(book_id=objBook, pagenumber=pagenumber)
        except:
            raise serializers.ValidationError({'error': 'This page does not exist'})
            
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
        


class FavoriteSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Favorite
        fields = '__all__'

    def create(self, validated_data):
        validated_data['user_id'] = self.context['request'].user
        return super().create(validated_data)
    

class BookRatingSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=False)
    book_id = serializers.IntegerField()
    rate = serializers.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        model = BookRating
        fields = '__all__'
    
    def create(self, validated_data):
        print('hel')
        validated_data['user_id'] = self.context['request'].user
        book_id=validated_data.get('book_id')
        rate=validated_data.get('rate')
        objbook = Books.objects.get(id=book_id)
        user_id=self.context['request'].user
        print('holloooooo')
        try:
            objBookRating = BookRating.objects.get(user_id=user_id, book_id=objbook)
            objBookRating.rate = rate
            objBookRating.save()
            print('jhnhjn')
            
            if objbook.peoplerate is None:
                print('hello')
                objbook.rate = rate
                objbook.peoplerate = 1
                objbook.save()
            
            newrate = (objbook.peoplerate * objbook.rate + rate) / (objbook.peoplerate + 1)
            objbook.peoplerate = objbook.peoplerate + 1
            objbook.rate = newrate
            objbook.save()
            
            return objBookRating
        except:
            objBookRating = BookRating.objects.create(user_id=user_id, book_id=objbook, rate=rate)
            objBookRating.save()
            print('world')
            if objbook.peoplerate is None:
                print('hello')
                objbook.rate = rate
                objbook.peoplerate = 1
                objbook.save()

            return objBookRating


class TranslateTextSerializer(serializers.Serializer):
    text = serializers.CharField()
    target_language = serializers.ChoiceField(choices=[
        'af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg', 'ca', 'ceb', 'ny', 'zh-cn', 'zh-tw', 'co', 'hr',
        'cs', 'da', 'nl', 'en', 'eo', 'et', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gu', 'ht', 'ha', 'haw', 'iw',
        'hi', 'hmn', 'hu', 'is', 'ig', 'id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km', 'rw', 'ko', 'ku', 'ky', 'lo', 'la',
        'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'my', 'ne', 'no', 'or', 'ps', 'fa', 'pl', 'pt',
        'pa', 'ro', 'ru', 'sm', 'gd', 'sr', 'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta',
        'tt', 'te', 'th', 'tr', 'tk', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu'
    ])
    if text is None or target_language is None:
        raise serializers.ValidationError({'error': 'there is NO text or NO target_lenguage'})