from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.template.context_processors import csrf


def login(request):
    c = {}
    c.update(csrf(request))
    return render(request,'login.html', c)

def auth_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    # username = 'test'
    # password = 'test123'
    user = auth.authenticate(username=username, password=password)

    # User.objects.create_user( username="whatever", email="whatever@some.com", password="password")
    # user = auth.authenticate(username="whatever", password="password")


    if user is not None:
        auth.login(request,user)
        return HttpResponseRedirect('/loginmodule/logged_in/')
    else:
        return HttpResponseRedirect('/loginmodule/invalid_login/')

def logged_in(request):
    return render(request,'logged_in.html', {"full_name": request.user.username})


def invalid_login(request):
    return render(request,'invalid_login.html')

def logout(request):
    auth.logout(request)
    return render(request,'logout.html')

def home_screen(request):
    return render(request,'home.html')

