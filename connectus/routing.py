import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

from django.core.asgi import get_asgi_application
from chat.consumers import PublicChatConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectus.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path("public_chat/<room_id>/", PublicChatConsumer.as_asgi()),
            ])
        )
    )
})