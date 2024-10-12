import json
import os
import time
from functools import wraps

def jsonfilecache(seconds):
    """
    A decorator that caches the result of the decorated function in a JSON file.

    Args:
        seconds (int): The number of seconds the cache is valid for.
    Returns:
        function: The decorated function with caching behavior.
    """
    def cache_decorator(func):
        """
        Inner decorator function that handles caching logic.

        Args:
            func (function): The function to be decorated.
        Returns:
            function: The wrapped function with caching.
        """
        cache_file = f"{func.__name__}.cache.json"

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that checks cache and updates it if necessary.

            Args:
                *args: Positional arguments for the decorated function.
                **kwargs: Keyword arguments for the decorated function.
            Returns:
                The result of the decorated function, either from cache or computed.
            """
            current_time = time.time()
            cache_data = {}

            # Load cache if it exists
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    try:
                        cache_data = json.load(f)
                    except json.JSONDecodeError:
                        cache_data = {}

            # Check if cache is still valid
            if (
                'timestamp' in cache_data and
                current_time - cache_data['timestamp'] < seconds
            ):
                # Return cached result if valid
                return cache_data['result']

            # Call the function and store result in cache
            result = func(*args, **kwargs)
            cache_data = {
                'timestamp': current_time,
                'result': result
            }
            # Write updated cache to file
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)

            return result

        return wrapper

    return cache_decorator