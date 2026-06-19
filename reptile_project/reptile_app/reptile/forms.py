from django import forms
from .models import Record, CareType

class CheckboxIntegerField(forms.IntegerField):
    def to_python(self, value):
        # HTMLでチェックが入っていると 'on' や '1' が届く -> 1 を返す
        # チェックがない、または空データなら -> 0 を返す
        if value in ('on', '1', True):
            return 1
        return 0

    def validate(self, value):
        # 親クラスのチェックを行わせず、スルーさせる
        pass


class RecordForm(forms.ModelForm):
    
    #元気 (0, 1, 2) を文字列として受け取ってバリデーションを通す
    condition = forms.TypedChoiceField(
        coerce=int,
        choices=[(0, '元気'), (1, '普通'), (2, '元気がない')],
        widget=forms.RadioSelect(),
        initial=1, # デフォルトを「普通」にする
        required=True
    )

    feeding = CheckboxIntegerField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_feeding'
        })
    )
    
    #フン (0, 1) を文字列から数値へ自動変換
    feces = forms.TypedChoiceField(
        coerce=int,
        choices=[(0, '異常'), (1, '正常')],
        required=False,
        empty_value=None,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    #脱皮 (0, 1) を文字列から数値へ自動変換
    shedding = forms.TypedChoiceField(
        coerce=int,
        choices=[(0, '白濁'), (1, '脱皮')],
        required=False,
        empty_value=None,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
        
    # care_type(お世話の種類)に入れた項目を持ってきてチェックボックス形式で選択肢にする
    care_types = forms.ModelMultipleChoiceField(
        queryset = CareType.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        label = '今日やったお世話',
        required = False,
    )
    
    
    class Meta:
        model = Record #models.pyのRecordをベースに使う
        #画面に表示したい項目
        fields = [
            'record_date', 'reptile', 'condition', 'weight', 'length', 
            'feeding', 'food_type_memo', 'feces', 'shedding', 'care_types', 'memo', 'image'
        ]
        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'form-control', #入力ボックスの横幅が広がる
                'placeholder': '00.0'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '00.0'}),
            'food_type_memo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '餌の種類'}),
            'record_date': forms.DateInput(attrs={'type':'date', 'class':'form-control'}),
            #ペットの選択肢欄を綺麗な形にする
            'reptile': forms.Select(attrs={'class': 'form-control'}),
            'memo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'id': 'id_image'}),
        }
        

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # フォームの自動変換を通った安全な数値をモデルに代入
        instance.condition = self.cleaned_data.get('condition')
        instance.feeding = self.cleaned_data.get('feeding')
        instance.feces = self.cleaned_data.get('feces')
        instance.shedding = self.cleaned_data.get('shedding')
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 編集画面の時に、初期値を正しくチェックボックスやラジオボタンに反映させる処理
        if self.instance and self.instance.pk:
            self.initial['feeding'] = (self.instance.feeding == 1)
            self.initial['condition'] = self.instance.condition
            self.initial['feces'] = self.instance.feces
            self.initial['shedding'] = self.instance.shedding