from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class PathBasedCORSMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, path_cors_config):
        super().__init__(app)
        self.path_cors_config = path_cors_config

    def _origin_is_allowed(self, origin: str, allowed_origins: list) -> bool:
        for pattern in allowed_origins:
            if origin is not None and (pattern == "*" or pattern == origin):
                return True
        return False

    def _method_is_allowed(self, method: str, allowed_methods: str) -> bool:
        return method in allowed_methods.split(',')

    def _headers_are_allowed(self, request_headers: str, allowed_headers: str) -> bool:
        if allowed_headers == "*":
            return True
        request_headers_set = {header.strip().lower() for header in request_headers.split(',')}
        allowed_headers_set = {header.strip().lower() for header in allowed_headers.split(',')}
        return request_headers_set.issubset(allowed_headers_set)

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        method = request.method
        request_method = request.headers.get("Access-Control-Request-Method")
        request_headers = request.headers.get("Access-Control-Request-Headers")

        for path, cors_config in self.path_cors_config.items():
            if request.url.path.startswith(path):
                allowed_origins = cors_config.get("Access-Control-Allow-Origin", [])
                allowed_methods = cors_config.get("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
                allowed_headers = cors_config.get("Access-Control-Allow-Headers", "*")

                if self._origin_is_allowed(origin, allowed_origins):
                    if method == "OPTIONS":
                        # Check if the requested method and headers are allowed
                        if (request_method and not self._method_is_allowed(request_method, allowed_methods)) or \
                                (request_headers and not self._headers_are_allowed(request_headers, allowed_headers)):
                            return JSONResponse(status_code=403, content="CORS preflight request failed")

                        # Respond to preflight request
                        headers = {
                            "Access-Control-Allow-Origin": origin,
                            "Access-Control-Allow-Methods": allowed_methods,
                            "Access-Control-Allow-Headers": allowed_headers,
                            "Access-Control-Allow-Credentials": str(
                                cors_config.get("Access-Control-Allow-Credentials", True)).lower(),
                            "Access-Control-Expose-Headers": cors_config.get("Access-Control-Expose-Headers", ""),
                        }
                        return JSONResponse(status_code=200, headers=headers, content=None)

                    # For non-OPTIONS requests, add CORS headers to the response
                    response = await call_next(request)
                    response.headers.update({
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Credentials": str(cors_config.get("allow_credentials", True)).lower(),
                        "Access-Control-Expose-Headers": cors_config.get("expose_headers", ""),
                    })
                    return response

        # Fallback if no matching path found
        return await call_next(request)
