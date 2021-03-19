from loginmodule.forms import AccountAuthenticationForm, RegistrationForm
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template.context_processors import csrf
from .models import User


def login(request):
    context = {}

    user = request.user

    if user.is_authenticated:
        return redirect("public_chat")



    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = auth.authenticate(email=email,password=password)

            if user:
                auth.login(request,user)
                return redirect("public_chat")


        else:
            context['login_form'] =form
    return render(request, "loginmodule/login.html", context)


def contact_us(request):
    c = {}
    c.update(csrf(request))
    return render(request,"loginmodule/contact_us.html")

def logout(request):
    auth.logout(request)
    return render(request, "loginmodule/logout.html")


def home_screen(request):
    return render(request, "loginmodule/home_screen.html")


def sign_up(request):
    user = request.user

    if user.is_authenticated:
        return HttpResponse(f"You are already authenticated as {user.email}.")

    context = {}

    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            account = auth.authenticate(email=email,password=raw_password)

            auth.login(request, account)
            return redirect("public_chat")
    

        else:
            context['registration_form'] = form

    return render(request,'loginmodule/sign_up.html', context)

