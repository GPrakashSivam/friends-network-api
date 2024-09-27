from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from .views import (
    UserSignupView,
    UserLoginView,
    UserSearchView,
    AcceptFriendRequestView,
    RejectFriendRequestView,
    SendFriendRequestView,
    FriendsListView,
    PendingFriendRequestsView,
    UserActivityListView,
    BlockUserView,
    UnblockUserView,
    CustomTokenRefreshView
)

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='search'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    # Friend Request Management
    path('friend-request/send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/accept/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('friend-request/reject/', RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('friends/', FriendsListView.as_view(), name='friends-list'),
    path('friend-requests/pending/', PendingFriendRequestsView.as_view(), name='pending-friend-requests'),
    path('activities/', UserActivityListView.as_view(), name='user-activity-list'),
    
    # Block Management
    path('block/', BlockUserView.as_view(), name='block-user'),
    path('unblock/', UnblockUserView.as_view(), name='unblock-user'),

    # API schema generation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Redoc API UI
    path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
