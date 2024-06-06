from django.urls import path
from book.views import *
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('pages/<int:pk>/', GetPageView.as_view()),
    path('yourbooks/', GetLastPagesView.as_view()),
    path('page/<int:pk>/', ReadBookView.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)