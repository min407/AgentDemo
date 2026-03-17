# Vercel Python API Entry Point
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.app import app

# Vercel serverless handler
def handler(request, context=None):
    """Vercel serverless function handler"""
    return app(request.environ, lambda status, headers: Response(status=status, headers=headers))

from werkzeug.wrappers import Response
