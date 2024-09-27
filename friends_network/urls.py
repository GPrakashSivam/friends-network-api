from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView

urlpatterns = [
    # Swagger API UI
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('admin/', admin.site.urls),
    path('api/',include('friends.urls')),
]
