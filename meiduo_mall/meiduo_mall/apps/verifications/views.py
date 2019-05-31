from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
# Create your views here.
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from verifications import constants


class ImageCodeView(APIView):
    def get(self,request,image_code_id):

        text,image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('img_%s'%image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        return HttpResponse(image,content_type='image/jpg')
