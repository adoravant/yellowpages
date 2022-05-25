from django import template

register = template.Library()

@register.filter(name="cut")
def https_to_http(value):
    return value.replace("https", "http", 1)

@register.filter(name="site_strip")
def site_strip(value):
    value = value[96:]
    value = value.replace('%2F', "").replace("F", "")
    return value