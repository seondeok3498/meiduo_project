from django.contrib.auth.backends import ModelBackend
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings

from .models import User
from .constants import VERIFY_EMAIL_TOKEN_EXPIRES


def check_verify_email_token(token):
    s = Serializer(settings.SECRET_KEY, VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = s.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')

        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


def generate_verify_email_url(user):
    s = Serializer(settings.SECRET_KEY, VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {
        'user_id': user.id,
        'email': user.email,
    }
    token = s.dumps(data)
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token.decode()
    return verify_url


def get_user_by_account(account):
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user and user.check_password(password):
            return user




