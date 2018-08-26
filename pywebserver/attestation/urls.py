from django.urls import path
from django.conf.urls import url
from . import views
from .models import Link
from jsonrpc.backend.django import api
from lib.previews import get_info
from django.forms.models import model_to_dict

urlpatterns = [
   url('^(?:model-(?P<model>[^/]+))?$', views.index, name='index'),
   path('loading', views.loading, name='loading'),
   url('progress(?:-(?P<model>[a-z]+))?.png', views.progress, name='progress'),
   url('^info(?:/model-(?P<model>[^/]+))?/(?P<pid>[^/]+)/?$', views.pid, name='pid'),
   url('^info(?:/model-(?P<model>[^/]+))?/(?P<pid>[^/]+)/(?P<nmlid>[^/]+)/(?P<words>.+)$', views.info, name='info'),
]


def linkmodels_to_dict(links):
    r = []
    for l in links:
        row = model_to_dict(l)
        row['url'] = l.url()
        r.append(row)
    return r


@api.dispatcher.add_method
def get_info(pid, words=[], request=None):
    return get_info(pid, words)


@api.dispatcher.add_method
def ping(request=None):
    return 'pong'


@api.dispatcher.add_method
def update_item(model, pid, nmlid, status, kind, extras, request=None):
    model = views.get_model(model)
    items = model.objects.filter(pid=pid, nmlid=nmlid)
    items.update(status=status, kind=kind, extras=extras)
    return len(items)


@api.dispatcher.add_method
def get_kinds(kind='', model=None, request=None):
    model = views.get_model(model)
    return [d['kind'] for d in model.objects.values('kind').distinct()]


@api.dispatcher.add_method
def get_items(amount=1, model=None, request=None):
    model = views.get_model(model)
    links = model.objects.filter(status=model.UNDEFINED).order_by('?')[0:amount]
    return linkmodels_to_dict(links)
