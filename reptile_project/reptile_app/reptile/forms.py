from django import forms
from .models import Record, CareType

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record #models.pyのRecoedをベースに使う
        #画面に表示したい項目
        fields = [
            'record_date', 'reptile', 'condition', 'weight', 'length', 
            'feeding', 'food_type_memo', 'feces', 'shedding', 'care_types', 'memo', 'image'
        ]
        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'form-control', #入力ボックスの横幅が広がる
                'placeholder': '00.0',
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '00.0',
            }),
            #給餌をラジオボタンに
            'feeding': forms.RadioSelect(choices=[(0, 'なし'),(1, 'あり')], attrs={'class': 'form-check-input'}),
            'food_type_memo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '餌の種類'
            }),
            #フンをラジオボタンに
            'feces': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            #脱皮　modelsのデータ構造流用
            'shedding': forms.RadioSelect(choices=[(0, '白濁'), (1, '脱皮')], attrs={'class': 'form-check-input'}),
            'memo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'メモ（最大500文字）'}),
            #日付をカレンダー選択
            'record_date': forms.DateInput(attrs={'type':'date', 'class':'form-control'}),
            #ペットの選択肢欄を綺麗な形にする
            'reptile': forms.Select(attrs={'class': 'form-control'}),
            #conditionをラジオボタンに変更
            'condition': forms.RadioSelect(),
            #memoの欄を大きくする
            'memo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    #care_tupe(お世話の種類)に入れた項目を持ってきてチェックボックス形式で選択肢にする
    care_types = forms.ModelMultipleChoiceField(
        queryset = CareType.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        label = '今日やったお世話'
    )
