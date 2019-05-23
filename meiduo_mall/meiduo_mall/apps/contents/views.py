from django.shortcuts import render
from django.views import View

from collections import OrderedDict

from .utils import get_categories
from .models import Content, ContentCategory
# Create your views here.


class IndexView(View):
    def get(self, request):
        categories = get_categories()

        contents = OrderedDict()
        content_categories = ContentCategory.objects.all()
        for content_category in content_categories:
            contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')
        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request, 'index.html', context)
