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