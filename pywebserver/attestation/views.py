from django.shortcuts import render
from .models import Link
from django.db.models import Count
from methods import get_info
from django.http.response import HttpResponse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO


def __render(request, file, context = {}):
    return render(request, file, context=context)


def index(request):
    return __render(request, 'index.html')


def loading(request):
    return __render(request, 'loading.html')


def info(request, pid, nmlid, words=''):
    words = words.split('/')
    context = get_info(pid, words)
    context['nmlid'] = nmlid
    context['alto'] = context['alto'].jsonserialize()
    context['Link'] = Link
    context['entity'] = ' '.join(words)
    return __render(request, 'info.html', context=context)


def progress(request):
    data = Link.objects.all().values('status').annotate(total=Count('status'))
    notdone_count = [p['total'] for p in data if p['status'] == 0][0]
    data = [p for p in data if p['status'] != 0]
    data = {
        "status": [[l[1] for l in Link.STATUS_CHOICES if l[0] == p['status']][0] for p in data],
        "count": [p['total'] for p in data]
    }

    fig = plt.figure(figsize=(5, 8))
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(data['status'], data['count'], label='amount')
    ax.set_title('Attestation counts (%d not yet done)' % notdone_count)
    ax.legend()

    io = BytesIO()
    fig.savefig(io, format='png')
    return HttpResponse(io.getvalue(), content_type="image/png")