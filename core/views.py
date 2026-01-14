from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from django.shortcuts import redirect
from django.contrib import messages
from .forms import PautaForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Municipio
from django.db.models import Count





from .models import Noticia, Fonte, Municipio, Pauta
from .serializers import (
    NoticiaSerializer,
    FonteSerializer,
    MunicipioSerializer,
    PautaSerializer
)

# =========================================================
# ===================== API VIEWSETS ======================
# =========================================================

class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.all().order_by('-data_publicacao')
    serializer_class = NoticiaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['fonte', 'deduplicado']
    search_fields = ['titulo', 'texto_resumo', 'conteudo']
    ordering_fields = ['data_publicacao', 'acessos']

    @action(detail=True, methods=['post'])
    def registrar_acesso(self, request, pk=None):
        noticia = self.get_object()
        noticia.acessos += 1
        noticia.save()
        return Response({'acessos': noticia.acessos})


class FonteViewSet(viewsets.ModelViewSet):
    queryset = Fonte.objects.all()
    serializer_class = FonteSerializer
    permission_classes = [permissions.IsAuthenticated]


class MunicipioViewSet(viewsets.ModelViewSet):
    queryset = Municipio.objects.all()
    serializer_class = MunicipioSerializer
    permission_classes = [permissions.IsAuthenticated]


class PautaViewSet(viewsets.ModelViewSet):
    queryset = Pauta.objects.all()
    serializer_class = PautaSerializer
    permission_classes = [permissions.IsAuthenticated]

# =========================================================
# ===================== DASHBOARD =========================
# =========================================================

@login_required
def dashboard(request):
    hoje = timezone.now().date()
    trinta_dias_atras = hoje - timedelta(days=30)

    total_noticias = Noticia.objects.filter(
        data_publicacao__date__gte=trinta_dias_atras
    ).count()

    fontes_ativas = Fonte.objects.filter(ativo=True).count()

    acessos_hoje = sum(
        n.acessos for n in Noticia.objects.filter(coletado_em__date=hoje)
    )

    noticias_em_alta = Noticia.objects.all().order_by('-acessos')[:10]

    pautas_data = []
    pautas_labels = []

    for pauta in Pauta.objects.all()[:8]:
        count = Noticia.objects.filter(classificacaopauta__pauta=pauta).count()
        if count > 0:
            pautas_data.append(count)
            pautas_labels.append(pauta.nome)

    if not pautas_data:
        pautas_data = [5, 3, 2, 1]
        pautas_labels = ['Política', 'Economia', 'Esportes', 'Educação']

    atividades_recentes = []
    for noticia in Noticia.objects.order_by('-coletado_em')[:3]:
        atividades_recentes.append({
            'data': noticia.coletado_em,
            'descricao': f'Notícia coletada: {noticia.titulo[:50]}...',
            'tipo': 'info',
            'badge': 'Coleta'
        })

    return render(request, 'dashboard.html', {
        'total_noticias': total_noticias,
        'fontes_ativas': fontes_ativas,
        'acessos_hoje': acessos_hoje,
        'alertas_ativos': 0,
        'noticias_em_alta': noticias_em_alta,
        'pautas_data': pautas_data,
        'pautas_labels': pautas_labels,
        'atividades_recentes': atividades_recentes,
    })

# =========================================================
# ===================== NOTÍCIAS ==========================
# =========================================================

@login_required
def listar_noticias(request):
    noticias = Noticia.objects.all().order_by('-data_publicacao')

    if request.GET.get('fonte'):
        noticias = noticias.filter(fonte_id=request.GET['fonte'])

    if request.GET.get('municipio'):
        noticias = noticias.filter(
            classificacaomunicipio__municipio_id=request.GET['municipio']
        )

    if request.GET.get('pauta'):
        noticias = noticias.filter(
            classificacaopauta__pauta_id=request.GET['pauta']
        )

    if request.GET.get('q'):
        q = request.GET['q']
        noticias = noticias.filter(
            Q(titulo__icontains=q) |
            Q(texto_resumo__icontains=q) |
            Q(conteudo__icontains=q)
        )

    return render(request, 'noticias/list.html', {
        'noticias': noticias,
        'fontes': Fonte.objects.all(),
        'municipios': Municipio.objects.all(),
        'pautas': Pauta.objects.all(),
    })


@login_required
def detalhe_noticia(request, id):
    noticia = get_object_or_404(Noticia, id=id)
    noticia.acessos += 1
    noticia.save()

    return render(request, 'noticias/detail.html', {
        'noticia': noticia,
        'pautas': noticia.classificacaopauta_set.all(),
        'municipios': noticia.classificacaomunicipio_set.all(),
    })

# =========================================================
# ===================== FONTES ============================
# =========================================================

@login_required
def listar_fontes(request):
    fontes = Fonte.objects.annotate(
        total_noticias=Count('noticia')
    ).order_by('nome')

    return render(request, 'fontes/list.html', {
        'fontes': fontes
    })


@login_required
def detalhe_fonte(request, id):
    fonte = get_object_or_404(Fonte, id=id)

    noticias = Noticia.objects.filter(
        fonte=fonte
    ).order_by('-data_publicacao')

    return render(request, 'fontes/detail.html', {
        'fonte': fonte,
        'noticias': noticias
    })


# =========================================================
# ===================== MUNICÍPIOS ========================
# =========================================================

