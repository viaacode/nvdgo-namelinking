from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django import template
import json
import re

from xml.etree import ElementTree
import datetime

register = template.Library()


def _serialize(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime.date):
        serial = obj.isoformat()
        return serial

    if isinstance(obj, datetime.time):
        serial = obj.isoformat()
        return serial

    if isinstance(obj, ElementTree.Element):
        serial = obj.attrib
        return serial

    if hasattr(obj, '__dict__'):
        return obj.__dict__

    return obj.__repr__()


@register.filter(needs_autoescape=True)
def highlight(text, word, regex=False, autoescape=True):
    if autoescape:
        text = conditional_escape(text)
        word = conditional_escape(word)

    if not regex:
        return mark_safe(text.replace(word, '<mark>%s</mark>' % word))

    return mark_safe(re.sub(word, r'<mark>\1</mark>', text))


@register.filter(needs_autoescape=True)
def highlight_words(text, words, autoescape=True):
    regex = '(%s)' % words.replace(' ', '\W*')
    return highlight(text, regex, regex=True, autoescape=autoescape)


@register.filter(name='json')
def json_(obj, autoescape=False, serializer=_serialize):
    obj = json.dumps(obj, default=serializer, indent=4)
    if autoescape:
        obj = conditional_escape(obj)
    return mark_safe(obj)


@register.filter(name='replace')
def replace_(txt: str, args: str):
    search, replace = args.split(':', 1)
    return txt.replace(search, replace)