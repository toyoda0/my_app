from django.shortcuts import render, redirect, get_object_or_404
from .models import Record, Reptile, ReptileInvite, UserShare
from .forms import RecordForm
from django import forms
import datetime, calendar
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q

#カレンダー画面
@login_required
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
    
    #自分が共有してもらっている相手（オーナー）のIDリストを取得
    shared_owner_ids = UserShare.objects.filter(shared_user=request.user).values_list('owner_user_id', flat=True)
    
    #自分のペット、または共有されたペットをまとめて取得
    user_reptiles = Reptile.objects.filter(
        Q(user=request.user) | Q(user_id__in=shared_owner_ids)
    ).distinct()
    
    #デフォルトで表示するペット（1匹目）の選び方
    selected_pet_id = request.GET.get('pet_id')
    if not selected_pet_id and user_reptiles.exists():
        #自分がゲストなら「共有されたペット」を選ぶ
        shared_reptiles = user_reptiles.filter(user_id__in=shared_owner_ids)
        if shared_reptiles.exists():
            selected_pet_id = shared_reptiles.first().id
        else:
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
@login_required
def record_add(request, year, month, day):
    #URLの数字を日付データに変換
    selected_date = datetime.date(year, month, day)
    
    #保存ボタンが押された時の処理
    if request.method == 'POST':
        form = RecordForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            #保存する前に日付を上書きしたいからデータベースへの保存はしないで
            record = form.save(commit=False)
            weight = form.cleaned_data.get('weight')
            length = form.cleaned_data.get('length')
            #もし「体重がマイナス」または「体長がマイナス」だったら
            if (weight is not None and weight < 0) or (length is not None and length < 0):
                messages.error(request, "体重または体長にマイナスの値は入力できません。")
                #保存処理に進まず、エラーメッセージを持たせたまま登録画面をもう一度表示
                return render(request, 'reptile/record_form.html', {'form': form, 'selected_date': selected_date})
            form.save(commit=True)
            
            return redirect('reptile:calendar_home') #保存したらカレンダー画面に戻る
    else:        
        #URLの後ろについている「?pet_id=〇〇」からペットのIDを取得する
        chosen_pet_id = request.GET.get('pet_id')
        
        #初期値の入れ物（辞書）を作成 日付を初期値で表示させる
        initial_data = {'record_date': selected_date}
        
        #カレンダーでペットが選ばれていたら、フォームの初期値（reptile）にも追加する
        if chosen_pet_id:
            initial_data['reptile'] = chosen_pet_id
            
        #準備した初期値をformに渡す
        form = RecordForm(initial=initial_data, user=request.user)
            
    return render(request, 'reptile/record_form.html', {'form': form, 'selected_date': selected_date})


#ペット登録
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
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #instance.pk がある（＝データベースに既に保存されているデータを編集している）場合
        if self.instance and self.instance.pk:
            #おわかれ日の入力欄をメモの上に追加
            self.fields['record_end_date'] = forms.DateField(
                label='おわかれ日',
                required=False,
                widget=forms.DateInput(attrs={'type': 'date'})
            )
            
            #画面の並び順を再調整
            field_order = ['name', 'species', 'morph', 'sex', 'birthday', 'adoption_date', 'record_end_date', 'memo']
            self.order_fields(field_order)

#ログインユーザーを飼い主にして個体追加
@login_required
def reptile_add(request):
    if request.method == 'POST':
        form = ReptileForm(request.POST)
        if form.is_valid():
            reptile = form.save(commit=False)
            #ログインしているユーザーを飼い主にセット
            reptile.user = request.user
            reptile.save()
            return redirect('reptile:reptile_list')
    else:
        form = ReptileForm()
        
    return render(request, 'reptile/reptile_form.html', {'form': form})


#ペット一覧
@login_required
def reptile_list(request):
    # 自分がゲスト（共有されている側）の場合のオーナーIDリストを取得
    shared_owner_ids = UserShare.objects.filter(shared_user=request.user).values_list('owner_user_id', flat=True)
    
    # 「自分のペット」または「共有されたオーナーのペット」をまとめて取得
    reptiles = Reptile.objects.filter(
        Q(user=request.user) | Q(user_id__in=shared_owner_ids)
    ).distinct()
    
    return render(request, 'reptile/reptile_list.html', {'reptiles': reptiles})
    

#ペット詳細
@login_required    
def reptile_detail(request, record_id):
    #自分がゲストの場合のオーナーIDリスト
    shared_owner_ids = UserShare.objects.filter(shared_user=request.user).values_list('owner_user_id', flat=True)
    
    #自分が飼い主(user)か、または共有してくれたオーナー(user_id__in)のペットなら取得OKにする
    reptile = get_object_or_404(
        Reptile,
        Q(id=record_id) & (Q(user=request.user) | Q(user_id__in=shared_owner_ids))
    )
    
    #性別の数字（0, 1, 2）を、モデルで定義した文字（不明, 男の子, 女の子）に変換する
    sex_display = reptile.get_sex_display()
    
    context = {
        'reptile': reptile,
        'sex_display': sex_display,
    }
    return render(request, 'reptile/reptile_detail.html', context)


