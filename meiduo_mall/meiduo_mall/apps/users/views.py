from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from users.models import User
from . import serializers
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class UserDetailView(RetrieveAPIView):
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user





def favicon(request):
    print(123555)
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