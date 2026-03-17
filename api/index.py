# Vercel Python API Entry Point
from api.app import app

# Vercel expects a WSGI application
app.debug = False

def handler(request):
    """Vercel serverless handler"""
    return app(request.environ, lambda status, headers: Response(status=status, headers=headers))

from werkzeug.wrappers import Response
