# utils.py
import uuid
import random
import string
from django.utils.text import slugify


def generate_unique_slug(model, field_value, slug_field: str = "slug"):
    """
    Generate a unique slug for a given model and field value.
    """
    base_slug = slugify(field_value)
    slug = base_slug
    counter = 1

    while model.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug



import random
import string

def generate_sku(product=None, prefix: str = "SKU"):
    """
    Generate a random SKU like SKU-FLO-1234
    If product is passed, use first 3 letters of product name as prefix.
    """
    if product:
        prefix = product.name[:3].upper()

    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}-{letters}{numbers}"
