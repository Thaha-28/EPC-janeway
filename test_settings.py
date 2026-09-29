import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.railway_settings'
import django
django.setup()
print('Settings OK')
print('ALLOWED_HOSTS:', os.environ.get('ALLOWED_HOSTS', 'not set'))