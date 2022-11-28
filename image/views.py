from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer,SharedFileAddSerializer,SharedFileSerializer
from .models import Account,SharedFile
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.urls import reverse
from rest_framework import parsers
from rest_framework import renderers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.sites.shortcuts import get_current_site
from datetime import datetime,timedelta
from django.utils import timezone
# Create your views here.

class RegistrationView(APIView):
    """ handling the registration of the users, sending email verification link """

    def post(self, request, *args, **kwargs):
        data = {}
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            account = serializer.save()
            token = Token.objects.get_or_create(user=account)[0].key
            return Response({'success':'Your account has been created','token': token,'status':status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
        return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class ObtainAuthToken(APIView):
    """ login view (extending built in ObtainAuthClass to renew the token) """

    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    """ 
        everytime a user logs in, user gets a new token which will be used, to send as header 
        with all the requests to the api which are requires authentication.
    """

    def post(self, request):
        account = Account.objects.filter(email=request.data['username'])
        if account.exists():
            serializer = AuthTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']

            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            return Response({'token': token.key,'status':status.HTTP_200_OK}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Your account is not registered.','status':status.HTTP_204_NO_CONTENT}, status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    """ Logout view ( deleting auth_token connneted to user logging out """

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response({'success':"You have been logged out."},status=status.HTTP_200_OK)


class FileSharePostView(APIView):
    """ FileSharePostView view ( uploading files ) """
    permission_classes = [IsAuthenticated]
    def post(self,request,*args,**kwargs):
        token = request.GET.get('token')
        try:
            user = Token.objects.get(key=token).user
        except Token.DoesNotExist:
            return Response({'error': 'The link is expired'}, status=status.HTTP_400_BAD_REQUEST)
        if user is not None:
            serializer = SharedFileAddSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(owner=user)
                return Response({'success':'File shared successfully','link':serializer.data['link']}, status=status.HTTP_201_CREATED)
            return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class FileSharedView(APIView):
    def get(self,request,link,*args,**kwargs):
        # SharedFile.objects.filter(date__lte=datetime.now()).delete()
        files = SharedFile.objects.filter(link=link).first()
        if files:
            if files.expires_on<timezone.now():
                files.delete()
                return Response({'not_found':'This file has been deleted','status':status.HTTP_404_NOT_FOUND})
            serializer = SharedFileSerializer(files,many=False)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'not_found':'This file has been deleted','status':status.HTTP_404_NOT_FOUND})