from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_cNum, name='home_cNum'),
    path('topicos/', views.topicos_cNum, name='topicos_cNum'),
]


