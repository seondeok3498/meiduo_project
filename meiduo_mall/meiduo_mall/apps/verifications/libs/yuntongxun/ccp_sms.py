# -*- coding:utf-8 -*-
import ssl

from verifications.libs.yuntongxun.CCPRestSDK import REST

ssl._create_default_https_context = ssl._create_stdlib_context # 解决Mac开发环境下，网络错误的问题


# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountSid = '8a216da86a960fd9016aa4ef13da0cf6'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = '357879dece4f495b8a6514b2189c0344'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8a216da86a960fd9016aa5d6eeab0d97'

# 说明：请求地址，生产环境配置成app.cloopen.com
_serverIP = 'sandboxapp.cloopen.com'

# 说明：请求端口 ，生产环境为8883
_serverPort = "8883"

# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'


class CCP(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(CCP, '_instance'):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._instance.rest = REST(_serverIP, _serverPort, _softVersion)
            cls._instance.rest.setAccount(_accountSid, _accountToken)
            cls._instance.rest.setAppId(_appId)

        return cls._instance

    def send_templates_cmc(self, to, datas, tempId):
        result = self._instance.rest.sendTemplateSMS(to, datas, tempId)
        print(result)

        if result.get('statusCode') == '000000':
            return 0
        else:
            return -1


if __name__ == '__main__':
    # 注意： 测试的短信模板编号为1
    # sendTemplateSMS('17600992168', ['123456', 5], 1)
    # CCP().send_templates_cmc('15234414746', ['306011', 5], 1)
    CCP().send_templates_cmc('13620623111', ['306011', 5], 1)

