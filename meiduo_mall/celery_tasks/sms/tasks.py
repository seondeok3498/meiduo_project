from celery_tasks.sms.yuntongxun.ccp_sms import CCP
from . import constants
from celery_tasks.main import celery_app


@celery_app.task(bind=True, name='send_sms_code', retry_backoff=3)
def send_sms_code(self, mobile, sms_code):
    try:
        send_ret = CCP().send_templates_cmc(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                            constants.SEND_SMS_TEMPLATE_ID)
    except Exception as e:
        raise self.retry(exc=e, max_retries=3)
    else:
        return send_ret
