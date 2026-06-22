import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

class Reptile(models.Model):
    
    class SexChoices(models.IntegerChoices):
        UNKNOWN = 0, '不明'
        MALE = 1, '男の子'
        FEMALE = 2, '女の子'
        
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reptiles'
    )
    name = models.CharField(max_length=100, verbose_name='名前')
    species = models.CharField(max_length=100, verbose_name='種類')
    morph = models.CharField(max_length=100, blank=True, verbose_name='モルフ')
    sex = models.IntegerField(
        choices = SexChoices.choices,
        default=SexChoices.UNKNOWN,
        verbose_name='性別'
    )
    birthday = models.DateField(null=True, blank=True, verbose_name='誕生日')
    adoption_date = models.DateField(null=True, blank=True, verbose_name='お迎え日')
    record_end_date = models.DateField(null=True, blank=True, verbose_name='お別れ日')
    memo = models.CharField(max_length=500, null=True, blank=True, verbose_name='メモ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) #更新日時
    
    class Meta:
        db_table = 'reptiles'
        verbose_name_plural = '爬虫類'
    
    def __str__(self):
        return self.name


class CareType(models.Model):
    name = models.CharField(max_length=50, verbose_name='お世話の名前')
    
    class Meta:
        db_table = 'care_types'
        verbose_name = 'お世話の種類'
        verbose_name_plural = 'お世話の種類'
        
    def __str__(self):
        return self.name
    

class Record(models.Model):
    CONDITION_CHOICES = [
        (0, '元気'),
        (1, '普通'),
        (2, '元気がない'),
    ]
    FECES_CHOICES = [(0, '異常'), (1, '正常')]
    BINARY_CHOICES = [(0, 'No'), (1, 'Yes')]
    
    reptile = models.ForeignKey(Reptile, on_delete=models.CASCADE, related_name='records')
    record_date = models.DateField(verbose_name='記録日')
    condition = models.IntegerField(choices=CONDITION_CHOICES, default=1, verbose_name='元気')
    weight = models.FloatField(null=True, blank=True, verbose_name='体重(g)')
    length = models.FloatField(null=True, blank=True, verbose_name='体長(cm)')
    feeding = models.IntegerField(choices=BINARY_CHOICES, null=True, blank=True, verbose_name='給餌')
    food_type_memo = models.CharField(max_length=100, blank=True, verbose_name='餌の種類')
    feces = models.IntegerField(choices=FECES_CHOICES, null=True, blank=True, verbose_name='フン')
    shedding = models.IntegerField(choices=BINARY_CHOICES, null=True, blank=True, verbose_name='脱皮')
    
    care_types = models.ManyToManyField(
        CareType,
        blank=True,
        related_name='records',
        verbose_name='本日のお世話内容'
    )
    image = models.ImageField(upload_to='records/%y/%m/%d/', null=True, blank=True, verbose_name='写真')
    memo = models.CharField(max_length=500, blank=True, verbose_name='メモ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    
    class Meta:
        db_table = 'records'
        verbose_name_plural = '飼育記録'
    
    def __str__(self):
        return f"{self.record_date} - {self.reptile.name}"


User = get_user_model()

#招待リンク状態を管理する
class ReptileInvite(models.Model):
    #誰が招待URLを作ったか
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    #URLの末尾につけるランダム文字列
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    #発行日時
    created_at = models.DateTimeField(auto_now_add=True)
    #使用済みフラグ
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'invitations'
    
    def __str__(self):
        return f"{self.inviter.email}の招待トークン"


#確定した共有関係を管理する
class UserShare(models.Model):
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares_as_owner')
    shared_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares_as_guest')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_shares'
        
    def __str__(self):
        return f"{self.owner_user.email}"