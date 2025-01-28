from typing import Optional
from django.core.cache.backends.base import (
    DEFAULT_TIMEOUT,
    BaseCache,
)
from django.utils.functional import cached_property
from .utils import reverse_key


class BaseCupidDBDjangoCache(BaseCache):
    '''
    Implements the necessary functions to extend Django's BaseCache class
    '''

    def __init__(self, server, params, library):
        super().__init__(params)
        self._servers = server

        self._lib = library
        self._class = library.CupidClient
        self._options = params.get('OPTIONS') or {}

    @property
    def client_servers(self):
        return self._servers

    @cached_property
    def _cache(self):
        host, port = self.client_servers.split(':')
        return self._class(host, port, **self._options)

    def get_backend_timeout(self, timeout=DEFAULT_TIMEOUT):
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout
        return 0 if timeout is None else max(0, int(timeout))

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_and_validate_key(key, version=version)
        if timeout is not None and timeout != DEFAULT_TIMEOUT:
            if int(timeout) == 0:
                self._cache.delete(key)
                return
        self._cache.set(key, value, self.get_backend_timeout(timeout))

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_and_validate_key(key, version=version)
        if timeout is not None and timeout != DEFAULT_TIMEOUT:
            if int(timeout) == 0:
                return not self._cache.delete(key)
        return self._cache.add(key, value, self.get_backend_timeout(timeout))

    def touch(self, key, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_and_validate_key(key, version=version)
        if timeout is not None and timeout != DEFAULT_TIMEOUT:
            if int(timeout) == 0:
                return self._cache.delete(key)
        return bool(self._cache.touch(key, self.get_backend_timeout(timeout)))

    def get(self, key, default=None, version=None):
        key = self.make_and_validate_key(key, version=version)
        return self._cache.get(key, default)

    def delete(self, key, version=None):
        key = self.make_and_validate_key(key, version=version)
        return bool(self._cache.delete(key))

    def has_key(self, key, version=None):
        key = self.make_and_validate_key(key, version=version)
        return self._cache.has_key(key)

    def incr(self, key, delta=1, version=None):
        key = self.make_and_validate_key(key, version=version)
        if not self._cache.has_key(key):
            raise ValueError(f"Key '{key}' not found.")
        return self._cache.incr(key, delta)

    def delete_many(self, keys, version=None):
        keys = [self.make_and_validate_key(key, version=version) for key in keys]
        self._cache.delete_many(keys)

    def clear(self):
        self._cache.flush()

    def close(self, **kwargs):
        pass


class BaseCupidDBCache(BaseCupidDBDjangoCache):
    '''
    Implements additional functionality supported by CupidDB
    '''

    def get_dataframe(self, key, version=None, **kwargs):
        key = self.make_and_validate_key(key, version=version)
        return self._cache._get_dataframe(key=key, **kwargs)

    def ttl(self, key: str, version=None) -> float:
        key = self.make_and_validate_key(key, version=version)
        ttl = self._cache.ttl(key)
        if ttl is None:
            return 0.0
        else:
            return ttl

    def keys(self, pattern: Optional[str] = None, version: Optional[int] = None) -> list[str]:
        if pattern is None:
            pattern = '*'
        new_pattern = self.make_and_validate_key(pattern, version=version)
        return [
            reverse_key(key)
            for key in self._cache.keys(new_pattern)
        ]


class CupidDBCache(BaseCupidDBCache):

    def __init__(self, server, params):
        import pycupiddb

        super().__init__(server=server, params=params, library=pycupiddb)
