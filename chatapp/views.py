from django.shortcuts import render
from dijango.http import HttpResponse
# Create your views here.
def index(request):
    return HttpResponse("first page")
