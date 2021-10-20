import config

if config.CACHE_ENDPOINT:
    from inc.cache_remote import Cache
else:
    from inc.cache_sqlite import Cache
