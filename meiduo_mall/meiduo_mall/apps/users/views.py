from django.shortcuts import render, redirect
from django.views import View
from django import http
import re
from django.db import DatabaseError
from django.urls import reverse
from django.contrib.auth import login
from django_redis import get_redis_connection

from users.models import User
from meiduo_mall.utils.response_code import RETCODE

# Create your views here.


class UsernameCountView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'count': count
        })


class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'count': count
        })


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code_client = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        if not all([username, password, password2, mobile, allow, sms_code_client]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        if not re.match(r'^[a-zA-Z0-9-]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20个字符的密码')
        if password2 != password:
            return http.HttpResponseForbidden('两次密码输入不一致')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号')

        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        sms_code_server = sms_code_server.decode()
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码已失效'})
        if sms_code_client != sms_code_server:
            return render(request, 'register', {'sms_code_errmsg': '输入短信验证码有误'})

        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        # return render(request, 'register.html', {'register_errmsg': '注册失败'})

        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        login(request, user)

        return redirect(reverse('contents:index'))

