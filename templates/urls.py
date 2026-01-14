from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # ← ESSENCIAL

    # Dashboard
    path('', views.dashboard, name='casa'),
    path('painel/', views.dashboard, name='painel'),

    # Notícias
    path('noticias/', views.listar_noticias, name='listar_noticias'),
    path('noticias/<int:id>/', views.detalhe_noticia, name='detalhe_noticia'),

    # Fontes
    path('fontes/', views.listar_fontes, name='listar_fontes'),
    path('fontes/<int:id>/', views.detalhe_fonte, name='detalhe_fonte'),

    # Municípios
    path('municipios/', views.listar_municipios, name='listar_municipios'),
    path('municipios/<int:id>/', views.detalhe_municipio, name='detalhe_municipio'),

    # Pautas
    path('pautas/', views.listar_pautas, name='listar_pautas'),
    path('pautas/<int:id>/', views.detalhe_pauta, name='detalhe_pauta'),

    # Alertas
    path('alertas/', views.listar_alertas, name='listar_alertas'),

    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]
