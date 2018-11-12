from pythonmodules.mediahaven import MediaHaven
import io
import base64
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from pythonmodules.cache import WrapperCacher
from pythonmodules import decorators
import logging

logger = logging.getLogger('pythonmodules.previews')


def get_cacher(name):
    try:
        return caches[name]
    except InvalidCacheBackendError:
        return caches['default']


@decorators.log_call(logger=logger)
def get_info(pid, words=None, extra_previews=True):
    def b64img(img):
        data = io.BytesIO()
        img.save(data, format='JPEG', quality=85)
        return base64.b64encode(data.getvalue()).decode()

    mh = get_media_haven()
    alto = mh.get_alto(pid)
    result = dict(
        pid=pid,
        words=len(words) if words is not None else 0,
        alto=alto.search_words(words),
        alto_link=alto.url
    )

    with mh.get_preview(pid) as im:
        result['previewImageUrl'] = im.meta['previewImagePath']
        result['meta'] = im.meta

        if result['words'] > 0 and extra_previews:
            result['preview_full'] = b64img(im.highlight_words(words, crop=False))
            result['preview'] = b64img(im.highlight_words(words))

        result['props'] = im.meta['mdProperties']

    return result


_instances = {}


def get_media_haven():
    global _instances
    if 'MediaHaven' not in _instances:
        cache = get_cacher('MediaHaven')
        mh = MediaHaven('../config.ini')
        mh.set_cacher(WrapperCacher(cache))
        _instances['MediaHaven'] = mh
    return _instances['MediaHaven']


