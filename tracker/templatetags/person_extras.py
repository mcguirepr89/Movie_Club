from django import template
from ..models import Person

register = template.Library()

@register.filter
def get_person_name(person_id):
    try:
        return Person.objects.get(pk=person_id).name
    except Person.DoesNotExist:
        return ""
