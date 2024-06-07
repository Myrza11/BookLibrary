from django.shortcuts import render
from rest_framework.permissions import AllowAny
from book.serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

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

