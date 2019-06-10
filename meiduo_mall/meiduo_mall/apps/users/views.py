from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from users.models import User
from . import serializers
from rest_framework.permissions import IsAuthenticated
# Create your views here.


class VerifyEmailView(APIView):
    def get(self,request):
        token = request.query_params.get('token')
        if not  token:
            return Response({'message':'缺少token'},status=status.HTTP_400_BAD_REQUEST)
        user = User.check_verify_email_token(token)
        if not user:
            return Response({'message':'链接信息无效'},status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            try:
                user.save()
            except Exception as e:
                print(e)
            return Response({'message':'OK'})

class EmailView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.EmailSerializer

    def get_object(self):
        user = self.request.user
        return user

class UserDetailView(RetrieveAPIView):
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

def favicon(request):
    # print(123555)
    return redirect('/static/favicon.ico')

class UserView(CreateAPIView):
    serializer_class = serializers.CreateUserSerializer

class UsernameCountView(APIView):
    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        data = {
            'username':username,
            'count':count
        }
        return Response(data)

class MobileCountView(APIView):
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile':mobile,
            'count':count,
        }
        return Response(data)