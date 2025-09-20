from django.shortcuts import render
from rest_framework import viewsets

from safeboda.cache_debug import cache_performance
from users.models import User
from users.serializers import UserSerializer

from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def cache_stats(request):
    try:
        client = cache.client.get_client(write=True)  # Get Redis client
        keys = [key.decode('utf-8') for key in client.keys('*')]
        total_keys = len(keys)

        # Optional: cache hit/miss ratio
        info = client.info('stats')
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        hit_ratio = hits / (hits + misses) if (hits + misses) > 0 else None

    except Exception as e:
        keys = ["Not supported by this cache backend."]
        total_keys = 0
        hit_ratio = None

    return Response({
        'cache_keys': keys,
        'total_keys': total_keys,
        'hit_ratio': hit_ratio
    })


def get_cache_key(prefix, identifier=None):
    """Generate consistent cache keys"""
    if identifier:
        return f"{prefix}_{identifier}"
    return prefix


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @cache_performance("user_list_cache")
    def list(self, request, *args, **kwargs):
        cache_key = get_cache_key('users_list')
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60)
        return response

    @cache_performance("user_list_cache")
    def retrieve(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        cache_key = get_cache_key("user", user_id)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60)
        return response

    def perform_create(self, serializer):
        cache.delete('users_list')
        super().perform_create(serializer)

    def perform_update(self, serializer):
        user_id = serializer.instance.id
        cache.delete('users_list')
        cache.delete(f'user_{user_id}')
        super().perform_update(serializer)

        # Write-through: immediately update cache
        user_data = self.get_serializer(serializer.instance).data
        cache_key = f"user_{serializer.instance.id}"
        cache.set(cache_key, user_data, timeout=settings.CACHE_TTL)

    def perform_destroy(self, instance):
        user_id = instance.id
        cache.delete('users_list')
        cache.delete(f'user_{user_id}')
        super().perform_destroy(instance)
