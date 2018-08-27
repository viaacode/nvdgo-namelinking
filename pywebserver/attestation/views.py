from django.shortcuts import render
from . import models
from django.db.models import Count
from lib.previews import get_info
from django.http.response import HttpResponse
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logging

DEFAULT_MODEL = 'namenlijst'


def get_model(model=None) -> models.LinkBase:
    if model is None:
        model = DEFAULT_MODEL
    model = 'Link%s' % model.title()
    return models.__dict__[model]


def __render(request, file, context={}):
    return render(request, file, context=context)


def index(request, model=None):
    if model is None:
        model = DEFAULT_MODEL
    return __render(request, 'index.html', context={"model": model})


def loading(request):
    return __render(request, 'loading.html')


def pid(request, pid, model=None):
    if model is None:
        model = DEFAULT_MODEL

    link = get_model(model)
    links = list(link.objects.filter(pid=pid))
    words = [link.entity.split(' ') for link in links]
    logging.getLogger('pythonmodules').debug('words: %s', str(words))
    context = get_info(pid, words, extra_previews=False)
    context['model'] = model
    context['Link'] = link
    context['links'] = links

    return __render(request, 'pid.html', context=context)


def info(request, pid, nmlid, words='', model=None):
    if model is None:
        model = DEFAULT_MODEL
    words = words.split('/')
    context = get_info(pid, words)
    context['nmlid'] = nmlid
    context['model'] = model
    context['Link'] = get_model(model)
    context['entity'] = ' '.join(words)
    obj = context['Link'].objects.filter(nmlid=nmlid, pid=pid).first()
    if obj:
        context['status'] = obj.status
        context['kind'] = obj.kind
        context['extras'] = obj.extras
        context['url'] = obj.url()
    else:
        context['status'] = context['Link'].UNDEFINED
        context['url'] = ''

    return __render(request, 'info.html', context=context)


def progress(request, model=None):
    model = get_model(model)
    data = model.objects.all().values('status').annotate(total=Count('status'))
    notdone_count = [p['total'] for p in data if p['status'] == model.UNDEFINED][0]
    data = [p for p in data if p['status'] not in [model.UNDEFINED, model.SKIP]]
    x = [[l[1] for l in model.STATUS_CHOICES if l[0] == p['status']][0] for p in data]
    y = [p['total'] for p in data]
    if len(data) is 0:
        x = [k[1] for k in model.STATUS_CHOICES if k[0] == model.UNDEFINED]
        y = [notdone_count]
    fig = plt.figure(figsize=(5, 8))
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(x, y, label='amount')
    ax.set_title('Attestation counts (%d not yet done)' % notdone_count)
    ax.legend()

    io = BytesIO()
    fig.savefig(io, format='png')
    return HttpResponse(io.getvalue(), content_type="image/png")