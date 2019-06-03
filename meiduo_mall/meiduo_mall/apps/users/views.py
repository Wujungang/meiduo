from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from users.models import User
from . import serializers
# Create your views here.



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