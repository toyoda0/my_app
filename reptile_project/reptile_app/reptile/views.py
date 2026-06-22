from django.shortcuts import render, redirect, get_object_or_404
from .models import Record, Reptile, ReptileInvite, UserShare
from .forms import RecordForm
from django import forms
import datetime, calendar
from django.contrib.auth.decorators import login_required
from django.utils import timezone


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
@login_required
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


@login_required
def reptile_list(request):
    #ログインしているユーザーが飼っているペットだけを一覧で取得
        reptiles = Reptile.objects.filter(owner=request.user)
        
        return render(request, 'reptile/reptile_list.html', {'reptiles': reptiles})
    

@login_required    
def reptile_detail(request, record_id):
    # データベースから指定されたID（pk）のペットを1匹だけ取得。なければ404エラー（画面がありません）を返す
    reptile = get_object_or_404(Reptile, id=record_id, owner=request.user)
    # 性別の数字（0, 1, 2）を、モデルで定義した文字（不明, 男の子, 女の子）に変換する
    sex_display = reptile.get_sex_display()
    
    context = {
        'reptile': reptile,
        'sex_display': sex_display,
    }
    return render(request, 'reptile/reptile_detail.html', context)


#お世話記録の修正
def record_edit(request, record_id):
    #URLから渡されたIDと、ログインユーザーを元に、過去の記録を1件取得
    #get_object_or_404を使うことで、存在しないIDや他人の記録だったら自動で404エラーにする
    #Recordからreptileを辿って、その先のownerが今のログインユーザー（request.user）
    record = get_object_or_404(Record, id=record_id, reptile__owner=request.user)
    
    if request.method == "POST":
        #instance=record を渡すことで「新規登録」ではなく「上書き保存」にする
        form = RecordForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            return redirect('calendar_home')
    else:
        #過去のデータが最初から入った状態のフォームを作る
        form = RecordForm(instance=record)
        
    return render(request, 'reptile/record_edit.html', {'form': form, 'record':record})


#お世話記録の削除
def record_delete(request, record_id):
    #該当のお世話記録を取得（なければ404エラー）
    record = get_object_or_404(Record, id=record_id)
    
    if request.method == 'POST':
        record.delete()
        return redirect('calendar_home')
    
    # 安全のためPOST以外（直リンクなど）でのアクセスは編集画面に戻す
    return redirect('record_edit', record_id=record_id)


#ペットの詳細編集
def reptile_edit(request, record_id):
    #他人に勝手に編集されないよう、owner=request.user も含めて安全に取得
    reptile = get_object_or_404(Reptile, id=record_id, owner=request.user)
    
    if request.method == 'POST':
        #instance=reptileを渡して既存データの上書き保存
        form = ReptileForm(request.POST, instance=reptile)
        if form.is_valid():
            form.save()
            #編集が終わったら、そのペットの詳細画面に戻す
            return redirect('reptile_detail', record_id=reptile.id)
    else:
        #過去のデータが最初から入った状態のフォームを作る
        form = ReptileForm(instance=reptile)
        
    context = {
        'form': form,
        'reptile': reptile,
    }
    return render(request, 'reptile/reptile_edit.html', context)


#招待用URL発行
@login_required
def invite_url_add(request):
    #画面を最初に開いた（まだ作成ボタンを押していない）ときは、URLが存在しないのでNone
    generated_url = None
    
    if request.method == 'POST':
        #ReptileInvite モデルを使って、新しいデータをデータベースに1件登録（create）
        #inviter=request.user：いまログインしてボタンを押したユーザーを招待した人として記録
        invite = ReptileInvite.objects.create(inviter=request.user)
        current_host = request.get_host()
        scheme = request.scheme
        generated_url = f"{scheme}://{current_host}/share/accept/{invite.token}/"
        
    context = {
        'generated_url': generated_url
    }
    return render(request, 'reptile/invite_url_add.html', context)


#共有しているメンバー一覧
@login_required
def member_list(request):
    return render(request, 'reptile/member_list.html', {})


#招待URLを踏んだユーザーを user_shares に登録
@login_required
def invite_accept(request, token):
    
    # データベースからまだ使われていないトークンを探す
    invite = get_object_or_404(ReptileInvite, token=token, used_at__isnull=True)
    inviter = invite.inviter
    
    # 自分のURLなら何もせずカレンダーへ戻す
    if inviter == request.user:
        return redirect('calendar_home')
    
    if request.method == 'POST':
        #user_shares テーブルにデータを1件作ってグループを繋ぐ
        UserShare.objects.get_or_create(
            owner_user=inviter,
            shared_user=request.user
        )
        
        #招待リンクを使用済みにする
        invite.used_at = timezone.now()
        invite.save()
        
        return redirect('calendar_home')
    
    context = {
        'inviter': inviter,
    }
    return render(request, 'reptile/invite_accept.html', context)