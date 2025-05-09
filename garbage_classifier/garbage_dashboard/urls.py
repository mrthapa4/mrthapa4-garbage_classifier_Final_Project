# urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload_file'),
    path('profile/', views.profile, name='profile'),
    path('classify/<int:item_id>/', views.classify_item, name='classify_item'),
    path('result/', views.result, name='result'),
] 