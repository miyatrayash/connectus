from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from django.contrib.auth import get_user_model
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils import timezone
from datetime import datetime
from channels.db import database_sync_to_async
from django.core.paginator import Paginator
from django.core.serializers.python import Serializer

from chat.models import PublicChatRoom, PublicRoomChatMessage
count = 0
User = get_user_model()

DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE = 20

MSG_TYPE_MESSAGE = 0  # For standard messages
MSG_TYPE_CONNECTED_USER_COUNT = 1 # Sending the number of connected users to the chat room
class PublicChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        global count
        print("PublicChatConsumer: connect: " + str(self.scope['user']))
        print(f"Connect: {count}")
        count += 1
        await self.accept()
        self.room_id = None


    async def disconnect(self, code):

        global count
        print("PublicChatConsumer: disconnect")
        print(f"DisConnect: {count}")
        count += 1
        try:
            if self.room_id != None:
                await self.leave_room(self.room_id)
        except Exception:
            pass

    async def receive_json(self, content, **kwargs):

        global count
        command = content.get("command", None)
        print(f"Receive_json: {count}")
        count += 1

        print("PublicChatConsumer: receive_json: " + str(command))

        try:
            if command == "send":
                if len(content["message"].lstrip()) != 0:
                    # raise ClientError(422,"You can't send an empty message.")
                    await self.send_room(content["room_id"], content["message"])
            elif command == "join":
                # Make them join the room
                await self.join_room(content["room"])
            elif command == "leave":
            # Leave the room
                await self.leave_room(content["room"])
            elif command == "get_room_chat_messages":
                await self.display_progress_bar(True)
                room = await get_room_or_error(content['room_id'])
                payload = await get_room_chat_messages(room, content['page_number'])
                if payload != None:
                    payload = json.loads(payload)
                    await self.send_messages_payload(payload['messages'], payload['new_page_number'])
                else:
                    raise ClientError(204,"Something went wrong retrieving the chatroom messages.")
                await self.display_progress_bar(False)
        except ClientError as e:
            await self.display_progress_bar(False)
            await self.handle_client_error(e)


    async def send_room(self, room_id, message):
        """
            Called by receive_json when someone sends a message to a room.
        """
    # Check they are in this room
        global count
        print(f"Send_room: {count}")
        count +=1
        print("PublicChatConsumer: send_room")
        if self.room_id != None:
            if str(room_id) != str(self.room_id):
                raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
            if not is_authenticated(self.scope["user"]):
                raise ClientError("AUTH_ERROR", "You must be authenticated to chat.")
        else:
            raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")

        # Get the room and send to the group about it
        room = await get_room_or_error(room_id)
        await create_public_room_chat_message(room,self.scope["user"], message)
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "profile_image": self.scope["user"].profile_image.url,
                "username": self.scope["user"].username,
                "user_id": self.scope["user"].id,
                "message": message,

            }
        )

    async def chat_message(self,event):
        global count
        print(f"Chat_message: {count}")
        count += 1
        print("PublicChatConsumer: chat_message from user #" + str(event["user_id"]))
        timestamp = calculate_timestamp(timezone.localtime(timezone.now()))
        await self.send_json(
            {
                "msg_type": MSG_TYPE_MESSAGE,
                "profile_image": event["profile_image"],
                "username": event["username"],
                "user_id": event["user_id"],
                "message": event["message"],
				"natural_timestamp": timestamp,
            }
        )

    async def join_room(self, room_id):
            global count
            print(f"Join_room: {count}")
            count += 1
            """
            Called by receive_json when someone sent a join command.
            """
            print("PublicChatConsumer: join_room")
            is_auth = is_authenticated(self.scope["user"])
            print("here")
            try:
                room = await get_room_or_error(room_id)
            except ClientError as e:
                await self.handle_client_error(e)

            # Add user to "users" list for room
            if is_auth:
                await connect_user(room, self.scope["user"])

            # Store that we're in the room
            self.room_id = room.id

            # Add them to the group so they get room messages
            await self.channel_layer.group_add(
                room.group_name,
                self.channel_name,
            )

            # Instruct their client to finish opening the room
            await self.send_json({
                "join": str(room.id)
            })

            # send the new user count to the room
            num_connected_users = await  get_num_connected_users(room)
            await self.channel_layer.group_send(
            room.group_name,
            {
				"type": "connected.user.count",
				"connected_user_count": num_connected_users,
			}
            )
    async def leave_room(self, room_id):

        """
        Called by receive_json when someone sent a leave command.
        """
        print("PublicChatConsumer: leave_room")
        global count
        print(f"Leave Room: {count}")
        count += 1
        is_auth = is_authenticated(self.scope["user"])
        room = await get_room_or_error(room_id)

        # Remove user from "users" list
        if is_auth:
            await disconnect_user(room, self.scope["user"])

        # Remove that we're in the room
        self.room_id = None
        # Remove them from the group so they no longer get room messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name,
        )

        # send the new user count to the room
        num_connected_users = await get_num_connected_users(room)
        await self.channel_layer.group_send(
        room.group_name,
			{
				"type": "connected.user.count",
				"connected_user_count": num_connected_users,
			}
		)



    async def handle_client_error(self, e):
            """
            Called when a ClientError is raised.
            Sends error data to UI.
            """
            errorData = {}
            errorData['error'] = e.code
            if e.message:
                errorData['message'] = e.message
                await self.send_json(errorData)

    async def send_messages_payload(self, messages, new_page_number):
        """
		Send a payload of messages to the ui
		"""
        print("PublicChatConsumer: send_messages_payload. ")
        await self.send_json(
			{
				"messages_payload": "messages_payload",
				"messages": messages,
				"new_page_number": new_page_number,
			},
		)

    async def connected_user_count(self, event):
        """
		Called to send the number of connected users to the room.
		This number is displayed in the room so other users know how many users are connected to the chat.
		"""
		# Send a message down to the client
        print("PublicChatConsumer: connected_user_count: count: " + str(event["connected_user_count"]))
        await self.send_json(
			{
				"msg_type": MSG_TYPE_CONNECTED_USER_COUNT,
				"connected_user_count": event["connected_user_count"]
			},
		)

    async def display_progress_bar(self, is_displayed):
            """
        1. is_displayed = True
		- Display the progress bar on UI
		2. is_displayed = False
		- Hide the progress bar on UI
        """
            print("DISPLAY PROGRESS BAR: " + str(is_displayed))
            await self.send_json(
			{
				"display_progress_bar": is_displayed
			}
		)