#お世話記録の修正
@login_required
def record_edit(request, record_id):
    # 自分がゲストの場合のオーナーIDリスト
    shared_owner_ids = UserShare.objects.filter(shared_user=request.user).values_list('owner_user_id', flat=True)
    
    #記録のペットの飼い主が、自分または共有オーナーなら編集OKにする
    record = get_object_or_404(
        Record, 
        Q(id=record_id) & (Q(reptile__user=request.user) | Q(reptile__user_id__in=shared_owner_ids))
    )
    
    if request.method == "POST":
        #instance=record を渡すことで「新規登録」ではなく「上書き保存」にする
        form = RecordForm(request.POST, request.FILES, instance=record, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('reptile:calendar_home')
    else:
        #過去のデータが最初から入った状態のフォームを作る
        form = RecordForm(instance=record)
        
    return render(request, 'reptile/record_edit.html', {'form': form, 'record':record})


#お世話記録の削除
@login_required
def record_delete(request, record_id):
    # 自分がゲストの場合のオーナーIDリスト
    shared_owner_ids = UserShare.objects.filter(shared_user=request.user).values_list('owner_user_id', flat=True)
    
    #記録のペットの飼い主が、自分または共有オーナーなら安全に削除できるようにガード
    record = get_object_or_404(
        Record,
        Q(id=record_id) & (Q(reptile__user=request.user) | Q(reptile__user_id__in=shared_owner_ids))
    )
    
    if request.method == 'POST':
        record.delete()
        return redirect('reptile:calendar_home')
    
    # 安全のためPOST以外（直リンクなど）でのアクセスは編集画面に戻す
    return redirect('reptile:record_edit', record_id=record_id)


#ペットの詳細編集
@login_required
def reptile_edit(request, record_id):
    #自分がゲストの場合のオーナーIDリスト
    shared_owner_ids = UserShare.objects.filter(shared_user=request.user).values_list('owner_user_id', flat=True)
    
    #他人に勝手に編集されないよう、自分または共有オーナーのペットのみ安全に取得
    reptile = get_object_or_404(
        Reptile,
        Q(id=record_id) & (Q(user=request.user) | Q(user_id__in=shared_owner_ids))
    )
    
    if request.method == 'POST':
        #instance=reptileを渡して既存データの上書き保存
        form = ReptileForm(request.POST, instance=reptile)
        if form.is_valid():
            form.save()
            #編集が終わったら、そのペットの詳細画面に戻す
            return redirect('reptile:reptile_detail', record_id=reptile.id)
    else:
        #過去のデータが最初から入った状態のフォームを作る
        form = ReptileForm(instance=reptile)
        
    context = {
        'form': form,
        'reptile': reptile,
    }
    return render(request, 'reptile/reptile_edit.html', context)


#ペットの削除
@login_required
def reptile_delete(request, record_id):
    #他人(ゲストも)のペットを削除できないようにuser=request.user
    reptile = get_object_or_404(Reptile, id=record_id, user=request.user)
    
    #削除ボタンが押された時のみ削除を実行
    if request.method == 'POST':
        reptile.delete()
        return redirect('reptile:reptile_list')
    
    #直接(GET)でアクセスされた場合は編集画面に戻す
    return redirect('reptile:reptile_list')


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
        scheme = request.scheme #通信の接続方式
        generated_url = f"{scheme}://{current_host}/Reptinote/share/accept/{invite.token}/"
        
    context = {
        'generated_url': generated_url
    }
    return render(request, 'reptile/invite_url_add.html', context)


#共有しているメンバー一覧
@login_required
def member_list(request):
    #自分がオーナー、または自分がゲストのデータを両方取得
    shared_members = UserShare.objects.filter(
        Q(owner_user=request.user) | Q(shared_user=request.user)
    )
    
    context = {
        'shared_members': shared_members
    }
    return render(request, 'reptile/member_list.html', context)


#共有解除
@login_required
def share_delete(request, share_id):
    if request.method == 'POST':
        #自分がオーナーのデータのみ削除可能
        share = get_object_or_404(UserShare, id=share_id, owner_user=request.user)
        share.delete()
    return redirect('reptile:member_list')


#招待URLを踏んだユーザーを user_shares に登録
def invite_accept(request, token):
    
    #有効なトークンかチェック（使用済みや存在しない場合は404）
    invite = get_object_or_404(ReptileInvite, token=token, used_at__isnull=True)
    inviter = invite.inviter
    
    #ログインしていない場合は、トークンを持たせて登録・ログイン画面へ
    if not request.user.is_authenticated:
        return redirect(f'/Reptinote/user/regist/?token={token}')
    
    #自分のURLなら何もせずカレンダーへ戻す
    if inviter == request.user:
        return redirect('reptile:calendar_home')
    
    #user_shares テーブルにデータを1件作ってグループを繋ぐ
    UserShare.objects.get_or_create(
        owner_user=inviter,
        shared_user=request.user
    )
    
    #招待リンクを使用済みにする
    invite.used_at = timezone.now()
    invite.save()
    
    #登録が完了したらカレンダーへ
    return redirect('reptile:calendar_home')
