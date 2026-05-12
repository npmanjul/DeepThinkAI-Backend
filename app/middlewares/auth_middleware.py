from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from app.utils.jwt import decode_access_token


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        # Public routes
        public_routes = [
        "/",
        "/api/v1/auth/login",
        "/api/v1/auth/signup",
        "/api/v1/auth/google-auth",
        "/api/v1/auth/get-otp",
        "/api/v1/auth/verify-otp",
        "/api/v1/blog/read-blog",
        "/docs",
        "/openapi.json",
        ]

        # Skip auth
        if request.url.path in public_routes:
            return await call_next(request)

        token = request.cookies.get("access_token")

        if not token:
            return JSONResponse(
                status_code=401,
                content={"message": "Unauthorization Access"}
            )

        try:
            decoded_user = decode_access_token(token)
            print(decoded_user)

            if not decoded_user:
                return JSONResponse(
                    status_code=401,
                    content={"message": "Invalid or expired token"}
                )

            request.state.user = decoded_user

        except Exception as e:
            return JSONResponse(
                status_code=401,
                content={"message": str(e)}
            )

        response = await call_next(request)
        return response