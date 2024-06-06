from django.conf import settings
from rest_framework.permissions import AllowAny
from register.serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema



class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    @extend_schema(tags=['RegisterCreate'])
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        data = request.data
        if serializer.is_valid():
            user = CustomUser.objects.create_user(
                username=data['username'],
                name=data['name'],
                email=data.get('email'),
                password=data['password'],
                is_active=False,
            )
            confirmation_code = get_random_string(length=4, allowed_chars='0123456789')

            user.confirmation_code = confirmation_code
            user.save()

            subject = 'Confirmation code'
            message = f'Your confirmation code is: {confirmation_code}'
            from_email = 'bapaevmyrza038@gmail.com'
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            # Вместо отправки на почту возвращаем код в Response
            #response_data = {
            #    'id': user.id,
            #    'username': user.username,
            #    'email': user.email,
            #    'name': user.name,
            #    'avatar': user.avatar.url if user.avatar else None,
            #    'created_at': user.created_at,
            #    'is_active': user.is_active,
            #    'confirmation_code': confirmation_code,
            #}
            #return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(tags=['RegisterCreate'])
    def patch(self, request):
        confirmation_code = request.data.get('confirmation_code')
        if not confirmation_code:
            return Response({'error': 'Confirmation code is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(confirmation_code=confirmation_code, is_active=False)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid or expired confirmation code.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = True
        user.save()

        return Response({'message': 'Email confirmed successfully.'}, status=status.HTTP_200_OK)
    

class CustomUserLoginView(TokenObtainPairView):
    # permission_classes = [AllowAny]
    pass


class CustomUserTokenRefreshView(APIView):

    @extend_schema(tags=['RegisterRefresh'])
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            return Response({'access': access_token,
                             'refresh':token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        

class ForgotPasswordView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer
    queryset = CustomUser.objects.all()

    @extend_schema(tags=['RegisterChange'])
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = request.data.get('email')
            username = request.data.get('username')
            if not email or not username:
                return Response({'error': 'One of the fields is empty'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = CustomUser.objects.get(email=email, username=username)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            
            confirmation_code = get_random_string(4, allowed_chars='0123456789')
            user.confirmation_code = confirmation_code
            user.save()
            confirmation_code = user.confirmation_code
            subject = 'Confirmation code'
            message = f'Your confirmation code is: {confirmation_code}'
            from_email = 'bapaevmyrza038@gmail.com'  
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return Response({'message': 'Confirmation code sent successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer
    queryset = CustomUser.objects.all()

    @extend_schema(tags=['RegisterChange'])
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Получение данных из запроса
            email = request.data.get('email')
            username = request.data.get('username')
            confirmation_code = request.data.get('confirmation_code')
            new_password = request.data.get('new_password')

            if not all([email, username, confirmation_code, new_password]):
                return Response({'error': 'One of the fields missed'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = CustomUser.objects.get(email=email, username=username)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            if user.confirmation_code != confirmation_code:
                return Response({'error': 'Confirmation code is not match'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            return Response({'success': 'Password successfully updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(tags=['RegisterChange'])
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.data.get('old_password')
            new_password = serializer.data.get('new_password')

            user = request.user
            if not user.check_password(old_password):
                return Response({'error': 'Old password is wrong'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response({'success': 'Password is changed'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ChangeUsernameView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['RegisterChange'])
    def post(self, request):
        serializer = ChangeUsernameSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            new_username = serializer.data.get("new_username")
            if user.name == new_username:
                return Response({'error': 'This username already in use'}, status=status.HTTP_400_BAD_REQUEST)

            user.username = new_username
            user.save()

            return Response({"detail": "Username changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

    @extend_schema(tags=['RegisterList'])
    def get_users(self):
        return self.queryset


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

    @extend_schema(
        tags=['RegisterChange'],
        operation_id='update_user_with_patch'
    )
    def patch(self, request, *args, **kwargs):
        allowed_fields = ['avatar']
        data = {k: v for k, v in request.data.items() if k in allowed_fields}

        serializer = self.serializer_class(self.get_object(), data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
