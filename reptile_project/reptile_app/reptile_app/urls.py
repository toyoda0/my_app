from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reptile.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('user/', include('user.urls')),
]