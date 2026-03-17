# Vercel Python API Entry Point
from api.app import app

app.debug = False

def handler(request, context=None):
    """Vercel serverless function handler"""
    from werkzeug.wrappers import Response

    response = app(request.environ, lambda status, headers: (status, headers))
    return response
