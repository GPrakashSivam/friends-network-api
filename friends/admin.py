from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Friends_Request, Friendships, User_Activity, Blocks
from django.utils.translation import gettext_lazy as _

# Registering User model to Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'role')
    search_fields = ('email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'role'),
        }),
    )

# Registering Friends_Request model
@admin.register(Friends_Request)
class FriendsRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__email', 'receiver__email')
    ordering = ('created_at',)
    
    fieldsets = (
        (None, {'fields': ('sender', 'receiver', 'status',)}),
    )

# Registering Friendships model
@admin.register(Friendships)
class FriendshipsAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user1__email', 'user2__email')
    ordering = ('created_at',)

    fieldsets = (
        (None, {'fields': ('user1', 'user2',)}),
    )

# Registering User_Activity model
@admin.register(User_Activity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email',)
    ordering = ('created_at',)

    fieldsets = (
        (None, {'fields': ('user', 'activity_type', 'description',)}),
    )

# Registering Blocks model
@admin.register(Blocks)
class BlocksAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('blocker__email', 'blocked__email')
    ordering = ('created_at',)

    fieldsets = (
        (None, {'fields': ('blocker', 'blocked',)}),
    )
