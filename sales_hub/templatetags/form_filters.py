from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    """
    Add CSS class(es) to a form field.
    Usage: {{ field|add_class:"my-class another-class" }}
    """
    return field.as_widget(attrs={'class': css})
