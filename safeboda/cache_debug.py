import time
import functools
import logging
import time
# import requests

logger = logging.getLogger(__name__)


def cache_performance(cache_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()

            logger.info(f"{cache_name}: {end_time - start_time:.4f}s")
            return result
        return wrapper
    return decorator


def test_cache_performance():
    url = "http://localhost:8000/api/users/"

    # First call (cache miss)
    start = time.time()
    response1 = requests.get(url)
    time1 = time.time() - start

    # Second call (cache hit)
    start = time.time()
    response2 = requests.get(url)
    time2 = time.time() - start

    print(f"First call: {time1:.4f}s")
    print(f"Second call: {time2:.4f}s")
    print(f"Speedup: {time1/time2:.2f}x")


if __name__ == "__main__":
    test_cache_performance()
