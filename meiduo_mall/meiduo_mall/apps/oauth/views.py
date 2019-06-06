from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from oauth.utils import OAuthQQ


class QQAuthURLView(APIView):
    def get(self,request):
        next = request.query_params['next']
        oauth = OAuthQQ(state = next)
        login_url = oauth.get_qq_login_url()
        return Response({'login_url':login_url})