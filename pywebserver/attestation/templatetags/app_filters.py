from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django import template
import re

register = template.Library()


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
