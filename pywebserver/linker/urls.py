from django.urls import path
from django.conf.urls import url
from . import views
import pandas as pd
import numpy as np
from .models import Link
from jsonrpc.backend.django import api

urlpatterns = [
   path('', views.index, name='index'),
   path('loading', views.loading, name='loading'),
   # path('details/<pid>', views.details, name='details'),
   url('^details/(?P<pid>[^/]+)/(?P<nmlid>[^/]+)/(?P<words>.+)$', views.detailframe, name='detailframe'),
   url('^info/(?P<pid>[^/]+)/(?P<nmlid>[^/]+)/(?P<words>.+)$', views.details, name='details'),
]

@api.dispatcher.add_method
def get_info(pid, words = [], request = None):
    from methods import get_info
    return get_info(pid, words)

@api.dispatcher.add_method
def ping(request = None):
    return 'pong'


@api.dispatcher.add_method
def update_item(id, status, kind, extras, request = None):
    items = Link.objects.filter(id=id)
    items.update(status = status, kind = kind, extras = extras)
    # csvfile = '/Users/mike/Scripts/nvdgo-namelinking/ui/results.csv'
    # df = pd.read_csv(csvfile).fillna('')
    # mask = (df['nmlid'] == nmlid) & (df['article_id'] == article_id)
    # df.loc[mask, 'status'] = status
    # df.loc[mask, 'kind'] = kind
    # df.loc[mask, 'extras'] = extras
    # df.to_csv(csvfile, index=False)
    return len(items)


@api.dispatcher.add_method
def import_csv(request = None):
    location = '/Users/mike/Scripts/nvdgo-namelinking/ui/results.csv'

    df = pd.read_csv(location).fillna('')

    fields = [
        'status',
        'entity',
        'article_date',
        'title',
        'article_id',
        'firstname',
        'lastname',
        'nmlid',
        'kind',
        'extras'
    ]

    i = 0
    for row in df.itertuples():
        data = {k: getattr(row, k, k) for k in fields}
        data['id'] = '|'.join((data['article_id'], data['nmlid'], data['entity'],))
        link = Link(**data)
        link.save()
        i += 1

    return i

@api.dispatcher.add_method
def get_kinds(kind = '', request = None):
    return [d['kind'] for d in Link.objects.values('kind').distinct()]

@api.dispatcher.add_method
def get_items(amount = 100, request = None):
    from django.forms.models import model_to_dict
    links = Link.objects.filter(status = '').order_by('?')[0:amount]
    return [model_to_dict(d) for d in links]
