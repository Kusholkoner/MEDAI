from api_server_vercel import app

# Vercel serverless function handler
def handler(request, context):
    """Vercel serverless function handler"""
    return app(request, context)
