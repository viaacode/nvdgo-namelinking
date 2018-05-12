from pythonmodules.mediahaven import MediaHaven
import io
import base64
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError


def get_cache(name):
    try:
        return caches[name]
    except InvalidCacheBackendError:
        return caches['default']


def get_info(pid, words = []):
    def b64img(im):
        data = io.BytesIO()
        im.save(data, format='JPEG')
        return base64.b64encode(data.getvalue()).decode()

    cache = get_cache('MediaHaven')
    mh = MediaHaven('../config.ini')
    mh.set_cache(cache)
    result = {
        "pid": pid,
        "words": len(words),
    }

    im = mh.get_preview(pid).open()
    result['previewImageUrl'] = im.meta['previewImagePath']
    result['meta'] = im.meta
    result['alto'] = im.get_words(words)
    
    if len(words):
        result['preview_full'] = b64img(im.highlight_words(words, crop = False))
        result['preview'] = b64img(im.highlight_words(words))

    # result['preview_confidence_full'] = b64img(im.highlight_confidence())

    im.close()
    result['props'] = {item['attribute']: item['value'] for item in im.meta['mdProperties']}
    return result
