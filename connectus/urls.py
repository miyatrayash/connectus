"""connectus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from chat.views import home
from loginmodule.views import login,logout,sign_up,home_screen,contact_us

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login,name="login"),
    path('logout/', logout,name="log_out"),
    path('sign_up/',sign_up,name="sign_up"),
    path('', home_screen,name="home_screen"),
    path('contact_us/',contact_us,name="contact_us"),
    path('home/',home,name='home'),
    path('account/',include('chat.urls',namespace='account'))
]


if settings.DEBUG:
    urlpatterns+= static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns+= static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)