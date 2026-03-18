import os
import sys
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastenot_project.settings')

# Import Django WSGI
import django
from django.core.wsgi import get_wsgi_application

django.setup()
application = get_wsgi_application()
