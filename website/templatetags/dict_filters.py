from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    try:
        return d.get(key, 0)
    except:
        return 0

@register.filter
def get_day_range(start, end):
    return range(start, end + 1)

@register.filter
def get_range(value):
    return range(value)

@register.filter
def min(value, max_val):
    try:
        return value if value <= int(max_val) else int(max_val)
    except:
        return value
