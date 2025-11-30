# Vercel Python serverless entry: expose FastAPI app
from app.main import app
print("Welcome to Exateks API - Empowering Small Businesses")

# Vercel expects a module-level variable named `app`
# FastAPI ASGI app is imported from app.main