from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reptile.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('user/', include('user.urls')),
]


#DEBUG が True のとき
if settings.DEBUG:
    #/media/ へのアクセスが来たらどのフォルダを見ればいいか教える
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )