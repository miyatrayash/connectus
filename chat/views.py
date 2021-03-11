from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,"home.html",{"full_name": request.user.username})