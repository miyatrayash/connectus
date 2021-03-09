from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template.context_processors import csrf
from .models import User


def login(request):
    c = {}
    c.update(csrf(request))
    return render(request, "login.html", c)


def auth_view(request):
    email = request.POST.get("email")
    password = request.POST.get("password")

    # username = 'test'
    # password = 'test123'
    user = auth.authenticate(email=email, password=password)

    # User.objects.create_user( username="whatever", email="whatever@some.com", password="password")
    # user = auth.authenticate(username="whatever", password="password")

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect("logged_in/")
    else:
        return HttpResponseRedirect("invalid_login/")


def logged_in(request):
    return render(request, "logged_in.html", {"full_name": request.user.username})


def invalid_login(request):
    return render(request, "invalid_login.html")


def logout(request):
    auth.logout(request)
    return render(request, "logout.html")


def home_screen(request):
    return render(request, "home.html")


def sign_up(request):
    c = {}
    c.update(csrf(request))
    return render(request, "sign_up.html", c)


def register(request):

    email = request.POST.get("email")
    password = request.POST.get("password")
    name = request.POST.get("name")
    conf_password = request.POST.get("confPassword")
    username = request.POST.get("username")
    user = User.objects.create_user(
        email,username,name,password
    )
    user.save()

    return HttpResponseRedirect("logged_in/")
