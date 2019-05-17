from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings

from .constants import ACCESS_TOKEN_EXPIRES


def check_access_token(access_token_openid):
    s = Serializer(settings.SECRET_KEY, ACCESS_TOKEN_EXPIRES)
    try:
        data = s.loads(access_token_openid)
    except BadData:
        return None
    else:
        openid = data.get('openid')
        return openid


def generate_access_token(openid):
    s = Serializer(settings.SECRET_KEY, ACCESS_TOKEN_EXPIRES)
    data = {'openid': openid}
    access_token_openid = s.dumps(data)
    return access_token_openid.decode()
