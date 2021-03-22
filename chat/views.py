from django.conf import settings
from django.shortcuts import render


def public_chat_view(request):
    context = {}
    context['debug_mode'] = settings.DEBUG
    context['room_id']  = 1
    return render(request,"chat/public_chat.html",context)

def home(request):
    return render(request,"chat/home.html")
