from django import forms
from .models import Record, CareType

class RecordForm(forms.ModelForm):
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
                'placeholder': '00.0',
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '00.0',
            }),
            'food_type_memo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '餌の種類'
            }),
            'feeding': forms.CheckboxInput(attrs={'class': 'form-check-input', 'value': '1'}),
            #フンをラジオボタンに
            'feces': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            #脱皮　modelsのデータ構造流用
            'shedding': forms.RadioSelect(choices=[(0, '白濁'), (1, '脱皮')], attrs={'class': 'form-check-input'}),
            #日付をカレンダー選択
            'record_date': forms.DateInput(attrs={'type':'date', 'class':'form-control'}),
            #ペットの選択肢欄を綺麗な形にする
            'reptile': forms.Select(attrs={'class': 'form-control'}),
            #conditionをラジオボタンに変更
            'condition': forms.RadioSelect(),
            #memoの欄を大きくする
            'memo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,}),
            'image': forms.FileInput(attrs={'id': 'id_image'}),
        }
        
        
    #care_type(お世話の種類)に入れた項目を持ってきてチェックボックス形式で選択肢にする
    care_types = forms.ModelMultipleChoiceField(
        queryset = CareType.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        label = '今日やったお世話',
        required = False, #お世話を必須項目から外す
    )
    
    
    #データベースに保存される瞬間に、値を 1 か 0 の整数に変更
    def save(self, commit = True):
        instance = super().save(commit=False)
        
        #画面のチェックボックスにチェックがあれば'feeding'のデータが存在する
        feeding_data = self.data.get("feeding")
        
        #データベースには1か0の整数(int)として保存
        instance.feeding = 1 if feeding_data == '1' else 0
        
        if commit:
            instance.save()
            self.save_m2m() # お世話（care_types）の連動保存に必要
        return instance


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #「給餌」の項目を必須項目から外す
        self.fields['feeding'].required = False
        
        
        # 編集画面を開いた時に、データが1ならチェックボックスにチェックを入れる設定
        if self.instance and self.instance.pk:
            self.initial['feeding'] = (self.instance.feeding == 1)