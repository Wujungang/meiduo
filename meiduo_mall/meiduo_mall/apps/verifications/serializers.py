from rest_framework import serializers
from django_redis import get_redis_connection

class ImageCodeCheckSerializer(serializers.Serializer):
    #设置字段
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4,min_length=4)
    #校验

    def validate(self, attrs):
        #接受参数
        image_code_id = attrs['image_code_id']
        text = attrs['text']
        #redis数据库中找出存储的text
        redis_conn = get_redis_connection('verify_codes')
        redis_text = redis_conn.get('img_%s' %image_code_id).decode()
        #防止一个图片验证码被多次使用，查询结束就删除图片验证码
        redis_conn.delete('img_%s' %image_code_id)
        if not redis_text:
            raise serializers.ValidationError('图片验证码无效')
        if redis_text.lower() != text.lower():
            raise serializers.ValidationError('图片验证码无效')

        #检查短信验证码的有效期
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('send_flag_%s'%mobile)
        if send_flag:
            raise serializers.ValidationError('请求次数过于频繁')
        return attrs

