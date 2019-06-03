import re

from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码',write_only=True)
    sms_code = serializers.CharField(label='短信验证码',write_only=True)
    allow = serializers.CharField(label='同意协议',write_only=True)

    class Meta:
        model = User
        fields = ('id','username','password','password2','sms_code','mobile','allow')
        extra_kwargs = {
            'username':{
                'min_length':5,
                'max_length':20,
                'error_messages':{
                    'min_length':'仅允许5-20个字符串的用户名',
                    'max_length':'仅允许5-20个字符串的用户名',
                }
            },
            'password':{
                'write_only':True,
                'min_length':5,
                'max_length':20,
                'error_messages':{
                    'min_length':'仅允许5-20个字符串的用户名',
                    'max_length':'仅允许5-20个字符串的用户名',
                }
            },
        }
    def validate_mobile(self,value):
        if not re.match(r'^1[3-9]\d{9}$',value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self,value):
        if value != True:
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        redis_conn = get_redis_connection('verify_codes')
        mobile = attrs['mobile']
        real_sms_code = redis_conn.get('sms_%s'%mobile)
        if not real_sms_code:
            raise serializers.ValidationError('短信验证码不存在')
        if attrs['sms_code'] != real_sms_code:
            raise serializers.ValidationError('短信验证码错误')
        return attrs

    def create(self, validated_data):
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        user = User.objects.create(**validated_data)
        user.save()
        return user