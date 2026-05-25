from django.urls import path
from .import views

urlpatterns = [
    #カレンダー画面のURLは後で作成すること
    path('', views.calendar_home, name='calendar_home'),
    #カレンダーから日付を引っ張ってくる用のURL
    path('record/add/<int:year>-<int:month>-<int:day>/', views.record_add, name='record_add_with_date'),
]
