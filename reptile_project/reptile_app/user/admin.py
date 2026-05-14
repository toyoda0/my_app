from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import UserCreationForm, UserChangeForm


User = get_user_model()

class CustomizeUserAdmin(UserAdmin):
    form = UserChangeForm #編集画面
    add_form = UserCreationForm #ユーザー作成画面
    #一覧で表示するフィールド
    list_display = ('username', 'email', 'is_staff')
    
    fieldsets = (
        ('ユーザー情報', {
                'fields': ('username', 'email', 'password', 'website', 'picture')
            }),
        ('パーミッション', {'fields': ('is_staff', 'is_active', 'is_superuser')})
    )
    
    add_fieldsets = (
        (
            'ユーザー情報',{
                'fields':('username', 'email', 'password1', 'password2')
            }
            
        ),
    )

admin.site.register(User, CustomizeUserAdmin)