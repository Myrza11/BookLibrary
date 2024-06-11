from django.shortcuts import render
from rest_framework.permissions import AllowAny
from book.serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from googletrans import Translator



# Create your views here.
class GetPageView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetPageSerailizer

    def get(self, reqest, pk):
        try:
            objPages = Pages.objects.filter(book_id=pk)
            serializer = GetPageSerailizer(objPages, many=True)
            if not objPages.exists():
                return Response({'error': 'this book does not exist1'}, status=status.HTTP_400_BAD_REQUEST)
            objLastPage = LastPage.objects.create(book_id=objPages.first().book_id, pagenumber=1, user_id=reqest.user)
            objLastPage.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'this book does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        

class GetLastPagesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LastPageSerializer
    queryset = LastPage.objects.all()

    def get_books(self):
        return self.queryset
    

class BooksPagesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BooksSerializer
    queryset = Books.objects.all()

    def get_books(self):
        return self.queryset


class GetAllPagesBookView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetPageSerailizer

    def get(self, request, pk):
        serializer = GetPageSerailizer(Pages.objects.filter(book_id=pk), many=True)
        if len(serializer.data) != 0:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'this book does not exist'})


class FavoriteCreateView(generics.CreateAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class BookRatingView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookRatingSerializer

    def post(self, request):
        serializer = BookRatingSerializer(data=request.data, context={'request': request, 'user': request.user}, partial=True)
        print('hjhbhvghelloo')
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'you rated the book'}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response({'error': 'something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


class ReadBookView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReadBookSerializer

    def patch(self, request, pk):
        try:
            book = Books.objects.get(id=pk)
        except Books.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReadBookSerializer(data=request.data, partial=True, context={'request': request, 'pk': pk})
        if serializer.is_valid():
            serializer.save()
            objLastPage = LastPage.objects.get(book_id=book, user_id=request.user)
            validated_data = serializer.validated_data
            pagenumber = validated_data.get('pagenumber')
            want_continue = validated_data.get('want_continue')

            if (objLastPage.pagenumber > pagenumber or objLastPage.pagenumber < pagenumber) and want_continue != 'Yes':
                return Response({'suggest_return': f'You stopped in page {objLastPage.pagenumber}. Do you want to come back?'})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        recommendations = self.get_book_recommendations(user)  # Передаем user.id
        serializer = BooksSerializer(recommendations, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_book_recommendations(self, user_id, top_n=5):
        user_ratings = BookRating.objects.filter(user_id=user_id)

        # Collect ratings of all users
        ratings = BookRating.objects.all()

        # Create a dictionary to store user ratings
        user_ratings_dict = defaultdict(dict)
        for rating in ratings:
            user_ratings_dict[rating.user_id][rating.book_id] = rating.rate

        # Get the list of all users and books
        user_ids = list(user_ratings_dict.keys())
        book_ids = list(set(rating.book_id for rating in ratings))

        # Create a rating matrix
        rating_matrix = np.zeros((len(user_ids), len(book_ids)))
        for user_idx, user in enumerate(user_ids):
            for book_idx, book in enumerate(book_ids):
                rating_matrix[user_idx, book_idx] = user_ratings_dict[user].get(book, 0)

        # Compute user similarity using cosine_similarity
        user_similarity = cosine_similarity(rating_matrix)

        # Find the index of the current user in the user_ids list
        try:
            user_index = user_ids.index(user_id)
        except ValueError:
            return []

        # Get the similarity of the current user with other users
        similarity_scores = user_similarity[user_index]

        # Rank users by similarity and exclude the user itself
        similar_users = np.argsort(similarity_scores)[::-1]
        similar_users = similar_users[similar_users != user_index]

        # Recommendations based on similar users' ratings
        recommendations = defaultdict(float)
        for similar_user in similar_users[:top_n]:
            similar_user_id = user_ids[similar_user]
            similar_user_ratings = user_ratings_dict[similar_user_id]
            for book_id, rating in similar_user_ratings.items():
                if book_id not in user_ratings_dict[user_id]:
                    recommendations[book_id] += rating * similarity_scores[similar_user]

        # Get top-N recommended books
        recommended_book_ids = [book_id for book_id, score in sorted(recommendations.items(), key=lambda x: x[1], reverse=True)][:top_n]

        # Filter Books based on the recommended book IDs
        recommended_books = Books.objects.filter(id__in=recommended_book_ids)
        return recommended_books


class TranslateTextView(APIView):
    def post(self, request):
        serializer = TranslateTextSerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data['text']
            target_language = serializer.validated_data['target_language']

            translator = Translator()
            try:
                translated = translator.translate(text, dest=target_language)
                return Response({'translated_text': translated.text}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)