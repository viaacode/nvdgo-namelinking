from django.shortcuts import render
from django.conf import settings

def __render(request, file, context = {}):
    return render(request, file, context=context)

def index(request):
    return __render(request, 'index.html')

def loading(request):
    return __render(request, 'index.html')

def details(request, pid, nmlid, words=''):
    from methods import get_info
    import json
    words = words.split('/')
    context = get_info(pid, words)
    context['nmlid'] = nmlid
    context['ocr'] = json.dumps([word.__dict__ for word in context['ocr']])
    return __render(request, 'details.html', context=context)

def detailframe(request, pid, nmlid, words = ''):
    return __render(request, 'detailframe.html', context={"pid": pid, "words": words, "nmlid": nmlid})
