from decimal import Decimal

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from . import serializers

class OrderSettlementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user

        #获取redis的连接对象
        redis_conn = get_redis_connection('cart')
        #获取hash里面的数据
        redis_dict = redis_conn.hgetall('cart_%s'%user.id)
        #获取set里面的数据
        selected_list = redis_conn.smembers('cart_selected_%s'%user.id)
        #创建空字典用于以后存储数据
        cart = {}
        #遍历是否勾选的列表
        for sku_id in selected_list:
            #创建数据对象
            cart[int(sku_id)] = int(redis_dict[sku_id])
        #获取勾选商品的商品对象
        skus = SKU.objects.filter(id__in=cart.keys())
        #遍历商品对象
        for sku in skus:
            #给商品对象添加数量
            sku.count = cart[sku.id]
        #设置运费
        freight = Decimal('10.00')
        #使用序列化器，序列化对象
        serializer = serializers.OrderSettlementSerializer({'freight':freight,'skus':skus})
        #返回相应对象
        print(serializer.data)
        return Response(serializer.data)

