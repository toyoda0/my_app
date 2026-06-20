from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('regist/', views.regist, name='regist'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('index/', views.index, name='index'),
    path('info/', views.info, name='info'),
    path('request_password_reset/', views.request_password_reset, name='request_password_reset'),
    path('reset_password/<uuid:token>/', views.reset_password, name='reset_password'),
    #パスワード変更
    path('settings/password/', views.password_change, name='password_change'),
    #メールアドレス変更
    path('settings/email/', views.email_change, name='email_change'),
    #設定画面
    path('settings/', views.settings_home, name='settings_home'),
]
