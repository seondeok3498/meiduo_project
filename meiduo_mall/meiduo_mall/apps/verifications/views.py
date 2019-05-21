import random
import logging

from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http

from verifications.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
from . import constants
from verifications.libs.yuntongxun.ccp_sms import CCP
from celery_tasks.sms.tasks import send_sms_code

# Create your views here.


logger = logging.getLogger('django')


class SMSCodeView(View):
    def get(self, request, mobile):
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        if not all([image_code_client, uuid]):
            return http.JsonResponse({
                'code': RETCODE.NECESSARYPARAMERR,
                'errmsg': '缺少必传参数',
            })

        redis_conn = get_redis_connection('verify_code')
        send_flag_mobile = redis_conn.get('send_flag_%s' % mobile)
        if send_flag_mobile:
            return http.JsonResponse({
                'code': RETCODE.THROTTLINGERR,
                'errmsg': '发送短信过于频繁',
            })

        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '图形验证码失效',
            })
        redis_conn.delete('img_%s' % uuid)

        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '输入图形验证码有误'
            })

        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # CCP().send_templates_cmc(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
        #                          constants.SEND_SMS_TEMPLATE_ID)
        send_sms_code.delay(mobile, sms_code)

        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': '发送短信成功',
        })


class ImageCodeView(View):
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return http.HttpResponse(image, content_type='image/jpg')
