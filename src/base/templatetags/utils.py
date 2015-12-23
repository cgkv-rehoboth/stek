from django import template
register = template.Library()

@register.filter('klass')
def klass(ob):
    return ob.__class__.__name__

@register.filter('usernicename')
def usernicename(ob):
    if ob.first_name != "" and ob.last_name != "":
        return ob.first_name + " " + ob.last_name
    return ob.username

