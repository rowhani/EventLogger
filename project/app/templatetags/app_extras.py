#! /usr/bin/env python2.7

from django import template

register = template.Library()

@register.filter
def public(items):
    return items.filter(status='public')