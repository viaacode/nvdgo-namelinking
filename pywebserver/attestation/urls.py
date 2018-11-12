from django.urls import path
from django.conf.urls import url
from . import views
from .models import Link
from jsonrpc.backend.django import api
from lib import previews
from lib.dubbels import get_all_for_pid
from django.forms.models import model_to_dict

urlpatterns = [
   url('^(?:model-(?P<model>[^/]+))?$', views.index, name='index'),
   path('loading', views.loading, name='loading'),
   url('progress(?:-(?P<model>[a-z]+))?.png', views.progress, name='progress'),
   url('^info(?:/model-(?P<model>[^/]+))?/(?P<pid>[^/]+)/?$', views.pid, name='pid'),
   url('^info(?:/model-(?P<model>[^/]+))?/(?P<pid>[^/]+)/(?P<nmlid>[^/]+)/(?P<words>.+)$', views.info, name='info'),
]


@api.dispatcher.add_method
def get_info(pid, words=[], request=None):
    return previews.get_info(pid, words)


@api.dispatcher.add_method
def ping(request=None):
    return 'pong'


@api.dispatcher.add_method
def update_item(model, pid, nmlid, status, kind, extras, request=None):
    model = views.get_model(model)

    # update the dubbels as well
    pids = get_all_for_pid(pid)
    items = model.objects.filter(pid__in=pids, nmlid=nmlid)
    items.update(status=status, kind=kind, extras=extras)
    return len(items)


@api.dispatcher.add_method
def get_kinds(kind='', model=None, request=None):
    model = views.get_model(model)
    return [d['kind'] for d in model.objects.values('kind').distinct()]


def linkmodel_to_dict(model):
    result = model_to_dict(model)
    properties = ('url', 'status_class', 'status_text')
    for prop in properties:
        result[prop] = getattr(model, prop)
    return result


@api.dispatcher.add_method
def get_items(amount=1, model=None, order_by='?', request=None):
    model = views.get_model(model)
    links = model.objects.filter(status=model.UNDEFINED).order_by(order_by)[0:amount]
    return list(map(linkmodel_to_dict, links))

