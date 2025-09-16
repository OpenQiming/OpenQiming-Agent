import redis
from redis.connection import Connection, SSLConnection
from redis.asyncio.connection import Connection as AsyncConnection, SSLConnection as AsyncSSLConnection

redis_client = redis.Redis()
async_redis_client = redis.asyncio.Redis()


def init_app(app):
    connection_class = Connection
    if app.config.get('REDIS_USE_SSL'):
        connection_class = SSLConnection

    redis_client.connection_pool = redis.ConnectionPool(**{
        'host': app.config.get('REDIS_HOST'),
        'port': app.config.get('REDIS_PORT'),
        'username': app.config.get('REDIS_USERNAME'),
        'password': app.config.get('REDIS_PASSWORD'),
        'db': app.config.get('REDIS_DB'),
        'encoding': 'utf-8',
        'encoding_errors': 'strict',
        'decode_responses': False
    }, connection_class=connection_class)

    app.extensions['redis'] = redis_client


def init_fastapi(fastapi_app):
    connection_class = AsyncConnection
    if fastapi_app.state.config.get('REDIS_USE_SSL'):
        connection_class = AsyncSSLConnection

    async_redis_client.connection_pool = redis.asyncio.ConnectionPool(**{
        'host': fastapi_app.state.config.get('REDIS_HOST'),
        'port': fastapi_app.state.config.get('REDIS_PORT'),
        'username': fastapi_app.state.config.get('REDIS_USERNAME'),
        'password': fastapi_app.state.config.get('REDIS_PASSWORD'),
        'db': fastapi_app.state.config.get('REDIS_DB'),
        'encoding': 'utf-8',
        'encoding_errors': 'strict',
        'decode_responses': False
    }, connection_class=connection_class)
