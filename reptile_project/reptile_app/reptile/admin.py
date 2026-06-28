from django.contrib import admin
from .models import Reptile, CareType, Record

#爬虫類(生体)の管理画面設定
@admin.register(Reptile)
class ReptileAdmin(admin.ModelAdmin):
    #管理画面の一覧でどの項目を表示するか
    list_display = ('name', 'species', 'user', 'created_at')
    #検索ボックスで探せる項目
    search_fields = ('name', 'species')
    #画面の右側に表示する絞り込みフィルター
    list_filter = ('sex', 'user')
    
#お世話の種類の管理画面設定
@admin.register(CareType)
class CareTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    
#お世話の記録の管理画面設定
@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('record_date', 'reptile', 'condition', 'created_at')
    list_filter = ('condition', 'reptile', 'record_date')


