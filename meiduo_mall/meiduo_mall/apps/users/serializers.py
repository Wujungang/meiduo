import re

from django.conf import settings
from django.core.mail import send_mail
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from celery_tasks.email.tasks import send_active_email
from users.models import User, Address


class UserAddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time',)

    def validate_mobile(self,value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号验证失败')
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AddressTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('title',)





class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email')

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()
        to_email = validated_data['email']
        verify_url = instance.generate_verify_email_url()
        # send_active_email.delay(email,verify_url)

        subject = "美多商城邮箱验证"
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
        send_mail(subject, "", settings.EMAIL_FROM, [to_email], html_message=html_message)

        return instance



class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','mobile','email','email_active')



class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码',write_only=True)
    sms_code = serializers.CharField(label='短信验证码',write_only=True)
    allow = serializers.CharField(label='同意协议',write_only=True)
    token = serializers.CharField(label='登录状态token',read_only=True)
    class Meta:
        model = User
        fields = ('token','id','username','password','password2','sms_code','mobile','allow')
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
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        redis_conn = get_redis_connection('verify_codes')
        mobile = attrs['mobile']
        real_sms_code = redis_conn.get('sms_%s'%mobile)
        real_sms_code = real_sms_code.decode()
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
        user.set_password(validated_data['password'])
        user.save()
        #系统提供地方生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user