@login_required
def listar_municipios(request):
    municipios = Municipio.objects.annotate(
        total_noticias=Count('classificacaomunicipio')
    )

    return render(request, 'municipios/list.html', {
        'municipios': municipios
    })
from .forms import MunicipioForm
from django.contrib import messages

@login_required
def criar_municipio(request):
    form = MunicipioForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Município criado com sucesso!')
        return redirect('listar_municipios')

    return render(request, 'municipios/form.html', {'form': form})
@login_required
def editar_municipio(request, id):
    municipio = get_object_or_404(Municipio, id=id)
    form = MunicipioForm(request.POST or None, instance=municipio)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Município atualizado com sucesso!')
        return redirect('listar_municipios')
@login_required
def excluir_municipio(request, id):
    municipio = get_object_or_404(Municipio, id=id)

    if request.method == 'POST':
        municipio.delete()
        messages.success(request, 'Município removido com sucesso!')
        return redirect('listar_municipios')

    return render(request, 'municipios/confirm_delete.html', {'municipio': municipio})    


# =========================================================
# ===================== PAUTAS ============================
# =========================================================

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def listar_noticias(request):
    noticias = Noticia.objects.all().order_by('-data_publicacao')

    # Filtros
    if request.GET.get('fonte'):
        noticias = noticias.filter(fonte_id=request.GET['fonte'])

    if request.GET.get('municipio'):
        noticias = noticias.filter(
            classificacaomunicipio__municipio_id=request.GET['municipio']
        )

    if request.GET.get('pauta'):
        noticias = noticias.filter(
            classificacaopauta__pauta_id=request.GET['pauta']
        )

    if request.GET.get('q'):
        q = request.GET['q']
        noticias = noticias.filter(
            Q(titulo__icontains=q) |
            Q(texto_resumo__icontains=q) |
            Q(conteudo__icontains=q)
        )

    # Paginação
    page = request.GET.get('page', 1)
    paginator = Paginator(noticias, 10)  # 10 notícias por página
    try:
        noticias_page = paginator.page(page)
    except PageNotAnInteger:
        noticias_page = paginator.page(1)
    except EmptyPage:
        noticias_page = paginator.page(paginator.num_pages)

    return render(request, 'noticias/list.html', {
        'noticias': noticias_page,
        'fontes': Fonte.objects.all(),
        'municipios': Municipio.objects.all(),
        'pautas': Pauta.objects.all(),
        'paginator': paginator,
        'page_obj': noticias_page,
    })


@login_required
def detalhe_pauta(request, id):
    pauta = get_object_or_404(Pauta, id=id)
    return render(request, 'pautas/detail.html', {
        'pauta': pauta,
        'noticias': Noticia.objects.filter(
            classificacaopauta__pauta=pauta
        )
    })

# =========================================================
# ===================== ALERTAS ===========================
# =========================================================

@login_required
def listar_alertas(request):
    return render(request, 'alertas/list.html', {
        'alertas': []
    })

# =========================================================
# ===================== ANALYTICS =========================
# =========================================================

@login_required
def analytics(request):
    # Notícias por Fonte
    noticias_por_fonte = (
        Fonte.objects
        .annotate(total=Count('noticia'))
        .filter(total__gt=0)
        .order_by('-total')
    )

    # Notícias por Pauta
    noticias_por_pauta = (
        Pauta.objects
        .annotate(total=Count('classificacaopauta'))
        .filter(total__gt=0)
        .order_by('-total')
    )

    # Notícias por Município
    noticias_por_municipio = (
        Municipio.objects
        .annotate(total=Count('classificacaomunicipio'))
        .filter(total__gt=0)
        .order_by('-total')[:10]
    )

    context = {
        'total_noticias': Noticia.objects.count(),
        'total_fontes': Fonte.objects.count(),

        'fonte_labels': [f.nome for f in noticias_por_fonte],
        'fonte_data': [f.total for f in noticias_por_fonte],

        'pauta_labels': [p.nome for p in noticias_por_pauta],
        'pauta_data': [p.total for p in noticias_por_pauta],

        'municipio_labels': [m.nome for m in noticias_por_municipio],
        'municipio_data': [m.total for m in noticias_por_municipio],
    }

    return render(request, 'analytics/dashboard.html', context)

@login_required
def detalhe_municipio(request, id):
    municipio = get_object_or_404(Municipio, id=id)

    noticias = Noticia.objects.filter(
        classificacaomunicipio__municipio=municipio
    ).order_by('-data_publicacao')

    return render(request, 'municipios/detail.html', {
        'municipio': municipio,
        'noticias': noticias
    })
from .forms import PautaForm

@login_required
def listar_pautas(request):
    return render(request, 'pautas/list.html', {
        'pautas': Pauta.objects.all()
    })

@login_required
def criar_pauta(request):
    form = PautaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('listar_pautas')
    return render(request, 'pautas/form.html', {'form': form})

@login_required
def editar_pauta(request, id):
    pauta = get_object_or_404(Pauta, id=id)
    form = PautaForm(request.POST or None, instance=pauta)
    if form.is_valid():
        form.save()
        return redirect('listar_pautas')
    return render(request, 'pautas/form.html', {'form': form})

@login_required
def excluir_pauta(request, id):
    pauta = get_object_or_404(Pauta, id=id)
    if request.method == 'POST':
        pauta.delete()
        return redirect('listar_pautas')
    return render(request, 'pautas/confirm_delete.html', {'pauta': pauta})






