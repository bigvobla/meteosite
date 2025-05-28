from django import template

register = template.Library()

@register.simple_tag
def cloud_icon(cloudiness):
    try:
        cloudiness = float(cloudiness)
    except (TypeError, ValueError):
        return 'main/img/unknown.png'

    if cloudiness < 20:
        return 'main/img/sunny.png'
    elif cloudiness < 50:
        return 'main/img/partly_cloudy.png'
    elif cloudiness < 80:
        return 'main/img/cloudy.png'
    else:
        return 'main/img/very-cloudy.png'

