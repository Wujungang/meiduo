from decimal import Decimal

from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
# from utils.exceptions import logger


class SaveOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        """保存订单"""

        # 获取当前下单用户
        user = self.context['request'].user
        # 生成订单编号
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d'%user.id)

        address = validated_data['address']
        pay_method = validated_data['pay_method']
        # 保存订单基本信息数据 OrderInfo
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user = user,
                    address = address,
                    total_count = 0,
                    total_amount = Decimal(0),
                    freight=Decimal(10),
                    pay_method = pay_method,
                    # status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID'],
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID']

                )
        # 从redis中获取购物车结算商品数据
                redis_conn = get_redis_connection('cart')
                redis_cart = redis_conn.hgetall('cart_%s'%user.id)
                cart_selected = redis_conn.smembers('cart_selected_%s'%user.id)
                cart = {}
                for sku_id in cart_selected:
                    cart[int(sku_id)] = int(redis_cart[sku_id])
                skus = SKU.objects.filter(id__in=cart.keys())
                for sku in skus:
                    sku_count = cart[sku.id]
                    origin_stock = sku.stock
                    origin_sales = sku.sales
                    if sku_count > origin_stock:
                        transaction.savepoint_rollback(save_id)
                        raise serializers.ValidationError('商品库存不足')
        # 遍历结算商品：
                    new_stock = origin_stock - sku_count
                    new_sales = origin_sales + sku_count
                    sku.stock +=new_stock
                    sku.sales = new_sales
                    sku.save()
                    sku.goods.sales +=sku_count
                    sku.goods.save()
                    order.total_count += sku_count  # 累计总金额
                    order.total_amount += (sku.price * sku_count)  # 累计总额
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price
                    )
                order.total_amount +=order.freight
                order.save()
        # 判断商品库存是否充足
            except ValidationError:
                raise
            except Exception as e:
                # logger.error(e)
                transaction.savepoint_rollback(save_id)
                raise
            transaction.savepoint_commit(save_id)
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s'%user.id,*cart_selected)
            # pl.hdel('cart_%s' % user.id, *redis_cart_selected)

            pl.srem('cart_selected_%s'%user.id,*cart_selected)
            pl.execute()
            return order
class CartSKUSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(label='数量')
    class Meta:
        model = SKU
        fields = ('id','name','default_image_url','price','count')

class OrderSettlementSerializer(serializers.Serializer):
    freight = serializers.DecimalField(label='运费',max_digits=10,decimal_places=2)
    skus = CartSKUSerializer(many=True)