import logging

from django.shortcuts import render
from django.views import View
from django import http
from django.core.cache import cache

# Create your views here.
from .models import Area
from meiduo_mall.utils.response_code import RETCODE

logger = logging.getLogger('django')


class AreasView(View):
    def get(self, request):
        area_id = request.GET.get('area_id')
        if not area_id:
            province_list = cache.get('province_list')
            if not province_list:
                try:
                    province_model_list = Area.objects.filter(parent__isnull=True)

                    province_list = []
                    for province_model in province_model_list:
                        province_dict ={
                            'id': province_model.id,
                            'name': province_model.name,
                        }
                        province_list.append(province_dict)

                    cache.set('province_list', province_list, 3600)

                except Area.DoesNotExist as e:
                    logger.error(e)
                    return http.JsonResponse({
                        'code': RETCODE.DBERR,
                        'errmsg': '省份数据错误',
                    })
            return http.JsonResponse({
                'code': RETCODE.OK,
                'errmsg': 'OK',
                'province_list': province_list,
            })

        else:
            sub_data = cache.get('sub_area_' + area_id)

            if not sub_data:
                try:
                    parent_model = Area.objects.get(id=area_id)
                    # city_model_list = Area.object.filter(parent=province_model)
                    sub_model_list = parent_model.subs.all()

                    sub_list = []
                    for sub_model in sub_model_list:
                        sub_dict = {
                            'id': sub_model.id,
                            'name': sub_model.name,
                        }
                        sub_list.append(sub_dict)

                    sub_data = {
                        'id': parent_model.id,
                        'name': parent_model.name,
                        'subs': sub_list,
                    }
                    cache.set('sub_area_' + area_id, sub_data, 3600)

                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({
                        'code': RETCODE.DBERR,
                        'errmsg': '城市或区域数据错误',
                    })

            return http.JsonResponse({
                'code': RETCODE.OK,
                'errmsg': 'OK',
                'sub_data': sub_data,
            })

