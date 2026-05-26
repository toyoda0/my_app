from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Record
from .forms import RecordForm
import datetime, calendar

def calendar_home(request, year=None, month=None):
    #ログイン後に最初に表示されるカレンダー画面
    today = datetime.date.today()
    
    #URLに年と月が送られてきていたらそれを使い、なければ今月にする
    if year and month:
        current_year = int(year)
        current_month = int(month)
    else:
        current_year = today.year
        current_month = today.month
    
    #日曜始まりのカレンダーにする
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(current_year, current_month)
    
    #◀を押したときの先月を計算
    if current_month == 1:
        prev_year = current_year -1
        prev_month = 12
    else:
        prev_year = current_year
        prev_month = current_month -1
    
    #▶を押したときの次月を計算
    if current_month == 12:
        next_year = current_year +1
        next_month = 1
    else:
        next_year = current_year
        next_month = current_month +1
    
    #HTMLにもっていくデータ
    context = {
        'year' : current_year,
        'month' : current_month,
        'month_days' : month_days,
        'today' : today,
        'prev_year' : prev_year,
        'prev_month' : prev_month,
        'next_year' : next_year,
        'next_month' : next_month,
    }
    return render(request, 'reptile/calendar_home.html', context)


#カレンダーの記録をもって飛んだお世話記録登録画面
def record_add(request, year, month, day):
    #URLの数字を日付データに変換
    selected_date = datetime.date(year, month, day)
    
    #保存ボタンが押された時の処理
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            #保存する前に日付を上書きしたいからデータベースへの保存はしないで
            record = form.save(commit=False)
            #URLから取得した日付をセット(最優先)
            record.record_date = selected_date
            record.save()
            
            #多対多(ManyToMany)のデータを保存するための決まり文句
            form.save_m2m()
            
            return redirect('calendar_home') #保存したらカレンダー画面に戻る
        else:
            #最初に画面を表示しただけの時の処理
            form = RecordForm(initial={'record_date': selected_date})
            
        return render(request, 'reptile/record_form.html', {'form': form, 'selected_date': selected_date})
       