import json

from channels.generic.websocket import AsyncWebsocketConsumer
from chat.services import chat_save_message