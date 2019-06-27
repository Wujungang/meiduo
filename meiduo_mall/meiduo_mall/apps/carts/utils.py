import pickle
import base64
from django_redis import get_redis_connection

def merge_cart_cookie_to_redis(request,user,response):
    #获取cookie中的购物车数据
    cart_cookie = request.COOKIES.get('cart')
    #判断购物车数据是否存在
    if cart_cookie:
    #转码成自己需要的数据
        cart_cookies = pickle.loads(base64.b64decode(cart_cookie.encode()))
    #获取redis连接
        redis_conn = get_redis_connection('cart')
    #获取redis里面的hash数据
        sku_dict = redis_conn.hgetall('cart_%s'%user.id)
    #获取redis中的set数据
        selected_list = redis_conn.smembers('cart_selected_%s'%user.id)
    #创建空的字典用来存储数据
        cart = {}
    #遍历redis中的hash数据，创建字典数据
        for sku_id,count in sku_dict.items():
            cart[int(sku_id)] = count
    #遍历cookie中的字典，仿照redis中的数据，将数据添加到redis的数据类型中
        for sku_id,selected_count_dict in cart_cookies.items():
            cart[int(sku_id)] = selected_count_dict['count']
            if selected_count_dict['selected']:
                selected_list.add(sku_id)
    #判断是否有需要合并的数据
        if cart:
        #创建管道
            # pl = redis_conn.pipeline()
        #将数据合并到set和hash中
            redis_conn.hmset('cart_%s'%user.id,cart)
            redis_conn.sadd('cart_selected_%s'%user.id,*selected_list)
            # pl.execute()
    #删除cokie中的数据
        response.delete_cookie('cart')
    #返回响应体
    return response