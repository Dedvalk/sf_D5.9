from datetime import datetime
from django import template
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse


register = template.Library()


@register.simple_tag()
def current_time(format_string='%b %d %Y'):

    return datetime.now().strftime(format_string)

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):

    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    return d.urlencode()

@register.simple_tag()
def category_list(categories):

    clist = [category.name for category in categories]
    return ', '.join(clist)

@register.simple_tag(takes_context=True)
def post_url(context, **kwargs):

    d = ''
    for k, v in kwargs.items():
        print('kwarg->', k, ':', v)
        if k == 'post_id':
            d = f'newsportal/{v}'
    print(d)
    return d






