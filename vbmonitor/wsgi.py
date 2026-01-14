import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vbmonitor.settings')
application = get_wsgi_application()
ASGI_APPLICATION = "vbmonitor.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",  # só para desenvolvimento
    }
}
