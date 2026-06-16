from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Record, Reptile
from .forms import RecordForm
from django import forms
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
    
    #ログイン中のユーザーのペット一覧を取得
    user_reptiles = Reptile.objects.filter(owner=request.user)
    
    #画面(URLパラメータ)から選ばれたペットIDを取得
    #なければ1匹目のペットのIDをデフォルトに
    selected_pet_id = request.GET.get('pet_id')
    if not selected_pet_id and user_reptiles.exists():
        selected_pet_id = user_reptiles.first().id
        
    if selected_pet_id:
        #データベースから今月分のデータを取得してカレンダーの数字と合わせる処理
        #Recordから、表示したい年月、選んだペットに一致する記録をもってくる
        records = Record.objects.filter(
            record_date__year=current_year,
            record_date__month=current_month,
            reptile_id=selected_pet_id
        )
    else:
        #ペットが登録されていない場合は空にする
        records = Record.objects.none()
        
    
    #日付からレコードを探せるように辞書にする
    record_dict = {record.record_date.day: record for record in records}
    #お世話情報付きの1か月分のカレンダーデータの箱
    custom_month_days = []
    for week in month_days:
        week_date = []
        for day in week:
            #その日のレコードがあれば取得、ない日か0の日はNone
            day_record = record_dict.get(day) if day != 0 else None
            #日付の数字とレコードをひとまとめにした辞書
            day_info = {'day_num': day, 'record': day_record}
            #1日分のデータを週の箱に入れて並べる
            week_date.append(day_info)
        #7日分で週の箱ができたら月の箱に入れる
        custom_month_days.append(week_date)
    
    
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
        'month_days' : custom_month_days,
        'today' : today,
        'prev_year' : prev_year,
        'prev_month' : prev_month,
        'next_year' : next_year,
        'next_month' : next_month,
        'user_reptiles': user_reptiles,
        'selected_pet_id': int(selected_pet_id) if selected_pet_id else None,
    }
    return render(request, 'reptile/calendar_home.html', context)


#カレンダーの記録をもって飛んだお世話記録登録の処理
def record_add(request, year, month, day):
    #URLの数字を日付データに変換
    selected_date = datetime.date(year, month, day)
    
    #保存ボタンが押された時の処理
    if request.method == 'POST':
        form = RecordForm(request.POST, request.FILES)
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


class ReptileForm(forms.ModelForm):
    class Meta:
        model = Reptile
        #画面で入力する項目
        fields = ['name', 'species', 'morph', 'sex', 'birthday', 'adoption_date', 'memo']
        #カレンダー入力しやすいように日付の見た目を調整
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'adoption_date': forms.DateInput(attrs={'type': 'date'}),
            'memo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'メモ(最大500文字)'
            }),
        } 

#ログインユーザーを飼い主にして個体追加        
def reptile_add(request):
    if request.method == 'POST':
        form = ReptileForm(request.POST)
        if form.is_valid():
            reptile = form.save(commit=False)
            #ログインしているユーザーを飼い主にセット
            reptile.owner = request.user
            reptile.save()
            return redirect('calendar_home')
    else:
        form = ReptileForm()
        
    return render(request, 'reptile/reptile_form.html', {'form': form})


def reptile_list(request):
    #ログインしているユーザーが飼っているペットだけを一覧で取得
        reptiles = Reptile.objects.filter(owner=request.user)
        
        return render(request, 'reptile/reptile_list.html', {'reptiles': reptiles})
    
    
def reptile_detail(request, pk):
    # データベースから指定されたID（pk）のペットを1匹だけ取得。なければ404エラー（画面がありません）を返す
    reptile = get_object_or_404(Reptile, pk=pk, owner=request.user)
    # 性別の数字（0, 1, 2）を、モデルで定義した文字（不明, 男の子, 女の子）に変換する
    sex_display = reptile.get_sex_display()
    
    context = {
        'reptile': reptile,
        'sex_display': sex_display,
    }
    return render(request, 'reptile/reptile_detail.html', context)


#お世話記録の修正
def record_edit(request, pk):
    #URLから渡されたID(pk)を元に、編集したい過去の記録を1件取得
    record = get_object_or_404(Record, pk=pk)
    
    if request.method == "POST":
        #instance=record を渡すことで「新規登録」ではなく「上書き保存」にする
        form = RecordForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            return redirect('calendar_home')
    else:
        #過去のデータが最初から入った状態のフォームを作る
        form = RecordForm(instance=record)
        
    return render(request, 'record_edit.html', {'form': form, 'record':record})