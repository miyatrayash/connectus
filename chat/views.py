from django.shortcuts import render
from loginmodule.models import User
from django.http import HttpResponse
from django.conf import settings
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


        #Define state Template variable

        is_self = True
        is_friends = False

        
        if user.is_authenticated and user != request.user or not request.user.is_authenticated:
            is_self = False

        context['is_self'] = is_self
        context['is_friend'] = is_friends

        context['BASE_URL'] = settings.BASE_URL

        return render(request,"account/account.html",context)


def account_search_view(request,*args,**kwargs):
    context = {}
    print("here")
    if request.method == 'GET':
        search_query =request.GET.get("q")
        if len(search_query) > 0:
            search_results = User.objects.filter(email__icontains=search_query).filter(username__icontains=search_query).distinct()

            accounts = []

            for account in search_results:
                accounts.append((account,False))
            context['accounts'] = accounts

    return render(request, "account/search_results.html",context)