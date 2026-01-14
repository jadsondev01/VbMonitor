from django.urls import path
from . import views

app_name = 'core'  # ← CORRETO, apenas este

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Municípios
    path('municipios/', views.listar_municipios, name='listar_municipios'),
    path('municipios/criar/', views.criar_municipio, name='criar_municipio'),
    path('municipios/<int:id>/', views.detalhe_municipio, name='detalhe_municipio'),
    path('municipios/<int:id>/editar/', views.editar_municipio, name='editar_municipio'),
    path('municipios/<int:id>/excluir/', views.excluir_municipio, name='excluir_municipio'),

    # Fontes
    path('fontes/', views.listar_fontes, name='listar_fontes'),
    path('fontes/<int:id>/', views.detalhe_fonte, name='detalhe_fonte'),

    # Pautas
    path('pautas/', views.listar_pautas, name='listar_pautas'),
    path('pautas/criar/', views.criar_pauta, name='criar_pauta'),
    path('pautas/<int:id>/', views.detalhe_pauta, name='detalhe_pauta'),
    path('pautas/<int:id>/editar/', views.editar_pauta, name='editar_pauta'),
    path('pautas/<int:id>/excluir/', views.excluir_pauta, name='excluir_pauta'),

    # Notícias
    path('noticias/', views.listar_noticias, name='listar_noticias'),
    path('noticias/<int:id>/', views.detalhe_noticia, name='detalhe_noticia'),

    # Analytics / Alertas
    path('alertas/', views.listar_alertas, name='listar_alertas'),
    path('analytics/', views.analytics, name='analytics'),
]
