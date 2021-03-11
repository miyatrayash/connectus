from tortoise import Tortoise, run_async
from django.conf import settings
from .tortoise_models import ChatMessage

async def chat_save_message(username,room_id,message,message_type,image_caption):
    # 
    pass