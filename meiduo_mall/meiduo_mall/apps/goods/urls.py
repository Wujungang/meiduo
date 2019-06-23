from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from . import views
from django.views.generic import RedirectView
# from meiduo_mall.libs.captcha.captcha.captcha import captcha
# from django.views.generic.sim

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view())
    # url(r'^favicon.ico/$', RedirectView.as_view(url=r'/static/favicon.ico')),
    # # url(r'^favicon.ico/', views.favicon),
    # url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
    # url(r'^users/$', views.UserView.as_view()),
    # url(r'^email/$', views.EmailView.as_view()),
    # url(r'^user/$', views.UserDetailView.as_view()),
    # url(r'^usernames/(?P<username>\w{5,20})/count/$',views.UsernameCountView.as_view()),
    # url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # url(r'authorizations/$',obtain_jwt_token),
    # url(r'^browse_histories/$', views.UserBrowsingHistoryView.as_view()),
]