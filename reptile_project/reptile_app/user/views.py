from django.shortcuts import render, redirect
from.forms import UserForm, UserLoginForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,  login, logout
from django.contrib.auth.decorators import login_required

def regist(request):
    user_form = UserForm(request.POST or None)
    if user_form.is_valid():
        user = user_form.save(commit=False)
        password = user_form.cleaned_data.get('password', '')
        try:
            validate_password(password)
        except ValidationError as e:
            user_form.add_error('password', e)
            return render(request, 'user/registration.html', context={
                'user_form' : user_form,
            })
        user.set_password(password)
        user.save()
    return render(request, 'user/registration.html', context={
        'user_form' : user_form,
    })

def login_view(request):
    login_form = UserLoginForm(request.POST or None)
    next_url = request.GET.get('next')
    if login_form.is_valid():
        username = login_form.cleaned_data.get('username')
        password = login_form.cleaned_data.get('password1')
        #認証処理(成功したらuserが返される)
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_authenticated:
            login(request, user)#ログイン処理
            redirect_url = next_url if next_url else 'user:index'
            return redirect(redirect_url)
        else:
            login_form.add_error('username', '認証に失敗しました')
    return render(request, 'user/login.html', context={
        'login_form': login_form,
    })
    
def index(request):
    print(request.user)
    return render(request, 'user/index.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('user:login')

@login_required
def info(request):
    return render(request, 'user/info.html')