import os
import sys
from pathlib import Path

root = Path('/home/daswanson22/swanson-software-solutions')
sys.path.insert(0, str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swanson_site.settings')

from dotenv import load_dotenv
load_dotenv(root / '.env')  # adjust path if needed

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
