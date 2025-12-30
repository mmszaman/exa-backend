from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api.v1 import auth, email
from app.webhooks import router
from app.core.rate_limit import limiter

# Initialize FastAPI app (disable docs)
# Docs are disabled for security; use API clients like Postman or curl
app = FastAPI(
    title=settings.APP_NAME,
    description="SMBHub API v1",
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


# Add rate limiter to app state
# This allows access to the limiter in route handlers and middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Setup CORS middleware (MUST be before routers)
# Allows frontend to access API from different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_frontend_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API & webhook routers
# Each router handles a specific set of endpoints
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(email.router, prefix="/api/v1/email", tags=["email"])
app.include_router(router, prefix="/webhooks", tags=["webhooks"])

# Custom root endpoint
# Render a welcome page with API status
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """Custom welcome page."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ExateksAPI</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #fff;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                max-width: 600px;
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 20px;
                font-weight: 600;
            }
            p {
                font-size: 1.2rem;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            .status {
                display: inline-block;
                padding: 10px 20px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50px;
                font-size: 0.9rem;
                margin-bottom: 30px;
            }
            .endpoints {
                background: rgba(0, 0, 0, 0.2);
                padding: 20px;
                border-radius: 10px;
                text-align: left;
                margin-top: 30px;
            }
            .endpoints h3 {
                margin-bottom: 15px;
                font-size: 1.2rem;
            }
            .endpoint {
                margin: 10px 0;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
                opacity: 0.9;
            }
            .method {
                display: inline-block;
                padding: 2px 8px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                margin-right: 10px;
                font-size: 0.8rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ExateksAPI</h1>
            <div class="status">✓ API Running</div>
            <p>Please contact <strong><i>support@exateks.com</i></strong> for assistance.</p>
        </div>
    </body>
    </html>
    """


# Run the application
# This block is only executed when running this file directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
