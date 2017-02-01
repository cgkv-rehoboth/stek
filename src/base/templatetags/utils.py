from django import template
import random
register = template.Library()

@register.filter('klass')
def klass(ob):
    return ob.__class__.__name__

@register.filter('get')
def get(ob, name):
    if name in ob:
        return ob[name]
    return ''

@register.filter('usernicename')
def usernicename(ob):
    if ob.first_name != "" and ob.last_name != "":
        return ob.first_name + " " + ob.last_name
    return ob.username

@register.filter('encodemail')
def encodemail(str):
    # Basic encoding script
    str = str.lower().replace('@', 'A').replace('.', 'D')
    lst = 'BCEFGHIJKLMNOPQRSTUVWXYZ'
    str = ''.join('%s%s' % (x, random.choice(lst) + (random.choice(lst) if random.random() > 0.3 else '')) for x in str)
    return str

@register.filter('encodemailURL')
def encodemailURL(str):
    # Add key for identifing type in JS
    return '5e2nabe5s4' + encodemail(str)

@register.filter('encodemailHref')
def encodemailHref(str):
    # Will only decode the string for the href attribute. Text of the <a> won't be changed
    # Add key for identifing type in JS
    return 'p1ec2fx1uz' + encodemail(str)

@register.filter('encodemailPlain')
def encodemailPlain(str):
    # Returns a plain string
    # Add key for identifing type in JS
    return 'zs39qpz9ti' + encodemail(str)

@register.filter('isobject')
def isobject(ob, str):
    return hasattr(ob, str.lower())
