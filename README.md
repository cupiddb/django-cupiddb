# Django CupidDB Cache Backend
Django CupidDB Cache is a high-performance caching backend that leverages CupidDB, an in-memory database optimized for speed and efficiency. It supports caching dataframes, dictionaries, lists, and any other data types with low latency and high throughput. Built on Apache Arrow, it ensures fast serialization and retrieval, making it a great choice for any application that needs caching. Give it a try! 🚀

## Why Django CupidDB Cache Backend
- Caching DataFrame has higher performance
- Cached DataFrame can be filtered and select column, reducing bandwidth and memory usage
- Additional `get_dataframe`, `keys`, and `ttl`  commands in addition to the commands in the default backend
- Fully tested with Django's cache test suite

## Installation
Install with pip
```bash
pip install django-cupiddb
```

## Configuration
To start using django-cupiddb, change your Django cache settings to the following example
```python
CACHES = {
    'default': {
        'BACKEND': 'django_cupiddb.cache.CupidDBCache',
        'LOCATION': 'localhost:5995',
        'TIMEOUT': 300,
    },
}
```

## Supports all types of data
Just like all other Django cache backends, CupidDB can handle any type of data that needs to be cached. All views and templates will continue to work as expected.
``` python
>>> from django.core.cache import cache
>>> cache.set(key='dict', value={'key': 'value'})
>>> cache.get(key='dict')
{'key': 'value'}
```

## Additional Commands
In addition to the standard cache client methods provided by Django, django-cupiddb also implements the following methods.

### Get DataFrame
``` python
>>> from django.core.cache import cache
>>> import pandas as pd
>>> from pycupiddb import RowFilter

>>> df = pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': [6, 7, 8, 9, 10],
    })

>>> cache.set(key='df_cache', value=df)

>>> cache.get(key='df_cache')
   col1  col2
0     1     6
1     2     7
2     3     8
3     4     9
4     5    10

>>> filters = [
        RowFilter(column='col2', logic='gte', value=9, data_type='int'),
    ]
>>> cache.get_dataframe(key='df_cache', columns=['col1'], filters=filters)
   col1
0     4
1     5
```

### Key List
``` python
>>> cache.keys()
['df_cache', 'dict']
```

### TTL
``` python
>>> cache.ttl(key='df_cache')
289.729

# Note: In CupidDB, ttl of 0.0 means the data will persist forever
```
Warning: Django's cache TIMEOUT settings defaults to 300 seconds and CupidDB backend respects the settings. If you wish to persist your data for longer, you may set the TIMEOUT settings to a larger value or None.
Visit [Django settings](https://docs.djangoproject.com/en/dev/ref/settings/#timeout) for more details.
