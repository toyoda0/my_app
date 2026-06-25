from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

User = get_user_model()

#ユーザー新規登録用のフォーム    
class UserCreationForm(forms.ModelForm):
    confirm_password = forms.CharField(
        label='パスワード再入力', widget=forms.PasswordInput()
    )
    
    password = forms.CharField(
        label='パスワード', widget=forms.PasswordInput()
    )
    
    class Meta:
        model = User
        fields = ('username', 'email')
        labels = {
            'username': '名前',
            'email': 'メールアドレス',
            'password': 'パスワード'
        }
        widgets = {
            'password': forms.PasswordInput()
        }
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # 2つのパスワードが一致しているかチェック
        if password != confirm_password:
            raise ValidationError('パスワードが一致しません')
        
        # Djangoの強力なパスワード安全基準（8文字以上など）に合格するかチェック→いるか要確認
        try:
            if password:
                validate_password(password, self.instance)
        except ValidationError as e:
            self.add_error('password', e)
            
        return cleaned_data
        
    def save(self, commit=True):
        user = super().save(commit=False)
        # 入力されたパスワードをハッシュ（暗号化）して保存する
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

#ユーザー編集用のフォーム    
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label='パスワード')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_active', 'is_staff', 'is_superuser')
        
    def clean_password(self):
        return self.instance.password

#ログイン用フォーム
class UserLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', max_length=50, widget=forms.PasswordInput())

#パスワード再設定用フォーム
class RequestPasswordResetForm(forms.Form):
    email = forms.EmailField(label='メールアドレス', widget=forms.EmailInput())
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError('このメールアドレスのユーザーは存在しません')
        return email
    
    
class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(
        label='新しいパスワード',
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label='新しいパスワード(確認)',
        widget=forms.PasswordInput,
    )
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('パスワードが一致しません')
        else:
            raise ValidationError('パスワードを設定してください')
        return cleaned_data


#メールアドレス変更(ログイン済で変更用)
class EmailChangeForm(forms.Form):
    current_email = forms.EmailField(label='現在のメールアドレス', required=True)
    new_email1 = forms.EmailField(label='新しいメールアドレス', required=True)
    new_email2 = forms.EmailField(label='メールアドレス再入力', required=True)
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        #現在のメールアドレスを初期値にする
        self.fields['current_email'].initial = user.email
        self.fields['current_email'].widget.attrs['readonly'] = True #編集不可にする
        
    def clean_current_email(self):
        current_email = self.cleaned_data.get('current_email')
        if current_email != self.user.email:
            raise forms.ValidationError("現在のメールアドレスが一致しません。")
        return current_email
    
    def clean(self):
        cleaned_data = super().clean()
        new_email1 = cleaned_data.get('new_email1')
        new_email2 = cleaned_data.get('new_email2')
        
        #新しいアドレス同士が一致しているかチェック
        if new_email1 and new_email2 and new_email1 != new_email2:
            raise forms.ValidationError("新しいメールアドレスが一致しません。")
        
        #すでに使われているメールアドレスじゃないかチェック
        if new_email1 and User.objects.filter(email=new_email1).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("このメールアドレスはすでに登録されています。")
        
        return cleaned_data