from . import views
from django.urls import path, include


urlpatterns = [
    path('', views.home_eLab, name='home_eLab'),
    path('temas/', views.TemaListViewSorted.as_view(), name='temas'), #Classe herdada com classificação nas colunas
    path('tema/<int:pk>', views.TemaDetailView.as_view(), name='tema-detail'),
    path('tema/<int:pk>/update/', views.TemaUpdate.as_view(), name='tema_update'),
    path('outrotema/', views.OutroTema, name='outro_tema'),

    path('coments/', views.ComentListView.as_view(), name='coments'),
    path('coments/create/', views.ComentCreate.as_view(), name='coment_create'),
    path('coment/<int:pk>', views.ComentDetailView.as_view(), name='coment-detail'),
    path('coment/<int:pk>/update/', views.ComentUpdate.as_view(), name='coment_update'),
    path('coment/<int:pk>/delete/', views.ComentDelete.as_view(), name='coment_delete'),

    path('cis/', views.CiListView, name='cis'),
    path('cis/create/', views.CiCreate.as_view(), name='ci_create'),
    path('ci/<str:pk>', views.CiDetailView.as_view(), name='ci-detail'),
    path('ci/<str:pk>/delete/', views.CiDelete.as_view(), name='ci_delete'),
    path('ci/<str:pk>/update/', views.CiUpdate.as_view(), name='ci_update'),

    path('temacoments/create/', views.TemaComentCreate, name='temacoment_create'),
    path('temacoment/<int:pk>', views.TemaComentDetailView.as_view(), name='temacoment-detail'),
    path('temacoment/<int:pk>/delete/', views.TemaComentDelete.as_view(), name='temacoment_delete'),

    path('cicoments/create/', views.CiComentCreate, name='cicoment_create'),
    path('cicoments/novocreate/', views.CiComentNovoCreate, name='cicoment-novo-create'),
    path('cicoment/<int:pk>', views.CiComentDetailView.as_view(), name='cicoment-detail'),
    path('cicoment/<int:pk>/delete/', views.CiComentDelete.as_view(), name='cicoment_delete'),
    path('cicoment/<int:pk>/update/', views.CiComentUpdate.as_view(), name='cicoment_update'),

    path('comps/', views.CompListView, name='comps'),
    path('comps/create/', views.CompCreate.as_view(), name='comp_create'),
    path('comp/<str:pk>', views.CompDetailView.as_view(), name='comp-detail'),
    path('comp/<str:pk>/delete/', views.CompDelete.as_view(), name='comp_delete'),
    path('comp/<str:pk>/update/', views.CompUpdate.as_view(), name='comp_update'),


    path('compcoments/create/', views.CompComentCreate, name='compcoment-create'),
    path('compcoments/novocreate/', views.CompComentNovoCreate, name='compcoment-novo-create'),
    path('compcoment/<int:pk>', views.CompComentDetailView.as_view(), name='compcoment-detail'),
    path('compcoment/<int:pk>/delete/', views.CompComentDelete.as_view(), name='compcoment_delete'),
    path('compcoment/<int:pk>/update/', views.CompComentUpdate.as_view(), name='compcoment_update'),

    path('searchs/', views.SearchListView.as_view(), name='searchs'),


    path("coment/com-infos/", views.ComentComInfosListView.as_view(), name="coment-com-infos"),
    path("coment/<int:codcoment>/infos/", views.ComentInfoByComentListView.as_view(), name="comentinfo-by-coment"),
    path("comentinfo/novo/", views.ComentInfoCreate.as_view(), name="comentinfo-create"),
    path("comentinfo/<int:pk>/editar/", views.ComentInfoUpdate.as_view(), name="comentinfo-update"),
    path("comentinfo/<int:pk>/excluir/", views.ComentInfoDelete.as_view(), name="comentinfo-delete"),


    ]
