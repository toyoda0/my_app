from django.db import models
from django.contrib.auth.models import(
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.conf import settings
import uuid

#ユーザーを新規登録
class UserManager(BaseUserManager):
    
    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('メールアドレスは必須です')
        if not username:
            raise ValueError('ユーザー名は必須です')
        if not password:
            raise ValueError('パスワードは必須です')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_active'] = True
        extra_fields['is_superuser'] = True
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    
    username = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email' #ログインする時のIDはemail
    REQUIRED_FIELDS = ['username'] #createsuperuserの時に入力を求められる
    
    #管理画面でIDじゃなくてemailで一覧表示する
    def __str__(self):
        return self.email
    

#パスワード再発行
class PasswordResetToken(models.Model):
    #ユーザー1人に対してトークンは1つだけ
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  #Userから変更　参照先を設定依存
        on_delete=models.CASCADE,
        related_name='password_reset_token',
    )
    token = models.UUIDField(default=uuid.uuid4, db_index=True)
    used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name_plural = 'パスワードリセットトークン'
