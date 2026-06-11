from django import forms
from .models import Record, CareType

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record #models.pyのRecoedをベースに使う
        #画面に表示したい項目
        fields = ['record_date', 'reptile', 'condition', 'care_types', 'memo']
        
        widgets = {
            #日付をカレンダー選択
            'record_date' : forms.DateInput(attrs={'type':'date', 'class':'form-control'}),
            #ペットの選択肢欄を綺麗な形にする
            'reptile' : forms.Select(attrs={'class': 'form-control'}),
            #conditionをラジオボタンに変更
            'condition' : forms.RadioSelect(),
            #memoの欄を大きくする
            'memo' : forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    #care_tupe(お世話の種類)に入れた項目を持ってきてチェックボックス形式で選択肢にする
    care_types = forms.ModelMultipleChoiceField(
        queryset = CareType.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        label = '今日やったお世話'
    )
