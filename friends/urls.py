from django.urls import path


from friends.views import (
    send_friend_request,
    friend_requests,
    accept_friend_request,
    remove_friend,
    decline_friend_request,
    cancel_friend_request,
    friend_list_view
)

app_name = "friends"

urlpatterns = [
    path('friend_request/', send_friend_request, name="friend-request"),
    path('friend_list/<user_id>', friend_list_view, name="friend-list"),
    path('friend_request/<user_id>/', friend_requests, name="friend-requests"),
    path('accept_friend_request/<friend_request_id>/', accept_friend_request, name="accept-friend-request"),
    path('decline_friend_request/<friend_request_id>/', decline_friend_request, name="decline-friend-request"),
    path('cancel_friend_request/', cancel_friend_request, name="cancel-friend-request"),
    path('friend_remove/', remove_friend, name="remove-friend"),
]