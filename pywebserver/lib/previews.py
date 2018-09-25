from pythonmodules.mediahaven import MediaHaven
import io
import base64
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from pythonmodules.cache import WrapperCacher
from pythonmodules.mediahaven import MediaHavenException
from pythonmodules import decorators
import logging
from pythonmodules.profiling import timeit
from pythonmodules.namenlijst import Namenlijst
from pythonmodules.matcher import Matcher

logger = logging.getLogger('pythonmodules.previews')


def get_cacher(name):
    try:
        return caches[name]
    except InvalidCacheBackendError:
        return caches['default']


class Rater:
    def __init__(self, pid, nmlid):
        self.pid = pid
        self.nmlid = nmlid
        self.mh = get_media_haven()
        self._language = None
        self._alto = None
        self._details = None

    @property
    def language(self):
        if self._language is None:
            with timeit('mh.one'):
                language = self.mh.one('+(externalId:%s)' % self.pid)
                self._language = language['mdProperties']['language'][0].lower()
        return self._language

    @property
    def alto(self):
        if self._alto is None:
            with timeit('alto'):
                self._alto = self.mh.get_alto(self.pid)
        return self._alto

    @property
    def details(self):
        if self._details is None:
            with timeit('nml'):
                self._details = Namenlijst().get_person_full(self.nmlid, self.language)
        return self._details

    def ratings(self):
        language, alto, nml = self.language, self.alto, self.details

        lookups = (
            ('died_place_locality', nml.died_place['locality']),
            ('born_place_locality', nml.born_place['locality']),
            ('died_place_topo', nml.events['died']['topo']),
        )
        lookups = {k: v for k, v in lookups if len(v) > 1}

        matcher = Matcher(alto.text, nml.names.variations_normalized)
        return matcher.scores(lookups)


@decorators.log_call(logger=logger)
def get_info(pid, words=None, extra_previews=True):
    def b64img(img):
        data = io.BytesIO()
        img.save(data, format='JPEG', quality=85)
        return base64.b64encode(data.getvalue()).decode()

    mh = get_media_haven()
    result = dict(
        pid=pid,
        words=len(words) if words is not None else 0,
        alto=mh.get_alto(pid).search_words(words),
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
