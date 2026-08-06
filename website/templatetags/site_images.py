from django import template

from website.models import SiteImage

register = template.Library()


@register.simple_tag
def site_image(key):
    """Look up an admin-uploaded SiteImage by its key.

    Usage:
        {% load site_images %}
        {% site_image "services-shopify-showcase-1" as img %}
        {% if img %}<img src="{{ img.image.url }}" alt="{{ img.alt_text }}">{% endif %}

    Returns None if no image has been uploaded for that key yet, so callers can
    fall back to a default or simply skip rendering.
    """
    return SiteImage.objects.filter(key=key).first()
