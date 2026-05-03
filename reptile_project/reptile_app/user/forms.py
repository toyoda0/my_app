from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserForm(forms.ModelForm):
    
    class Meta():
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            'password': forms.PasswordInput
        }
        
class UserLoginForm(forms.Form):
    username = forms.CharField(label='ユーザー名', max_length=255)
    password1 = forms.CharField(
        label='パスワード', max_length=50, widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='パスワード(再)', max_length=50, widget=forms.PasswordInput
    )
        
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            raise ValueError('パスワードが一致しません')
        return cleaned_data
