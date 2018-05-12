from django.shortcuts import render
from .models import Link

def __render(request, file, context = {}):
    return render(request, file, context=context)

def index(request):
    return __render(request, 'index.html')

def loading(request):
    return __render(request, 'loading.html')

def info(request, pid, nmlid, words=''):
    from methods import get_info
    words = words.split('/')
    context = get_info(pid, words)
    context['nmlid'] = nmlid
    context['alto'] = context['alto'].jsonserialize()
    context['Link'] = Link
    context['entity'] = ' '.join(words)
    return __render(request, 'info.html', context=context)
