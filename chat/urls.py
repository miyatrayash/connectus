from django.urls import path
from django.urls.resolvers import URLPattern

from .views import (
    account_view, crop_image, edit_account_view,
)

app_name = "account"

urlpatterns = [
    path('<user_id>/',account_view, name="view"),
    path('<user_id>/edit/',edit_account_view, name="edit"),
    path('<user_id>/edit/cropImage',crop_image, name="crop_image"),


]