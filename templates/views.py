from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend



from .models import Noticia, Fonte, Municipio, Pauta
from .serializers import (
    NoticiaSerializer,
    FonteSerializer,
    MunicipioSerializer,
    PautaSerializer,
)

# =========================
# API VIEWSETS
# =========================

class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.all().order_by("-data_publicacao")
    serializer_class = NoticiaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["fonte", "deduplicado"]
    search_fields = ["titulo", "texto_resumo"]
    ordering_fields = ["data_publicacao", "acessos"]

    @action(detail=True, methods=["post"])
    def registrar_acesso(self, request, pk=None):
        noticia = self.get_object()
        noticia.acessos += 1
        noticia.save(update_fields=["acessos"])
        return Response({"acessos": noticia.acessos})


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


# =========================
# DASHBOARD
# =========================

@login_required
def dashboard(request):
    hoje = timezone.now().date()
    trinta_dias_atras = hoje - timedelta(days=30)

    # Estatísticas principais
    total_noticias = Noticia.objects.filter(
        data_publicacao__date__gte=trinta_dias_atras
    ).count()

    fontes_ativas = Fonte.objects.filter(ativo=True).count()

    acessos_hoje = (
        Noticia.objects.filter(coletado_em__date=hoje)
        .aggregate(total=Count("acessos"))
        .get("total") or 0
    )

    noticias_em_alta = (
        Noticia.objects.all()
        .order_by("-acessos")[:10]
    )

    # Distribuição por pauta
    pautas_qs = (
        Pauta.objects
        .annotate(total=Count("classificacaopauta__noticia"))
        .filter(total__gt=0)
        .order_by("-total")[:8]
    )

    pautas_labels = [pauta.nome for pauta in pautas_qs]
    pautas_data = [pauta.total for pauta in pautas_qs]

    if not pautas_data:
        pautas_labels = ["Política", "Economia", "Esportes", "Educação"]
        pautas_data = [5, 3, 2, 1]

    # Atividades recentes
    noticias_recentes = Noticia.objects.order_by("-coletado_em")[:3]

    if noticias_recentes.exists():
        atividades_recentes = [
            {
                "data": noticia.coletado_em,
                "descricao": f"Notícia coletada: {noticia.titulo[:50]}...",
                "tipo": "info",
                "badge": "Coleta",
            }
            for noticia in noticias_recentes
        ]
    else:
        atividades_recentes = [
            {
                "data": timezone.now() - timedelta(hours=1),
                "descricao": "Sistema VBMonitor iniciado com sucesso",
                "tipo": "success",
                "badge": "Sistema",
            },
            {
                "data": timezone.now() - timedelta(hours=2),
                "descricao": "Base de dados configurada",
                "tipo": "info",
                "badge": "Banco",
            },
            {
                "data": timezone.now() - timedelta(hours=3),
                "descricao": "Usuário admin criado",
                "tipo": "warning",
                "badge": "Usuário",
            },
        ]

    context = {
        "total_noticias": total_noticias,
        "fontes_ativas": fontes_ativas,
        "acessos_hoje": acessos_hoje,
        "alertas_ativos": 0,
        "noticias_em_alta": noticias_em_alta,
        "pautas_labels": pautas_labels,
        "pautas_data": pautas_data,
        "atividades_recentes": atividades_recentes,
    }

    return render(request, "dashboard.html", context)


# =========================
# NOTÍCIAS
# =========================

@login_required
def listar_noticias(request):
    noticias = Noticia.objects.all().order_by("-data_publicacao")

    fonte_id = request.GET.get("fonte")
    municipio_id = request.GET.get("municipio")
    pauta_id = request.GET.get("pauta")
    busca = request.GET.get("q")

    if fonte_id:
        noticias = noticias.filter(fonte_id=fonte_id)

    if municipio_id:
        noticias = noticias.filter(
            classificacaomunicipio__municipio_id=municipio_id
        )

    if pauta_id:
        noticias = noticias.filter(
            classificacaopauta__pauta_id=pauta_id
        )

    if busca:
        noticias = noticias.filter(
            Q(titulo__icontains=busca) |
            Q(texto_resumo__icontains=busca)
        )

    context = {
        "noticias": noticias.distinct(),
        "fontes": Fonte.objects.all(),
        "municipios": Municipio.objects.all(),
        "pautas": Pauta.objects.all(),
    }

    return render(request, "noticias/list.html", context)


@login_required
def detalhe_noticia(request, id):
    from django.shortcuts import get_object_or_404

    noticia = get_object_or_404(Noticia, id=id)

    noticia.acessos += 1
    noticia.save(update_fields=["acessos"])

    context = {
        "noticia": noticia,
        "pautas": noticia.classificacaopauta_set.all(),
        "municipios": noticia.classificacaomunicipio_set.all(),
    }

    return render(request, "noticias/detail.html", context)
@login_required
def listar_fontes(request):
    fontes = Fonte.objects.annotate(
        total_noticias=Count('noticia')
    )

    busca = request.GET.get('q')
    if busca:
        fontes = fontes.filter(nome__icontains=busca)

    return render(request, 'fontes/list.html', {
        'fontes': fontes,
        'busca': busca
    })

@login_required
def listar_municipios(request):
    municipios = Municipio.objects.annotate(
        total_noticias=Count('noticias')
    )

    return render(request, 'municipios/list.html', {
        'municipios': municipios
    })