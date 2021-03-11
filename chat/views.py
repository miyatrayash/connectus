from django.shortcuts import render

# Create your views here.
def home(request):
    print("here")
    return render(request,"chat/home.html",{"fullname": request.user.username})