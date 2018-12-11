from django.shortcuts import render
from . import models
from django.db.models import Count
from lib.previews import get_info
from django.http.response import HttpResponse
from django.http.response import HttpResponseNotFound
from io import BytesIO
from lib.matcher import Rater
from lib.dubbels import get_all_for_pid
from django.http import Http404
import seaborn as sns
from django.views.decorators.cache import cache_page
from django.conf import settings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pathlib

DEFAULT_MODEL = 'namenlijst'
SKIPS = settings.SKIPS

def get_model(model=None) -> models.LinkBase:
    if model is None:
        model = DEFAULT_MODEL
    model = 'Link%s' % model.title()
    return models.__dict__[model]


def __render(request, file, context=None):
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
    context = get_info(pid, words, extra_previews=False)
    context['model'] = model
    context['Link'] = link

    rates = []
    for link in links:
        rater = Rater(link.pid, link.nmlid, link.entity)
        rates.append(rater.ratings())
    context['links'] = links
    context['rates'] = rates

    return __render(request, 'pid.html', context=context)


def info(request, pid, nmlid, words='', model=None):
    if model is None:
        model = DEFAULT_MODEL
    words = words.split('/')
    context = get_info(pid, [words])
    context['nmlid'] = nmlid
    context['model'] = model
    context['Link'] = get_model(model)
    context['entity'] = ' '.join(words)
    obj = context['Link'].objects.filter(nmlid=nmlid, pid=pid).first()
    if obj is None:
        raise Http404("Link not found in database")

    context['status'] = obj.status
    context['kind'] = obj.kind
    context['extras'] = obj.extras
    context['url'] = obj.url
    context['score'] = obj.score

    context['link'] = obj
    rater = Rater(pid, nmlid, obj.entity)
    context['lookups'] = rater.lookups
    context['rating'] = rater.ratings()
    context['person'] = rater.details
    context['pids'] = get_all_for_pid(pid, include_self=False)
    return __render(request, 'info.html', context=context)


def progress(request, model=None):
    try:
        model = get_model(model)
    except KeyError:
        return HttpResponseNotFound('<h1>Link type "%s" not found</h1>' % model)
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


def evaluation(request, pid):
    path = 'evals/'
    files = [dir for dir in pathlib.Path(path).iterdir() if dir.is_dir()]

    file = None
    if pid is not None:
        try:
            file = next(dir_ for dir_ in files if dir_.name == pid)
        except StopIteration:
            raise Http404("Unknown pid %s" % pid)

    return __render(request, 'evaluation.html', {"files": files, "pid": pid, "file": file})


# @cache_page(60)
def stats(request, model=None, statname=None, format_=None):
    from .stats import Stats
    if format_ is None:
        format_ = 'svg'
    try:
        model = get_model(model)
    except KeyError:
        return HttpResponseNotFound('<h1>Link type "%s" not found</h1>' % model)
    obj = Stats(model)
    modelname = model.__name__[4:].lower()

    if statname is None:
        context = {
            "statname": statname,
            "model": modelname,
            "format": format_,
            "segments": (n for n in dir(obj) if n[:8] == 'segment_'),
            "highest_scores": obj._highest_scores(),
            "young_deaths": obj._young_deaths(),
            "old_deaths": obj._old_deaths(),
            "segmented_deaths": dict(),
            "most_common_names": obj._most_common_names(),
            "skipped_names": obj._skipped_names(),
            "skips": SKIPS,
        }

        segments = ('born_country', 'died_country', 'victim_type_details', 'victim_type', 'gender')
        for segment in segments:
            context['segmented_deaths'][segment] = obj._segmented_deaths(segment)

        for funcname in (n for n in dir(obj) if n[:7] == '_stats_'):
            context[funcname[1:]] = getattr(obj, funcname)()
        return __render(request, 'stats.html', context)

    if statname[0] == '_':
        return Http404("Invalid statname '%s'" % (statname,))

    if format_ not in obj.format_to_type:
        raise Http404("Unknown format '%s' requested" % (format_,))

    if not hasattr(obj, statname):
        raise Http404("Unknown statname '%s'" % (statname,))

    return obj._output(statname, format_)
