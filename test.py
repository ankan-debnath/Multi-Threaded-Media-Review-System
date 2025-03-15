import redis

try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    if redis_client.ping():
        print("✅ Redis connection is working!")
except redis.ConnectionError:
    print("❌ Could not connect to Redis. Make sure it's running.")
