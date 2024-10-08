# Generated by Django 5.1.1 on 2024-09-27 09:18

import django.contrib.postgres.indexes
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=30)),
                ('last_name', models.CharField(blank=True, max_length=30)),
                ('role', models.CharField(choices=[('read', 'Read'), ('write', 'Write'), ('admin', 'Admin')], default='read', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'friends_users',
            },
        ),
        migrations.CreateModel(
            name='Blocks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('blocked', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_by', to=settings.AUTH_USER_MODEL)),
                ('blocker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocking', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Blocks',
            },
        ),
        migrations.CreateModel(
            name='Friends_Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_requests', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Friends_Request',
                'db_table': 'friends_request',
            },
        ),
        migrations.CreateModel(
            name='Friendships',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendships_user1', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendships_user2', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Friendships',
            },
        ),
        migrations.CreateModel(
            name='User_Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Users_Activities',
                'db_table': 'friends_users_activity',
            },
        ),
        migrations.AddIndex(
            model_name='user',
            index=django.contrib.postgres.indexes.GinIndex(fields=['first_name', 'last_name'], name='user_search_gin', opclasses=['gin_trgm_ops', 'gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='blocks',
            index=models.Index(fields=['blocker', 'blocked'], name='friends_blo_blocker_78c5dc_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='blocks',
            unique_together={('blocker', 'blocked')},
        ),
        migrations.AddIndex(
            model_name='friends_request',
            index=models.Index(fields=['receiver', 'status'], name='friends_req_receive_8908e9_idx'),
        ),
        migrations.AddIndex(
            model_name='friends_request',
            index=models.Index(fields=['sender', 'status'], name='friends_req_sender__1d1720_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='friends_request',
            unique_together={('sender', 'receiver')},
        ),
        migrations.AddIndex(
            model_name='friendships',
            index=models.Index(fields=['user1', 'user2'], name='friends_fri_user1_i_2dec15_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='friendships',
            unique_together={('user1', 'user2')},
        ),
    ]
