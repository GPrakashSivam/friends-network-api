from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Friends_Request, User_Activity

class UserSignupSerializer(serializers.ModelSerializer):
    """
    Serializer for representing User Signup view
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name')
    
    def validate_email(self, value):
        """
        Check that the email is unique (case-insensitive).
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value


    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for representing User Login view
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email').lower()
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        data['user'] = user
        return data

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for representing User data in search results view.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')

class FriendsRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for representing User data in New Friends Request view
    """
    receiver_id = serializers.IntegerField()
    class Meta:
        model = Friends_Request
        fields = ['receiver_id', 'status']

class FriendSerializer(serializers.ModelSerializer):
    """
    Serializer for representing User data in Friends(accepted) view
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class PendingFriendRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for representing User data in Pending Friends Request view
    """
    sender = FriendSerializer(read_only=True)

    class Meta:
        model = Friends_Request
        fields = ['id','sender', 'receiver', 'created_at']

class AcceptFriendRequestSerializer(serializers.Serializer):
    """
    Serializer for representing User data to Accept New Friends
    """
    request_id = serializers.IntegerField()

    class Meta:
        model = Friends_Request
        fields = ['id','sender', 'receiver']

class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for representing User data in User Activities view
    """
    class Meta:
        model = User_Activity
        fields = ['activity_type', 'description', 'created_at']

class RejectFriendRequestSerializer(serializers.Serializer):
    """
    Serializer for representing User data to Reject Friends Request view
    """
    request_id = serializers.IntegerField()

class BlockUserSerializer(serializers.Serializer):
    """
    Serializer for representing User data to Block User view
    """
    user_id = serializers.IntegerField()

class UnblockUserSerializer(serializers.Serializer):
    """
    Serializer for representing User data to UnBlock User view
    """
    user_id = serializers.IntegerField()