from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Record
from .forms import RecordForm

#お世話記録を新しく作るためのビュー
class RecordCreateView(CreateView):
    model = Record
    form_class = RecordForm
    template_name = 'reptile/record_form.html'
    
    #保存成功後の画面切り替え先(一旦管理画面にした)
    success_url = reverse_lazy('admin:index')
