from fastapi import FastAPI, Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from redis import Redis
from typing import Optional, Callable, Dict, List, Tuple
import hashlib
from jose import JWTError
from foodfusionai.database import auth
from foodfusionai.utils import project_config
from foodfusionai.CONFIG import get_config, SUBSCRIPTION_TYPES
config = get_config()

def get_user_identifier(request: Request) -> str:
    """
    Get user identifier by JWT or IP address.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        return hashlib.md5(token.encode()).hexdigest()

    # fallback
    return request.client.host if request.client else "unknown"

def get_user_type(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            decoded_token = auth.decode_access_token(token)
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        subscription_type = decoded_token.get("subscription_type")
        return subscription_type
    else:  # default subscription type
        return SUBSCRIPTION_TYPES[0]

class RateLimitRule:
    def __init__(
            self,
            path_pattern: str,
            user_types: Dict[str, Dict[str, int]] # {"role": {"limit": limit_in_s, "period": period_in_s, "block": block_in_s}
    ):

        self.path_pattern = path_pattern
        self.user_types = user_types

    def matches_path(self, path: str) -> bool:
        """Retrieve the request path to apply rules to different routes"""
        if self.path_pattern == "*":
            return True

        parts = self.path_pattern.split("*")

        if len(parts) == 1:
            return path == self.path_pattern

        if not path.startswith(parts[0]):
            return False

        current_pos = len(parts[0])
        for i in range(1, len(parts)):
            part = parts[i]
            if not part:  # empty string (trailing asterisk)
                continue
            pos = path.find(part, current_pos)
            if pos == -1:
                return False
            current_pos = pos + len(part)

        return True

    def get_limits_for_user_type(self, user_type: str) -> Dict[str, int]:
        return self.user_types[user_type]


class RedisRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app: FastAPI,
            rate_limit_rules: List[RateLimitRule],
            default_rule: RateLimitRule,
            identifier_func: Optional[Callable[[Request], str]] = get_user_identifier,
            user_type_func: Optional[Callable[[Request], str]] = get_user_type,
            whitelist: Optional[list] = None,
            prefix: str = "",
    ):
        super().__init__(app)
        self.redis = Redis(
            host=config.redis_host,
            port=config.redis_port,
            password=config.redis_password,
            ssl=True
        )
        self.rate_limit_rules = rate_limit_rules
        self.default_rule = default_rule
        self.identifier_func = identifier_func
        self.user_type_func = user_type_func
        self.whitelist = whitelist or []
        self.prefix = prefix

    def get_applicable_rule(self, path: str) -> RateLimitRule:
        for rule in self.rate_limit_rules:
            if rule.matches_path(path):
                return rule

        # fallback
        return self.default_rule

    async def dispatch(self, request: Request, call_next: Callable) -> Response:

        identifier = self.identifier_func(request)

        if identifier in self.whitelist:  # has ultimate access rights
            return await call_next(request)

        user_type = self.user_type_func(request)

        # request path
        path = request.url.path

        rule = self.get_applicable_rule(path)

        limits = rule.get_limits_for_user_type(user_type)
        rate_limit_num = limits.get("limit")
        rate_limit_period = limits.get("period")
        block_duration = limits.get("block")

        # block_duration 0 --> user not blocked, execute actual endpoint
        if block_duration == 0:
            return await call_next(request)  # executes endpoint

        count_key = f"{self.prefix}{path}:{user_type}:{identifier}"
        block_key = f"{self.prefix}blocked:{path}:{user_type}:{identifier}"

        # check if the client is blocked
        if self.redis.exists(block_key):
            ttl = self.redis.ttl(block_key)
            return Response(
                content=f"Rate limit exceeded. Try again in {ttl} seconds.",
                status_code=429,
                headers={"Retry-After": str(ttl)}
            )

        # increment counter
        pipeline = self.redis.pipeline()
        pipeline.incr(count_key)
        pipeline.expire(count_key, rate_limit_period)
        result = pipeline.execute()

        current_count = result[0]

        headers = {
            "X-RateLimit-Limit": str(rate_limit_num),
            "X-RateLimit-Remaining": str(max(0, rate_limit_num - current_count)),
            "X-RateLimit-Reset": str(self.redis.ttl(count_key)),
            "X-RateLimit-UserType": user_type
        }

        if current_count > rate_limit_num:
            # block user for block_duration
            self.redis.setex(block_key, block_duration, 1)

            # reset
            self.redis.delete(count_key)

            return Response(
                content=f"Rate limit exceeded for {user_type} user. Try again later.",
                status_code=429,
                headers={**headers, "Retry-After": str(block_duration)}
            )

        # execute actual endpoint
        response = await call_next(request)

        # add headers
        for key, value in headers.items():
            response.headers[key] = value

        return response


def get_rate_limit_rules() -> Tuple[List[RateLimitRule], RateLimitRule]:
    api_version = project_config['api']['version']

    rules = [
        # same limits to prevent brute force attacks
        RateLimitRule(
            f"/{api_version}/users/auth/*",
            {
                "standard": {"limit": 5, "period": 60, "block": 300},
                "premium": {"limit": 5, "period": 60, "block": 300}
            }
        ),
        RateLimitRule(
            f"/{api_version}/users/create_user",
            {
                "standard": {"limit": 1, "period": 60, "block": 1000},
                "premium": {"limit": 1, "period": 60, "block": 1000}
            }
        ),

        # allow premium users more LLM usage
        # requests per day (86400s)
        RateLimitRule(
            f"/{api_version}/llm/*",
            {
                "standard": {"limit": 60, "period": 86400, "block": 86400},
                "premium": {"limit": 250, "period": 86400, "block": 86400}
            }
        )
    ]

    # default
    default_rule = RateLimitRule(
        "*",
        {
            "standard": {"limit": 10, "period": 60, "block": 300},
            "premium": {"limit": 10, "period": 60, "block": 300}
        }
    )

    return rules, default_rule