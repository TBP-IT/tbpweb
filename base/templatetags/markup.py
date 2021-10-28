import markdown as py_markdown

from django import template
from django.template.defaultfilters import stringfilter
try:
    from django.utils.encoding import force_unicode  # Django in Python 2
except ImportError:
    from django.utils.encoding import force_text as force_unicode  # Django in Python 3
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def markdown(value):
    """Mimics the Django <=1.4 "markdown" template tag.

    Uses python markdown (http://pythonhosted.org/Markdown/index.html) to
    support markdown syntax
    (http://daringfireball.net/projects/markdown/syntax).

    Usage:
    {% load markup %}
    {{ markdown_content_var|markdown }}
    """
    return mark_safe(py_markdown.markdown(
        value,
        safe_mode='remove',
        enable_attributes=False))
