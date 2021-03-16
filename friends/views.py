from django.shortcuts import redirect, render
from django.http import HttpResponse
import json

from loginmodule.models import User
from friends.models import FriendList, FriendRequest

def friend_list_view(request,*args, **kwargs):
    context = {}

    user = request.user

    if user.is_authenticated:
        user_id = kwargs.get("user_id")

        if user_id:
            try:
                this_user = User.objects.get(pk=user_id)
                context['this_user'] = this_user
            except User.DoesNotExist:
                return HttpResponse("That user does not exist.")

            try:
                friend_list = FriendList.objects.get(user=this_user)
            except FriendList.DoesNotExist:
                pass
        
            if user != this_user and not user in friend_list.friends.all():
                    return HttpResponse("You must be friends")

            friends = []

            auth_user_friend_list = FriendList.objects.get(user=user)

            for friend in friend_list.friends.all():
                friends.append((friend,auth_user_friend_list.is_mutual_friend(friend)))
            context['friends'] = friends
    else:
        return HttpResponse("not authenticated")

    return render(request,"friends/friends_list.html",context)

def friend_requests(request,*args,**kwargs):
    context = {}
    
    user = request.user
    if user.is_authenticated:
        user_id  = kwargs.get("user_id")
        viewer = User.objects.get(pk=user_id)

        if viewer == user:
            friend_requests = FriendRequest.objects.filter(receiver=viewer,is_active=True)
            context['friend_requests'] = friend_requests

        else:
            return HttpResponse("You cant view other's friend requests")

    else:
        redirect("login")
    
    return render(request,"friends/friend_requests.html",context)

def send_friend_request(request, *args, **kwargs):
    user = request.user

    payload = {}

    payload['response'] = "something went wrong"

    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")

        if user_id:
            receiver = User.objects.get(pk=user_id)

            try:
                friend_requests = FriendRequest.objects.filter(sender=user,receiver=receiver)

                try:
                    for request in friend_requests:
                        if request.is_active:
                            raise FileExistsError("YOu already send them")
                    friend_request = FriendRequest(sender=user,receiver=receiver)
                    friend_request.save()
                    payload['response'] = "Friend request sent."

                except Exception as e:
                    payload['response'] = str(e)
            except FriendRequest.DoesNotExis:
                friend_request = FriendRequest(sender=user,receiver=receiver)
                friend_request.save()
                payload['response'] = "Friend request sent"

        else:
            payload['response'] = "Unable To send"

    else:
        payload['response'] = "You must be authenticated"

    return HttpResponse(json.dumps(payload),)


def accept_friend_request(request, *args, **kwargs):
    user = request.user

    payload = {}

    if request.method == "GET" and user.is_authenticated:
        friend_request_id = kwargs.get("friend_request_id")
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)


            if friend_request.receiver == user:
                friend_request.accept()

                payload['response'] = "Accepted"
            else:
                payload['response'] = "Something is wrong"

        else:
            payload['response'] = "Unable TO Accept"
    else:
        payload['response'] = "Not authenticated"

    return HttpResponse(json.dumps(payload),content_type="application/json")


def remove_friend(request,*agrs,**kwargs):
    user = request.user

    payload = {}


    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")

        if user_id:
            try:
                removee = User.objects.get(pk=user_id)
                friend_list = FriendList.objects.get(user=user)
                friend_list.unfriend(removee)
                payload['payload'] = "Removed"
            except Exception as e:
                payload['response'] = str(e)

        else:
            payload['response'] = "Unable To remove"

    else:
        payload['response'] = "not authenticated"

    return HttpResponse(json.dumps(payload),content_type="application/json")

def decline_friend_request(request,*agrs, **kwargs):
    user = request.user

    payload = {}

    if request.method == "GET" and user.is_authenticated:
        friend_request_id = kwargs.get("friend_request_id")
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)

            if friend_request.receiver == user:
                if friend_request:
                    friend_request.decline()

                    payload['response'] = "Declined"
                else:
                    payload['response'] = "Something went wrong"

            else:
                payload['response'] = "not your request"
        else:
            payload['response'] = "Unable To decline"
    else:
        payload['response'] = "not  Authenticated"

    return HttpResponse(json.dumps(payload),content_type="application/json")



def cancel_friend_request(request,*agrs, **kwargs):
    user = request.user
    payload = {}

    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            receiver = User.objects.get(pk=user_id)

            try:
                friend_requests = FriendRequest.objects.filter(sender=user,receiver=receiver,is_active=True)

                for request in friend_requests:
                    request.cancel()
                    payload['response'] = "cancelled"
            except Exception:
                payload['response'] = "not exist"

        else:
            payload['response'] = "unable to cancel"
    else:
        payload['response'] = "Not authenticated"



    return HttpResponse(json.dumps(payload),content_type="application/json")