from django.conf.urls import url
from . import views
# from meiduo_mall.libs.captcha.captcha.captcha import captcha

urlpatterns = [
    url(r'image_codes/(?P<image_code_id>[\w-]+)/',views.ImageCodeView.as_view())
]