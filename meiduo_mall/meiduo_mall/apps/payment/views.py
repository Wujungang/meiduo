import os
from alipay import AliPay
from django.conf import settings
from django.shortcuts import render

from requests import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from orders.models import OrderInfo
from payment.models import Payment


class PaymentStatusView(APIView):
    def put(self,request):
        #获取查询字符串
        data = request.query_params.dict()
        #pop可以将data中的数据删除并返回删除后的对象
        signature = data.pop('sign')

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        #http://www.meiduo.site:8080/pay_success.html?
        # charset=utf-8&
        # out_trade_no=20190628022038000000001&
        # method=alipay.trade.page.pay.return&
        # total_amount=20374.00&
        # sign=ES0N8xiA6VDNCx094D5YkNuGu%2FJ8D2m7cCRs2dNcA1FkYADI16JifqHJb1zgZ248C4ZFvbYL15v3%2F%2FnmegGpKmXoUGn36qdsQvwBtqBYz1d7rr6rvBmdtvNRbGDCpZqg2RvCNqMxGQr3g0o8baECaaOk23%2B6cvJeryW17TNttOVu4ogrQR4C2Bh8E9iq9Ks5UWaWpgL2mHWeYZjgB5%2BhfkooV1mjGoTxcsiMHIZGKj%2Bx6jrzhbi3yt%2FPpOu5MVL64%2BKAZd8K%2FYUbijSIUW2i87Xp5ri9eroHrd723k9zDZ6ZjwhJ402bwSVXvcYFPLIdwx%2BOi7jqr6GiGZjBx0ttNg%3D%3D&
        # trade_no=2019062822001451771000092260&
        # auth_app_id=2016091300505093&
        # version=1.0&
        # app_id=2016091300505093&
        # sign_type=RSA2&
        # seller_id=2088102175510789&
        # timestamp=2019-06-28+10%3A21%3A55
        success = alipay.verify(data,signature)
        if success:
            order_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])
            return Response({'trade_id': trade_id})
        else:
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,order_id):
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=request.user,
                                          pay_method=OrderInfo.PAY_METHODS_ENUM["ALIPAY"],
                                          status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"])
        except OrderInfo.DoesNotExist:
            return Response({'messsage':'订单信息有误'},status=status.HTTP_400_BAD_REQUEST)

        # 构造支付宝支付链接地址
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )
        # 需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 拼接链接返回前端
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        print(alipay_url)
        return Response({'alipay_url': alipay_url})