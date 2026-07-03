from django import forms
from .models import Record, CareType, RecordCare
from django.db.models import Q

class CheckboxIntegerField(forms.IntegerField):
    def to_python(self, value):
        # HTMLでチェックが入っているとTrue(またはonや1)が届く:1を返す
        # チェックがない、または空データなら0を返す
        if value in ('on', '1', True):
            return 1
        return 0

    def validate(self, value):
        # 親クラスのチェックを行わせず、スルーさせる
        pass


#お世話記録フォーム
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
            'feeding', 'food_type', 'feces', 'shedding', 'memo', 'image'
        ]
        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'form-control', #入力ボックスの横幅が広がる
                'placeholder': '00.0'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '00.0'}),
            'food_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '餌の種類'}),
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
            
            #このレコードに紐づく古いお世話記録（RecordCare）を全部消す（更新対策）
            RecordCare.objects.filter(record=instance).delete()
            
            #画面でチェックされたお世話の種類を1つずつループして手動で登録する
            selected_cares = self.cleaned_data.get('care_types')
            if selected_cares:
                for care in selected_cares:
                    RecordCare.objects.create(record=instance, care_type=care)
            
        return instance

    #編集画面を開いた時の初期化
    def __init__(self, *args, **kwargs):
        #呼び出し元（views.py）から user を受け取るようにする
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        #もし user が渡されてきたら、選択肢をその人のペット（＋共有されたペット）だけに絞り込む
        if user:
            from reptile.models import Reptile, UserShare
            # 自分がオーナーのペット、または自分に共有されているオーナーのペットのIDを集める
            shared_owners = UserShare.objects.filter(shared_user=user).values_list('owner_user_id', flat=True)
            # 自分のペット、または共有相手のペットだけをドロップダウンに出す
            self.fields['reptile'].queryset = Reptile.objects.filter(
                Q(user=user) | Q(user__in=shared_owners)
            )
            
        # 編集画面の時に、初期値を正しくチェックボックスやラジオボタンに反映させる処理
        if self.instance and self.instance.pk:
            self.initial['feeding'] = (self.instance.feeding == 1)
            self.initial['condition'] = self.instance.condition
            self.initial['feces'] = self.instance.feces
            self.initial['shedding'] = self.instance.shedding
            
            #編集画面を開いた時に、登録済みのお世話にチェックを入れる初期化処理
            already_checked = RecordCare.objects.filter(record=self.instance).values_list('care_type_id', flat=True)
            self.initial['care_types'] = list(already_checked)