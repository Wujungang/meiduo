from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from goods.models import SKU
from users.models import User
from . import serializers,constants
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django_redis import get_redis_connection
# Create your views here.

class UserBrowsingHistoryView(CreateAPIView):
    serializer_class = serializers.AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    # def post(self,request):
    #     return self.create(request)
    def get(self,request):
        #获取用户id
        user_id = request.user.id

        #获取数据库连接方式
        redis_conn = get_redis_connection('history')
        #获取列表中的数据
        history = redis_conn.lrange('history_%s'%user_id,0,4)
        skus = []
        for sku_id in history:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)
        s = serializers.SKUSerializer(skus,many=True)
        return Response(s.data)






class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin,mixins.ListModelMixin, GenericViewSet):
    serializer_class = serializers.UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self,request,*args,**kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    def create(self, request, *args, **kwargs):
        count = request.user.addresses.count()
        if count > constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message':'保存地址数据已经达到上限'},status=status.HTTP_400_BAD_REQUEST)
        return super().create(request,*args,**kwargs)

    def destroy(self,request,*args,**kwargs):
        address = self.get_object()
        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    #保存默认地址
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None, address_id=None):
        address = self.get_object()
        user = request.user
        user.default_address = address
        user.save()
        return Response({'message':'保存用户默认地址成功'},status=status.HTTP_200_OK)

    #更新标题
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None, address_id=None):
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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