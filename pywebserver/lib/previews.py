from pythonmodules.mediahaven import MediaHaven
import io
import base64
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from pythonmodules.cache import WrapperCacher
from pythonmodules.mediahaven import MediaHavenException
from pythonmodules import decorators
import logging


def get_cacher(name):
    try:
        return caches[name]
    except InvalidCacheBackendError:
        return caches['default']


@decorators.log_call(logger=logging.getLogger('pythonmodules'))
def get_info(pid, words=None, extra_previews=True):
    def b64img(img):
        data = io.BytesIO()
        img.save(data, format='JPEG', quality=85)
        return base64.b64encode(data.getvalue()).decode()

    cache = get_cacher('MediaHaven')
    mh = MediaHaven('../config.ini')
    mh.set_cacher(WrapperCacher(cache))
    result = {
        "pid": pid,
        "words": len(words) if words is not None else 0,
        "alto": None,
    }

    with mh.get_preview(pid) as im:
        result['previewImageUrl'] = im.meta['previewImagePath']
        result['meta'] = im.meta
        result['alto'] = im.get_words(words)

        if result['words'] > 0 and extra_previews:
            result['preview_full'] = b64img(im.highlight_words(words, crop=False))
            result['preview'] = b64img(im.highlight_words(words))

        result['props'] = {item['attribute']: item['value'] for item in im.meta['mdProperties']}

    return result

