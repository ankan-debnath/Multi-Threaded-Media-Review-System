import redis
from rich.console import  Console
console = Console()

def get_redis_client():
    redis_client = redis.StrictRedis(host="localhost", port="6379", db=0, decode_responses=True)
    return redis_client

def is_redis_available(client):
    try:
        redis_available = client.ping()
    except redis.ConnectionError:
        redis_available = False
        console.print(f"[yellow]Warning : [/yellow] Redis Cache not available. Data will be only fetched from DB : ")
    return redis_available