import base64
import pickle

from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.
from goods.models import SKU
from . import serializers


class CartView(APIView):
    def perform_authentication(self, request):
        pass
    def get(self,request):
        #判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None
        if user is not None and user.is_authenticated:
            #获取redis链接对象  cart
            redis_conn = get_redis_connection('cart')
            #从redis中的hash中获取所有的商品id及数量
            cart_dict = redis_conn.hgetall('cart_%s'%user.id)
            #从redis中获取所有商品的勾选状态
            select_list = redis_conn.smember('cart_selected_%s'%user.id)
            #创建空的字典
            cart = {}
            #遍历商品数据
            for sku_id,count in cart_dict.items():
                # 形成商品字典
                cart[sku_id] = {
                    'count':count,
                    'selected':sku_id in select_list
                }
        #用户未登录
        else:
            #从cookie中获取商品信息
            cart = request.COOKIES.get('cart')
            if cart:
                #获取购物车数据
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
        #获取所有商品的对象查询集
        skus = SKU.objects.filter(id__in=cart.keys())
        #遍历商品对象
        for sku in skus:
            #更新商品的数量以及勾选状态
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']
        #序列化商品数据
        serializer = serializers.CartSKUSerializer(skus,many=True)
        #返回商品数据信息
        return Response(serializer.data)

    def post(self,request):
        #获取序列化器
        serializer = serializers.CatSerializer(data=request.data)
        #让序列化器校验
        serializer.is_valid(raise_exception=True)
        #获取序列化器校验后的sku_id
        sku_id = serializer.validated_data['sku_id']
        #获取序列化器校验后的count
        count = serializer.validated_data['count']
        #获取序列化器校验后的selected
        selected = serializer.validated_data['selected']
        #尝试对请求的用户进行验证
        try:
            user = request.user
        except Exception:
            user = None
        if user is not None and user.is_authenticated:
            #创建redis连接对象，连接cart
            redis_conn = get_redis_connection('cart')
            #创建管道
            pl = redis_conn.pipeline()
            #记录购物车商品数量
            pl.hincrby('cart_%s'%user.id,sku_id,count)
            #记录购物车的勾选项
            if selected:
                pl.sadd('cart_selected_%s'%user.id,sku_id)
            pl.execute()
            #成功后返回
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
        #如果用户未登录
            cart = request.COOKIES.get('cart')
            #使用cookie，获取cookie中的购物车数据
        # 判断购物车是否为空
            if cart is not None:
                # 购物车不为空，获取购物车里面的数据
                cart = pickle.loads(base64.b64decode(cart.encode()))
                print(cart)
            # 购物车为空
            else:
                # 创建空字典
                cart = {}
            #查询商品是否在购物车中
            sku = cart.get(sku_id)
            if sku:
            #如果商品在购物车中则，商品数量叠加
                count +=int(sku.get('count'))
            #商品不在购物车里则创建新的商品对象
            cart[sku_id] = {
                'count':count,
                'selected':selected
            }
            #将商品字典进行转码
            cart = base64.b64encode(pickle.dumps(cart)).decode()
            #设置相应对象
            response = Response(serializer.data,status=status.HTTP_201_CREATED)
            #将cookis设置到相应对象中
            response.set_cookie('cart',cart,max_age=60*60*60)
            #返回相应对象
            return response

