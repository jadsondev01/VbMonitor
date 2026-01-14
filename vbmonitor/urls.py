from django.contrib import admin
from django.urls import path
from core import views
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # ← ISSO É OBRIGATÓRIO

    # Dashboard
    path('', views.dashboard, name='casa'),
    path('painel/', views.dashboard, name='painel'),

    # Notícias
    path('noticias/', views.listar_noticias, name='listar_noticias'),
    path('noticias/<int:id>/', views.detalhe_noticia, name='detalhe_noticia'),

    # Fontes
    path('fontes/', views.listar_fontes, name='listar_fontes'),

    # Municípios
    path('municipios/', views.listar_municipios, name='listar_municipios'),

    # Pautas
    path('pautas/', views.listar_pautas, name='listar_pautas'),
    path('pautas/criar/', views.criar_pauta, name='criar_pauta'),
    path('pautas/<int:pk>/editar/', views.editar_pauta, name='editar_pauta'),
    path('pautas/<int:pk>/excluir/', views.excluir_pauta, name='excluir_pauta'),

    # Alertas
    path('alertas/', views.listar_alertas, name='listar_alertas'),

    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]
