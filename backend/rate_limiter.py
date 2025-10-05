import time
from typing import Dict
import redis
import os

class RateLimiter:
    def __init__(self):
        # Use Redis if available, otherwise use in-memory storage
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
            self.use_redis = True
        else:
            self.redis_client = None
            self.use_redis = False
            self.requests: Dict[str, list] = {}
        
        self.rate_limit = 60  # 60 requests per minute
        self.window_size = 60  # 1 minute window
    
    def is_allowed(self, user_id: str) -> bool:
        """Check if user is within rate limit"""
        current_time = time.time()
        
        if self.use_redis:
            return self._check_redis_rate_limit(user_id, current_time)
        else:
            return self._check_memory_rate_limit(user_id, current_time)
    
    def _check_redis_rate_limit(self, user_id: str, current_time: float) -> bool:
        """Check rate limit using Redis"""
        key = f"rate_limit:{user_id}"
        
        # Remove old entries
        self.redis_client.zremrangebyscore(key, 0, current_time - self.window_size)
        
        # Count current requests
        current_requests = self.redis_client.zcard(key)
        
        if current_requests >= self.rate_limit:
            return False
        
        # Add current request
        self.redis_client.zadd(key, {str(current_time): current_time})
        self.redis_client.expire(key, self.window_size)
        
        return True
    
    def _check_memory_rate_limit(self, user_id: str, current_time: float) -> bool:
        """Check rate limit using in-memory storage"""
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old requests outside the window
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if current_time - req_time < self.window_size
        ]
        
        # Check if under rate limit
        if len(self.requests[user_id]) >= self.rate_limit:
            return False
        
        # Add current request
        self.requests[user_id].append(current_time)
        return True
