from django.contrib import admin
from django.urls import path, include
from reptile import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portfolio.urls')),
    path('user/', include('user.urls')),
    path('record/add/', views.RecordCreateView.as_view(), name='record_add'),
]