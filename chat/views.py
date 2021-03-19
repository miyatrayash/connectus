from chat.filters import UserFilter
from chat.utils import save_temp_profile_image_from_base64String
from loginmodule.forms import AccountUpdateForm
from friends.views import friend_list_view
from friends.models import FriendList, FriendRequest
from django.shortcuts import redirect, render
from loginmodule.models import User, get_default_profile_image
from django.http import HttpResponse
from django.conf import settings
from django.core import files
from friends.utils import get_friend_request_or_false
from friends.friends_request_status import FriendRequestStatus
from friends.models import FriendList
import os
import cv2
import json

def public_chat_view(request):
    context = {}
    context['debug_mode'] = settings.DEBUG
    context['room_id']  = 1
    return render(request,"chat/public_chat.html",context)

def home(request):
    return render(request,"chat/home.html",{"fullname": request.user.username})


def account_view(request, *args,**kwargs):
    context = {}
    user_id = kwargs.get('user_id')

    try:
        user  = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse("user not exist")

    if user:
        context['id'] = user.id
        context['username'] = user.username
        context['profile_image'] = user.profile_image.url
        context['hide_email'] = user.hide_email
        context['email'] = user.email



        try:
            friend_list = FriendList.objects.get(user=user)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=user)
            friend_list.save()
    
        friends = friend_list.friends.all()
        context['friends'] =  friends

        is_self = True
        is_friends = False

        viewer = request.user
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        friend_requests = None
        if viewer.is_authenticated and viewer != user or not viewer.is_authenticated:
            is_self = False
            if friends.filter(pk=viewer.id):
                is_friends = True
            else:

                if get_friend_request_or_false(sender=user,receiver=viewer) != False:
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context['pending_friend_request_id'] = get_friend_request_or_false(sender=user,receiver=viewer).id
                    # print(context['pending_friend_request_id'])
                elif get_friend_request_or_false(sender=viewer,receiver=user) != False:
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

        else:
            try:
                friend_requests = FriendRequest.objects.filter(receiver=viewer,is_active=True)
            except FriendRequest.DoesNotExist:
                pass
        
        context['is_self'] = is_self
        context['is_friend'] = is_friends

        context['BASE_URL'] = settings.BASE_URL
        context['request_sent'] = request_sent
        context['friend_requests'] = friend_requests

        return render(request,"account/account.html",context)


def account_search_view(request,*args,**kwargs):
    context = {}
    if request.method == 'GET':
        search_query =request.GET.get("q")
        if len(search_query) > 0:
            user_list = User.objects.all()
            user_filter = UserFilter(request.GET, queryset=user_list)

            users = []

            for user in user_filter.qs:
                try:
                    friend_list = FriendList.objects.get(user=request.user,friends__id=user.id)
                    is_friend = True
                except FriendList.DoesNotExist:
                    is_friend = False
                users.append((user,is_friend))




            context['accounts'] = users

    return render(request, "account/search_results.html",context)


def edit_account_view(request,*args,**kwargs):
    if not request.user.is_authenticated:
        return redirect("login")


    user_id = kwargs.get("user_id")
    print(request.user.profile_image.url)
    try:
        user = User.objects.get(pk=user_id)

    except User.DoesNotExist:
        return HttpResponse("something went wrong")


    if user.pk != request.user.pk:
        return HttpResponse("You cant edit someone else")

    
    context = {}
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    if request.POST:
        form = AccountUpdateForm(request.POST,request.FILES,instance=request.user)

        if form.is_valid():
            form.save()
            return redirect("account:view",user_id=user.pk)
        else:
            form = AccountUpdateForm(request.POST, instance=request.user,
            initial= {
                "id": user.pk,
                "email": user.email,
                "username": user.username,
                "profile_image": user.profile_image,
                "hide_email": user.hide_email,
            }
            )
            context['form'] = form
    else:
        form = AccountUpdateForm(
            initial= {
                "id": user.pk,
                "email": user.email,
                "username": user.username,
                "profile_image": user.profile_image,
                "hide_email": user.hide_email,
            }
        )
        context['form'] = form

    
    return render(request,"account/edit_account.html", context)
    


def crop_image(request,*args,**kwargs):
    payload = {}

    user = request.user

    if request.POST and user.is_authenticated:
        try:
            imageString = request.POST.get("image")
            url = save_temp_profile_image_from_base64String(imageString,user)
            img = cv2.imread(url)
            cropX = int(float(str(request.POST.get("cropX"))))
            cropY = int(float(str(request.POST.get("cropY"))))
            cropWidth = int(float(str(request.POST.get("cropWidth"))))
            cropHeight = int(float(str(request.POST.get("cropHeight"))))

            if cropX < 0:
                cropX = 0
            if cropY < 0:
                cropY = 0

            print(url)
            crop_image = img[cropY:cropY + cropHeight,cropX:cropX + cropWidth]

            cv2.imwrite(url,crop_image)
            if user.profile_image.url != os.path.join("/media/", get_default_profile_image()):
                user.profile_image.delete()
            user.profile_image.save("profile_image.png",files.File(open(url,"rb")))
            user.save()

            payload['result'] = "success"
            payload['cropped_profile_image'] = user.profile_image.url

            os.remove(url)
        except Exception as e:
            payload['result'] = 'error'
            payload['exception'] = str(e)

    return HttpResponse(json.dumps(payload),content_type="application/json")
