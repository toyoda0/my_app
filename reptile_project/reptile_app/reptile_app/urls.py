# reptile_app/urls.py の中身
from django.contrib import admin
from django.urls import path, include
from portfolio import views as portfolio_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    #「/」にアクセスが来たらポートフォリオ画面を出す設定
    path('', portfolio_views.portfolio_home, name='portfolio_home'),

    #「/Reptinote/〜」にアクセスが来たらマイアプリを動かす設定
    path('Reptinote/', include('reptile.urls', namespace='reptile')), 
    path('Reptinote/user/', include('user.urls')), 
]



#DEBUG が True のとき
if settings.DEBUG:
    #/media/ へのアクセスが来たらどのフォルダを見ればいいか教える
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )