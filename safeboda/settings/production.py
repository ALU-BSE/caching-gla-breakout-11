import os


if os.environ.get('REDIS_CLUSTER_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_CLUSTER_URL'),
            'OPTIONS': {
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 20,
                    'retry_on_timeout': True,
                },
            }
        }
    }
