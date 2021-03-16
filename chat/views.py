from friends.views import friend_list_view
from friends.models import FriendList, FriendRequest
from django.shortcuts import redirect, render
from loginmodule.models import User
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core import files
from friends.utils import get_friend_request_or_false
from friends.friends_request_status import FriendRequestStatus
from friends.models import FriendList
import os
import cv2
import json
import base64
TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"

# Create your views here.
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
            search_results = User.objects.filter(email__icontains=search_query).filter(username__icontains=search_query).distinct()

            users = []

            for user in search_results:
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
        form = userUpdateForm(request.POST,request.FILES,instance=request.user)

        if form.is_valid():
            form.save()
            return redirect("account:view",user_id=user.pk)
        else:
            form = userUpdateForm(request.POST, instance=request.user,
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
        form = userUpdateForm(
            initial= {
                "id": user.pk,
                "email": user.email,
                "username": user.username,
                "profile_image": user.profile_image,
                "hide_email": user.hide_email,
            }
        )
        context['form'] = form

    
    return render(request,"account/edit_user.html", context)
    


def save_temp_profile_image_from_base64String(imageString, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"

    try:

        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        if not os.path.exists(f"{settings.TEMP}/{str(user.pk)}"):
            os.mkdir(settings.TEMP + "/" + str(user.pk))
        url = os.path.join(settings.TEMP + "/" + str(user.pk),TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(imageString)
        with storage.open('', 'wb+') as destination:
            destination.write(image)
            destination.close()

        return url
    except Exception as e:
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imageString += "=" * ((4 - len(imageString) % 4) % 4)
            return save_temp_profile_image_from_base64String(imageString,user)
        return None

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

            crop_image = img[cropY:cropY + cropHeight,cropX:cropX + cropWidth]

            cv2.imwrite(url,crop_image)

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