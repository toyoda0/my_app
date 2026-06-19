from django.urls import path
from .import views

urlpatterns = [
    #カレンダー画面
    path('calendar_home/', views.calendar_home, name='calendar_home'),
    #特定の年月を指定されたらそのカレンダーを出す(矢印押したとき)
    path('calendar/<int:year>/<int:month>/', views.calendar_home, name='calendar_move'),
    #カレンダーから日付を引っ張ってくる用のURL
    path('record/add/<int:year>-<int:month>-<int:day>/', views.record_add, name='record_add_with_date'),
    #新しいペットの登録
    path('reptile/add/', views.reptile_add, name='reptile_add'),
    #ペット一覧
    path('reptiles/', views.reptile_list, name='reptile_list'),
    #ペット詳細
    path('reptile/<int:pk>', views.reptile_detail, name='reptile_detail'),
    #お世話編集
    path('record/edit/<int:record_id>/', views.record_edit, name='record_edit'),
    #お世話削除
    path('record/<int:record_id>/delete/', views.record_delete, name='record_delete'),
]
