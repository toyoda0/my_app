from django.db import models
from django.conf import settings

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
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    molph = models.CharField(max_length=100)
    sex = models.IntegerField(
        choices = SexChoices.choices,
        default=SexChoices.UNKNOWN
    )
    birthday = models.DateField(null=True, blank=True)
    adoption_date = models.DateField(null=True, blank=True) #お迎え日
    record_end_date = models.DateField(null=True, blank=True) #お別れ日
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) #更新日時
    
    def __str__(self):
        return self.name
    

class Record(models.Model):
    CONDITION_CHOICES = [(0, '良い'), (1, '普通'), (2, '悪い')]
    FECES_CHOICES = [(0, '異常'), (1, '正常')]
    BINARY_CHOICES = [(0, 'No'), (1, 'Yes')]
    
    reptile = models.ForeignKey(Reptile, on_delete=models.CASCADE, related_name='records')
    record_date = models.DateField(verbose_name='記録日')
    condition = models.IntegerField(choices=CONDITION_CHOICES, default=1)
    weight = models.FloatField(null=True, blank=True)
    length = models.FloatField(null=True, blank=True)
    feeding = models.IntegerField
    food_type_memo = models.CharField(max_length=100, blank=True)
    feces = models.IntegerField(choices=FECES_CHOICES, default=1)
    shedding = models.IntegerField(choices=BINARY_CHOICES, default=0)
    image = models.ImageField(upload_to='records/', null=True, blank=True, verbose_name='写真')
    memo = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return f"{self.record_date} - {self.reptile.name}"
