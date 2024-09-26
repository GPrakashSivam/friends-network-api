from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from .models import User, Friends_Request, Friendships, User_Activity, Blocks
from .serializers import UserSignupSerializer, UserLoginSerializer, UserSerializer, UserActivitySerializer
from .serializers import (
    FriendsRequestSerializer,
    AcceptFriendRequestSerializer,
    RejectFriendRequestSerializer,
    FriendSerializer,
    PendingFriendRequestSerializer,
    BlockUserSerializer,
    UnblockUserSerializer
)

class UserSignupView(generics.CreateAPIView):
    """
    API to Signup for new users(friends)
    """
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSignupSerializer(user, context=self.get_serializer_context()).data,
                "message": "User created successfully."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(generics.GenericAPIView):
    """
    API view for Users to Login with email & password
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    # Apply rate limiting: max 5 attempts per minute per IP
    @method_decorator(ratelimit(key='ip', rate='5/m', block=False))
    def post(self, request, *args, **kwargs):
        was_limited = getattr(request, 'limited', False)
        if was_limited:
            return Response({
                "error": "Too many login attempts. Please try again later."
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            response = Response({
                "access": str(refresh.access_token),
                "message": "Login successful."
            }, status=status.HTTP_200_OK)
            # Set refresh token in HTTP-Only cookie
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,  # Ensure HTTPS
                samesite='Lax'  #or 'Strict'
            )
            return response
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenRefreshView(TokenRefreshView):
    """
    API view to Refresh the Access Token(used internally)
    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"detail": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            new_access = refresh.access_token
            return Response({
                'access': str(new_access),
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

class StandardResultsSetPagination(PageNumberPagination):
    """
    Class to ste Pagination Size
    """
    page_size = 10  # Up to 10 records per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserSearchView(generics.ListAPIView):
    """
    API view to search for users by email or name.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Optionally restricts the returned users to a search keyword,
        by filtering against a `search` query parameter in the URL.
        """
        queryset = User.objects.all()
        search_keyword = self.request.query_params.get('search', '').strip()

        if search_keyword:
            # Check if the search keyword exactly matches an email (case-insensitive)
            email_match = queryset.filter(email__iexact=search_keyword)
            if email_match.exists():
                return email_match

            # If not an exact email match, perform full-text search on first_name and last_name
            search_vector = SearchVector('first_name', 'last_name')
            search_query = SearchQuery(search_keyword)
            queryset = queryset.annotate(rank=SearchRank(search_vector, search_query)) \
                               .filter(Q(first_name__icontains=search_keyword) | Q(last_name__icontains=search_keyword)) \
                               .order_by('-rank', 'first_name', 'last_name')

        return queryset

class SendFriendRequestView(generics.CreateAPIView):
    """
    API view to Send New Friend request to other User(Friend)
    """
    serializer_class = FriendsRequestSerializer
    permission_classes = [IsAuthenticated]
    
    @method_decorator(ratelimit(key='user', rate='3/m', block=True))
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        receiver_id = serializer.validated_data['receiver_id']
        
        if receiver_id == request.user.id:
            return Response({"detail": "Cannot send friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({"detail": f"Receiver not found - {receiver_id}"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if blocked
        if Blocks.objects.filter(blocker=receiver, blocked=request.user).exists():
            return Response({"detail": "You are blocked by this user."}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if already friends
        if Friendships.objects.filter(
            Q(user1=request.user, user2=receiver) | Q(user1=receiver, user2=request.user)
        ).exists():
            return Response({"detail": "You are already friends."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if a pending request exists
        if Friends_Request.objects.filter(sender=request.user, receiver=receiver, status='pending').exists():
            return Response({"detail": "Friends request already sent."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check cooldown after rejection
        last_rejected = Friends_Request.objects.filter(sender=request.user, receiver=receiver, status='rejected').order_by('-created_at').first()
        if last_rejected and timezone.now() - last_rejected.timestamp < timedelta(hours=24):
            remaining = timedelta(hours=24) - (timezone.now() - last_rejected.timestamp)
            return Response({"detail": f"Cannot send another friends request for {remaining.seconds//3600} hours."}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            print("localtime:",timezone.localtime())
            friends_request = Friends_Request.objects.create(sender=request.user, receiver=receiver, created_at=timezone.localtime())
            print("******friends_request>>>>>>>",friends_request)
            # Log activity for the sender
            User_Activity.objects.create(user=request.user, activity_type='friend_request_sent',
                description=f"Friend request sent to {friends_request.receiver.email}")
        
        serializer = FriendsRequestSerializer(friends_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AcceptFriendRequestView(generics.GenericAPIView):
    """
    API view to Accept New Friend request got from other User(Friend)
    """
    serializer_class = AcceptFriendRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_id = serializer.validated_data['request_id']
        
        try:
            with transaction.atomic():
                friends_request = Friends_Request.objects.select_for_update().get(id=request_id, receiver=request.user, status='pending')
                friends_request.status = 'accepted'
                friends_request.updated_at = timezone.localtime()
                friends_request.save()
                Friendships.objects.create(user1=friends_request.sender, user2=friends_request.receiver)
                # Log activity for the sender
                User_Activity.objects.create(user=friends_request.receiver, activity_type='friends_request_accepted',
                    description=f"Friends request accepted by {request.user.email}")
            
            return Response({"detail": "Friends request accepted."}, status=status.HTTP_200_OK)

        except Friends_Request.DoesNotExist:
            return Response({"detail": "Friends request not found."}, status=status.HTTP_404_NOT_FOUND)
        
class RejectFriendRequestView(generics.GenericAPIView):
    """
    API view to Reject Friend request from other User
    """
    serializer_class = RejectFriendRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_id = serializer.validated_data['request_id']
        
        try:
            friends_request = Friends_Request.objects.select_for_update().get(id=request_id, receiver=request.user, status='pending')
        except Friends_Request.DoesNotExist:
            return Response({"detail": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)
        
        with transaction.atomic():
            friends_request.status = 'rejected'
            friends_request.save()
        
        return Response({"detail": "Friend request rejected."}, status=status.HTTP_200_OK)

class FriendsListView(generics.ListAPIView):
    """
    API view to list friends of the logged in user.
    Implements caching to optimize performance.
    """
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        cache_key = f"friends_list_user_{user.id}"
        friends = cache.get(cache_key)
        
        if friends is None:
            friendships = Friendships.objects.filter(Q(user1=user) | Q(user2=user)).select_related('user1', 'user2')
            friends = User.objects.filter(
                Q(id__in=friendships.values_list('user1', flat=True)) |
                Q(id__in=friendships.values_list('user2', flat=True))
            ).exclude(id=user.id).distinct()
            cache.set(cache_key, friends, 300)  # Cache for 5 minutes
        
        return friends

class PendingFriendRequestsView(generics.ListAPIView):
    """
    API view to list pending friend requests received by the logged in user.
    Includes pagination and sorting.
    """
    serializer_class = PendingFriendRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Friends_Request.objects.filter(receiver=user, status='pending').select_related('sender').order_by('-created_at')
        return queryset

class UserActivityListView(generics.ListAPIView):
    """
    API view to get User Activities of the logged in User
    """
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        return User_Activity.objects.filter(user=self.request.user).order_by('created_at')

class BlockUserView(generics.GenericAPIView):
    """
    API view to Block the other User
    """
    serializer_class = BlockUserSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data['user_id']
        
        if user_id == request.user.id:
            return Response({"detail": "Cannot block yourself."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_to_block = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        Blocks.objects.get_or_create(blocker=request.user, blocked=user_to_block)
        
        # Optionally, remove existing friendships and friend requests
        Friendships.objects.filter(
            Q(user1=request.user, user2=user_to_block) | Q(user1=user_to_block, user2=request.user)
        ).delete()
        
        Friends_Request.objects.filter(
            Q(sender=request.user, receiver=user_to_block) | Q(sender=user_to_block, receiver=request.user)
        ).delete()
        
        return Response({"detail": f"User {user_to_block.email} has been blocked."}, status=status.HTTP_200_OK)

class UnblockUserView(generics.GenericAPIView):
    """
    API view to UnBlock the other User
    """
    serializer_class = UnblockUserSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data['user_id']
        
        try:
            user_to_unblock = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        Blocks.objects.filter(blocker=request.user, blocked=user_to_unblock).delete()
        
        return Response({"detail": f"User {user_to_unblock.email} has been unblocked."}, status=status.HTTP_200_OK)

