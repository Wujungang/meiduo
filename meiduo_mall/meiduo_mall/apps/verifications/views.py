import random

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
# Create your views here.

from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from utils.yuntongxun.sms import CCP
from . import serializers
from verifications import constants

logger = logging.getLogger('django')

#短信验证码
# url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(GenericAPIView):
    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self,request,mobile):
        #校验参数
        serializer = self.get_serializer(data = request.query_params)
        serializer.is_valid(raise_exception = True)
        #生成短信验证码
        sms_code ='%06d'%random.randint(0,999999)
        #保存短信验证码
        redis_conn = get_redis_connection('verify_codes')
        pl = redis_conn.pipeline()
        pl.setex('sms_%s'%mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        pl.setex('send_flag_%s'%mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        pl.execute()
        #发送短信
        # # 发送短信
        try:
            ccp = CCP()
            expires = constants.SMS_CODE_REDIS_EXPIRES // 60
            result = ccp.send_template_sms(mobile, [sms_code, expires], constants.SMS_CODE_TEMP_ID)
        except Exception as e:
            logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
            return Response({'message': 'failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            if result == 0:
                logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
                return Response({'message': 'OK'})
            else:
                logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
                return Response({'message': 'failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # return Response({'message': 'OK'})





#图片验证码
class ImageCodeView(APIView):
    def get(self,request,image_code_id):

        text,image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('img_%s'%image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        return HttpResponse(image,content_type='image/jpg')
