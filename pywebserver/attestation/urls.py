from django.urls import path
from django.conf.urls import url
from . import views
from .models import Link
from jsonrpc.backend.django import api
from methods import get_info
from django.forms.models import model_to_dict

urlpatterns = [
   path('', views.index, name='index'),
   path('loading', views.loading, name='loading'),
   path('progress.png', views.progress, name='progress'),
   url('^info/(?P<pid>[^/]+)/(?P<nmlid>[^/]+)/(?P<words>.+)$', views.info, name='info'),
]


@api.dispatcher.add_method
def get_info(pid, words=[], request=None):
    return get_info(pid, words)


@api.dispatcher.add_method
def ping(request=None):
    return 'pong'


@api.dispatcher.add_method
def update_item(pid, nmlid, status, kind, extras, request=None):
    items = Link.objects.filter(pid=pid, nmlid=nmlid)
    items.update(status=status, kind=kind, extras=extras)
    return len(items)


@api.dispatcher.add_method
def get_kinds(kind='', request=None):
    return [d['kind'] for d in Link.objects.values('kind').distinct()]


@api.dispatcher.add_method
def get_itemzzs2(amount=100, request=None):
    links = Link.objects.filter(status=Link.UNDEFINED).order_by('?')[0:amount]
    return [model_to_dict(d) for d in links]


@api.dispatcher.add_method
def get_items(amount=1, request=None):
    links = Link.objects.filter(status=Link.UNDEFINED, distance__lte=2).order_by('?')[0:amount]
    return [model_to_dict(d) for d in links]
