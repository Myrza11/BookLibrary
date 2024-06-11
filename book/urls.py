from django.urls import path
from book.views import *
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView



urlpatterns = [
    path('pageghg/<int:pk>/', GetPageView.as_view()),
    path('yourbooks/', GetLastPagesView.as_view()),
    path('page/<int:pk>/', ReadBookView.as_view()),
    path('favorites/', FavoriteCreateView.as_view()),
    path('pages/<int:pk>/', GetAllPagesBookView.as_view()),
    path('bookrating/', BookRatingView.as_view()),
    path('recommendetion/', RecommendationView.as_view()),
    path('translate/', TranslateTextView.as_view()),
]


