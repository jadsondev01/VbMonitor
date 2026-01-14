from django.urls import path
from . import consumers  # vamos criar isso

websocket_urlpatterns = [
    path('ws/alertas/', consumers.AlertaConsumer.as_asgi()),
]
