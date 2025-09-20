from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from safeboda.cache_debug import cache_performance
from users.models import User


def get_cache_key(prefix, identifier=None):
    """Generate consistent cache keys"""
    if identifier:
        return f"{prefix}_{identifier}"
    return prefix


@receiver(post_save, sender=User)
def invalidate_user_cache(sender, instance, **kwargs):
    # What caches should be cleared?
    cache.delete(get_cache_key("users_list"))
    cache.delete(get_cache_key("user", instance.id))
    pass


@receiver(post_delete, sender=User)
def invalidate_user_cache_on_delete(sender, instance, **kwargs):
    # What caches should be cleared?
    cache.delete(get_cache_key("users_list"))
    cache.delete(get_cache_key("user", instance.id))
    pass

