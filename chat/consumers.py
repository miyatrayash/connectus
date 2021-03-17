from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from django.contrib.auth import get_user_model

User = get_user_model()

class PublicChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        
        print("PublicChatConsumer: connect: " + str(self.scope['user']))
        
        await self.accept()


        await self.channel_layer.group_add(
            "public_chatroom_1",
            self.channel_name
        )

    async def disconnect(self, code):
        
        print("PublicChatConsumer: disconnect")

    async def receive_json(self, content, **kwargs):
        
        command = content.get("command", None)
        
        print("PublicChatConsumer: receive_json: " + str(command))
        print("PublicChatConsumer: receive_json: message: " + str(content["message"]))

        if command == "send":
            if len(content["message"].lstrip()) == 0:
                raise Exception("Can't send Empty Message")
            await self.send_message(content["message"])

    async def send_message(self,message):
        await self.channel_layer.group_send(
            "public_chatroom_1",
            {
                "type": "chat.message",
                "profile_image": self.scope["user"].profile_image.url,
                "username": self.scope["user"].username,
                "user_id": self.scope["user"].id,
                "message": message,

            }
        )

    async def chat_message(self,event):

        print("PublicChatConsumer: chat_message from user #" + str(event["user_id"]))

        await self.send_json(
            {
                "profile_image": event["profile_image"],
                "username": event["username"],
                "user_id": event["user_id"],
                "message": event["message"],
            }
        )