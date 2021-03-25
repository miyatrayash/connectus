from django.db import  models
from django.conf import settings


class PublicChatRoom(models.Model):
    title               =  models.CharField(max_length=255,unique=True,blank=False)
    users               =  models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,null=True,help_text="Connected User")

    def __str__(self) -> str:
        return self.title


    def connect_user(self, user):

        is_user_added = False

        if not user in self.users.all():
            print(f"\n\n\n{user}\n\n\n")
            self.users.add(user)
            self.save()
            is_user_added = True
        elif user in self.users.all():
            is_user_added = True

        return is_user_added


    def disconnect_user(self, user):

        is_user_removed = False

        if user in self.users.all():
            self.users.remove(user)
            self.save()
            is_user_removed = True

        return is_user_removed


    @property
    def group_name(self):
        return f"PublicChatRoom-{self.id}"

class PublicRoomChatMessageManager(models.Model):
    def by_room(self,room):
        qs = PublicRoomChatMessage.objects.filter(room=room).order_by("-timestamp")
        return qs


class PublicRoomChatMessage(models.Model):
    user            = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    room            = models.ForeignKey(PublicChatRoom,on_delete=models.CASCADE)
    timestamp       = models.DateTimeField(auto_now_add=True)
    content         = models.TextField(unique=False,blank=False)


    objects = PublicRoomChatMessageManager()

    def __str__(self):
        return self.content


class PrivateChatRoom(models.Model):

    user1               = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user1")
    user2               = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user2")

    connected_users     = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="connected_users")
    is_active = models.BooleanField(default=False)


    @property
    def group_name(self):
        """
        Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
        return f"PrivateChatRoom-{self.id}"


class RoomChatMessageManager(models.Manager):
	def by_room(self, room):
		qs = RoomChatMessage.objects.filter(room=room).order_by("-timestamp")
		return qs

class RoomChatMessage(models.Model):
	"""
	Chat message created by a user inside a Room
	"""
	user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	room                = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
	timestamp           = models.DateTimeField(auto_now_add=True)
	content             = models.TextField(unique=False, blank=False,)

	objects = RoomChatMessageManager()

	def __str__(self):
		return self.content