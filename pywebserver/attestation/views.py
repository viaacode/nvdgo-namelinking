from django.shortcuts import render
from django.conf import settings

def __render(request, file, context = {}):
    return render(request, file, context=context)

def index(request):
    return __render(request, 'index.html')

def loading(request):
    return __render(request, 'loading.html')

def details(request, pid, nmlid, words=''):
    from methods import get_info
    words = words.split('/')
    context = get_info(pid, words)
    context['nmlid'] = nmlid
    context['alto'] = context['alto'].jsonserialize()
    return __render(request, 'details.html', context=context)

def detailframe(request, pid, nmlid, words = ''):
    return __render(request, 'detailframe.html', context={"pid": pid, "words": words, "nmlid": nmlid})
