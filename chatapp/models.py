from django.db import models

# Create your models here.
class permissions(models.Model):
    permissions_id=models.IntegerField(primary_key=True)
    permissions_role_id=models.IntegerField()
    permissions_title=models.TextField()
    permissions_module=models.TextField()
    permissions_description=models.TextField(blank=True,max_length=255)

class user_class(models.Model):
    user_id = models.IntegerField(primary_key=True)
    user_role_id= models.IntegerField()
    user_email=models.TextField()
    user_don=models.DateTimeField()
    user_addresses=models.TextField(max_length=255)

class Role_class(models.Model):
    #role_id = models.ForeignKey(user_class)
    role_title = models.CharField(max_length=15)
    role_description=models.TextField(blank=True,max_length=100)

class chat_class(models.Model):
    chat_id=models.IntegerField(primary_key=True)
    chat_history = models.TextField(max_length=200)

class group_chat(models.Model):
    group_chat_id=models.IntegerField(primary_key=True)
    group_chat_name=models.CharField(max_length=30)
    group_chat_history=models.TextField()
    #group_chat_user_id=ForeignKey(user_id)

class chat_histor(models.Model):
    chat_history_id=models.IntegerField(primary_key=True)
    chat_history_time=models.TextField()
    chat_history_discription=models.CharField(max_length=200)
    #chat_history_user_id=ForeignKey(user_class)


