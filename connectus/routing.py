from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter,URLRouter
import chat
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    )
})