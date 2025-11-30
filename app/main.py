"""
Exa Backend - FastAPI Application
Clean slate for building features from scratch.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import settings
from app.routers import email_router

# Initialize FastAPI app (disable docs)
app = FastAPI(
    title=settings.APP_NAME,
    description="Exa Backend API",
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_frontend_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(email_router.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """Custom welcome page."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Exa Backend API</title>
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
            <h1>🚀 Exa Backend</h1>
            <div class="status">✓ API Running</div>
            <p>Email Service API - Ready to send emails with templates</p>
            
            <div class="endpoints">
                <h3>Available Endpoints</h3>
                <div class="endpoint">
                    <span class="method">GET</span> /api/email/check
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> /api/email/send
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> /api/email/send-template
                </div>
            </div>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