def is_authenticated(user):
    if user.is_authenticated:
        return True
    return False

@sync_to_async
def get_num_connected_users(room):
	if room.users:
		return len(room.users.all())
	return 0

@database_sync_to_async
def create_public_room_chat_message(room, user, message):
    return PublicRoomChatMessage.objects.create(user=user,room=room, content=message)

@database_sync_to_async
def connect_user(room, user):
    global count
    print(f"Connect User: {count}")
    count += 1
    return room.connect_user(user)

@database_sync_to_async
def disconnect_user(room, user):
    global count
    print(f"DisConnect User: {count}")
    count += 1
    return room.disconnect_user(user)

@database_sync_to_async
def get_room_or_error(room_id):

    try:
        rooms = PublicChatRoom.objects.all()
        if len(rooms) < 1:
            room = PublicChatRoom.objects.create(pk=room_id)
        else:
            room = PublicChatRoom.objects.get(pk=room_id)

    except PublicChatRoom.DoesNotExist:
        raise ClientError("ROOM_INVALID", "Invalid room.")

    return room

@database_sync_to_async
def get_room_chat_messages(room, page_number):
    try:
        qs = PublicRoomChatMessage.objects.filter(room=room).order_by("-timestamp")
        p = Paginator(qs, DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)
        payload = {}
        messages_data = None
        new_page_number = int(page_number)

        if new_page_number <= p.num_pages:
            new_page_number = new_page_number + 1
            s = LazyRoomChatMessageEncoder()
            payload['messages'] = s.serialize(p.page(page_number).object_list)

        else:
            payload['messages'] = "None"
            payload['new_page_number'] = new_page_number
        payload['new_page_number'] = new_page_number
        return json.dumps(payload)

    except Exception as e:
        print("EXCEPTION: " + str(e))
        return None
class ClientError(Exception):
    """
    Custom exception class that is caught by the websocket receive()
    handler and translated into a send back to the client.
    """
    def __init__(self, code, message):
        super().__init__(code)
        self.code = code
        if message:
            self.message = message


def calculate_timestamp(timestamp):
    """
    1. Today or yesterday:
        - EX: 'today at 10:56 AM'
        - EX: 'yesterday at 5:19 PM'
    2. other:
        - EX: 05/06/2020
        - EX: 12/28/2020
    """
    ts = ""
    # Today or yesterday
    if (naturalday(timestamp) == "today") or (naturalday(timestamp) == "yesterday"):
        str_time = datetime.strftime(timestamp, "%I:%M %p")
        str_time = str_time.strip("0")
        ts = f"{naturalday(timestamp)} at {str_time}"
    # other days
    else:
        str_time = datetime.strftime(timestamp, "%m/%d/%Y")
        ts = f"{str_time}"
    return str(ts)

class LazyRoomChatMessageEncoder(Serializer):
	
    def get_dump_object(self, obj):
        dump_object = {}
        dump_object.update({'msg_type': MSG_TYPE_MESSAGE})
        dump_object.update({'msg_id': str(obj.id)})
        dump_object.update({'user_id': str(obj.user.id)})
        dump_object.update({'username': str(obj.user.username)})
        dump_object.update({'message': str(obj.content)})
        dump_object.update({'profile_image': str(obj.user.profile_image.url)})
        dump_object.update({'natural_timestamp': calculate_timestamp(timezone.localtime(obj.timestamp))})
        return dump_object