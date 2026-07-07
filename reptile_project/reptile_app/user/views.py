from django.shortcuts import render, redirect, get_object_or_404
from .import forms
from .models import PasswordResetToken
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone
from reptile.models import ReptileInvite, UserShare
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .forms import EmailChangeForm
from django.core.mail import send_mail



User = get_user_model()

#ユーザー一覧画面
def user_list(request):
    return render(
        request, 'user/user_list.html'
    )

#新規登録処理
def regist(request):
    
    #URLの「?token=xxxx」をキャッチする
    token = request.GET.get('token')
    
    user_form = forms.UserCreationForm(request.POST or None)
    if user_form.is_valid():
        # データベースに暗号化保存（新しく登録されたユーザーを取得）
        user = user_form.save()
        
        #もし招待トークンを持って登録画面に来ていた場合は自動共有
        if token:
            invite = ReptileInvite.objects.filter(token=token, used_at__isnull=True).first()
            if invite and invite.inviter != user:
                #自動でUserShareにレコードを作る
                UserShare.objects.get_or_create(
                    owner_user=invite.inviter,
                    shared_user=user
                )
                #招待リンクを使用済みにする
                invite.used_at = timezone.now()
                invite.save()        
         
        #入力された生のパスワードをフォームから取得
        raw_password = user_form.cleaned_data.get('password')
        
        #カスタムユーザーに合わせて email と raw_password で一度正しく認証する
        auth_user = authenticate(request, username=user.email, password=raw_password)
        
        #認証が成功したら、その認証済みユーザーでログインする
        if auth_user is not None:
            login(request, auth_user)
        else:
            #認証バックエンドを指定してログイン
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
        #ブラウザにログインセッションのCookieを書き込ませる
        request.session.save()
                
        #登録＆自動ログイン＆共有が完了したので、そのまま相手のペットカレンダーへ
        return redirect('reptile:calendar_home')
    
    #もし登録に失敗していたら、ターミナルに表示する
    if request.method == 'POST':
        print("フォームのバリデーションに失敗しました")
        print("エラー内容:", user_form.errors)
        
    #登録画面を表示（HTML側にtokenを渡しておく）
    return render(request, 'user/registration.html', context={
        'user_form': user_form,
        'token': token
    })
        
        

#ログイン処理
def login_view(request):
    login_form = forms.UserLoginForm(request.POST or None)
    next_url = request.GET.get('next')
    
    if login_form.is_valid():
        email = login_form.cleaned_data.get('email')
        password = login_form.cleaned_data.get('password')
        # メールとパスワードをデータベースと照合（成功したらuserが返される）
        user = authenticate(request, username=email, password=password)
        #アカウントが有効な状態ならログインを通す
        if user is not None:
            login(request, user)# ログイン処理
            redirect_url = next_url if next_url else 'reptile:calendar_home'
            return redirect(redirect_url)
        else:
            # エラーメッセージをメールアドレスの欄に出す
            login_form.add_error('email', 'メールアドレスまたはパスワードが間違っています')
            
    return render(request, 'user/login.html', context={
        'login_form': login_form
    })

#アプリのトップページ
def index(request):
    print(request.user)
    return render(request, 'user/index.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('user:login')


#パスワードリセットの処理
def request_password_reset(request):
    form = forms.RequestPasswordResetForm(request.POST or None)
    message = ''
    #入力されたメールアドレスを持つユーザーをデータベースから探す。いなければ404エラー
    if form.is_valid():
        email = form.cleaned_data['email']
        user = get_object_or_404(User, email=email)
        # 新しいトークンを作成、既存なら取得
        password_reset_token, created = PasswordResetToken.objects.get_or_create(user=user)
        
        #新規（created）既存どちらでも、常に新しいUUIDを発行して保存
        password_reset_token.token = uuid.uuid4()
        password_reset_token.used = False
        password_reset_token.save()
            
        #パスワード更新されるまで一時的にアカウント凍結
        user.is_active = False
        user.save()
        token = password_reset_token.token
        
        #復活URLの組み立て
        reset_url = f"{request.scheme}://{request.get_host()}/Reptinote/user/reset_password/{token}/"
        
        #メールを送信する
        subject = "【Reptinote】パスワード再設定URLのご案内"
        mail_message = f"以下のURLからパスワードの再設定を行ってください。\n\n{reset_url}"
        from_email = None  # settings.pyのDEFAULT_FROM_EMAILが自動で使われます
        recipient_list = [email]  # ユーザーが入力したアドレス宛てに送る
        
        #メール送信を実行
        send_mail(subject, mail_message, from_email, recipient_list)
        
        message = 'パスワードリセットトークンをお送りしました'
        return redirect('user:password_reset_done')
    
    #最初に画面を開いた（GET）とき、またはエラーがあるときは元の入力画面を出す    
    return render(request, 'user/password_reset_form.html', context={
        'reset_form': form, 'message': message,
    })

#復活URLからの新パスワード入力
def reset_password(request, token):
    password_reset_token = get_object_or_404(
        PasswordResetToken,
        token=token,
        used=False,
    )
    form = forms.SetNewPasswordForm(request.POST or None)
    message = ''
    if form.is_valid():
        user = password_reset_token.user
        password = form.cleaned_data['password1']
        validate_password(password)
        # パスワード更新
        user.set_password(password)
        user.is_active = True
        user.save()
        
        password_reset_token.used = True #URLは1回だけ使用可能
        password_reset_token.save()
        message = '新しいパスワードを設定しました。下のボタンよりログイン画面へ戻り、新しいパスワードでログインしてください。'
    
    return render(request,'user/password_reset_confirm.html', context={
        'form': form, 'message': message,
    })


#設定画面
@login_required
def settings_home(request):
    return render(request, 'user/settings_home.html')


#パスワード変更（ログイン済で変更用）
def password_change(request):
    #Django標準のフォームに、いまログインしているユーザー（request.user）を紐付ける
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            #パスワードを上書き保存
            user = form.save()
            
            #パスワード変更後にログイン状態が切れるのを防ぐ
            update_session_auth_hash(request, user)
            
            #次の画面（設定画面）に1回だけ表示する完了メッセージを登録
            messages.success(request, 'パスワードを変更しました。')
            
            #設定トップ画面へリダイレクト
            return redirect('user:settings_home')
            
    # フォームに不備がある、または最初に画面を開いた（GET）ときは画面を表示
    return render(request, 'user/password_change.html', {'form': form})


#メールアドレス変更（ログイン済で変更用）
@login_required
def email_change(request):
    #フォームに「ログイン中のユーザー情報（user=request.user）」を渡して初期化
    form = EmailChangeForm(user=request.user, data=request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            #新しいメールアドレスをユーザーモデルに保存
            user = request.user
            user.email = form.cleaned_data.get('new_email1')
            user.save()
            
            #メッセージを登録
            messages.success(request, 'メールアドレスを変更しました。')
            
            return redirect('user:settings_home')
        
    return render(request, 'user/email_change.html', {'form': form})


#パスワード再設定メール送付完了
def password_reset_done(request):
    return render(request, 'user/password_reset_done.html')