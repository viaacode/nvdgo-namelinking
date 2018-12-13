from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django import template
import json
import re
from collections import OrderedDict, namedtuple

from xml.etree import ElementTree
import datetime
import logging

logger = logging.getLogger('pythonmodules.previews')

register = template.Library()


def _serialize_new(obj):
    """JSON serializer for objects not serializable by default json code"""
    if obj is None:
        return obj

    if type(obj) in [str, int, float, bool]:
        return obj

    if type(obj) is set:
        obj = list(obj)

    if isinstance(obj, (datetime.time, datetime.date)):
        return obj.isoformat()

    if hasattr(obj, '_asdict'):
        obj = obj._asdict()

    if isinstance(obj, ElementTree.Element):
        return _serialize(obj.attrib)

    if isinstance(obj, dict):
        # return obj
        return OrderedDict([(k, _serialize(v)) for k, v in obj.items()])

    # try:
    #     obj = dict(obj)
    # except TypeError:
    #     print('typerr')
    #     pass
    # except ValueError:
    #     print('valerr')
    #     pass

    if hasattr(obj, '__iter__'):
        return list(map(_serialize, obj))

    return obj


def _serialize(obj):
    """JSON serializer for objects not serializable by default json code"""
    if obj is None:
        return obj

    if type(obj) in [str, int, float, bool]:
        return obj

    if type(obj) is set:
        obj = list(obj)

    if isinstance(obj, datetime.date):
        serial = obj.isoformat()
        return serial

    if isinstance(obj, datetime.time):
        serial = obj.isoformat()
        return serial

    if isinstance(obj, ElementTree.Element):
        return _serialize(obj.attrib)

    if hasattr(obj, '_asdict'):
        obj = obj._asdict()

    if isinstance(obj, (OrderedDict, dict)):
        # return obj
        return OrderedDict([(k, _serialize(v)) for k, v in obj.items()])

    try:
        obj = dict(obj)
    except TypeError:
        pass
    except ValueError:
        pass

    if hasattr(obj, '__iter__'):
        return list(map(_serialize, obj))

    return obj.__str__()


@register.filter(needs_autoescape=True)
def highlight(text, word, regex=False, autoescape=True, case_insensitive=True):
    if autoescape:
        text = conditional_escape(text)
        word = conditional_escape(word)

    if not case_insensitive:
        if not regex:
            logger.info('noregex word = %s ', word)
            return mark_safe(text.replace(word, '<mark>%s</mark>' % word))

    if not regex:
        word = re.escape(word)

    logger.info("word = %s ", word)
    return mark_safe(re.sub(word, r'<mark>\1</mark>', text, flags=re.IGNORECASE if case_insensitive else None))


@register.filter(needs_autoescape=True)
def highlight_words(text, words, autoescape=True, case_insensitive=True):
    regex = '(%s)' % words.replace(' ', '\W*')
    return highlight(text, regex, regex=True, autoescape=autoescape, case_insensitive=case_insensitive)


@register.filter(name='json')
def json_(obj, autoescape=False, serializer=_serialize):
    try:
        obj = serializer(obj)
    except TypeError as e:
        logger.warning(e)
        pass
    obj = json.dumps(obj, default=serializer, indent=4, sort_keys=True)
    if autoescape:
        obj = conditional_escape(obj)
    return mark_safe(obj)


@register.filter(name='replace')
def replace_(txt: str, args: str):
    search, replace = args.split(':', 1)
    return str(txt).replace(search, replace)


@register.filter(name='pct')
def pct(txt: float):
    return '%3.1f%%' % (txt * 100)


@register.filter(name='times')
def times(txt: str, amount: float):
    return str(txt*amount)


@register.filter(name='lookup')
def lookup(obj: dict, key: str):
    return obj[key]


@register.filter(name='lookupprop')
def lookupprop(obj: dict, key: str):
    return getattr(obj, key)
