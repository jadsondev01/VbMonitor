from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from datetime import datetime, timedelta
from core.models import Noticia, Fonte, Pauta, Municipio

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Período: últimos 30 dias
        fim = datetime.now()
        inicio = fim - timedelta(days=30)
        
        # Métricas básicas
        total_noticias = Noticia.objects.filter(
            data_publicacao__date__gte=inicio.date()
        ).count()
        
        # Notícias por fonte
        noticias_por_fonte = Noticia.objects.filter(
            data_publicacao__date__gte=inicio.date()
        ).values('fonte__nome').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        # Top pautas
        top_pautas = Noticia.objects.filter(
            data_publicacao__date__gte=inicio.date(),
            classificacaopauta__isnull=False
        ).values('classificacaopauta__pauta__nome').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        # Notícias mais acessadas
        top_acessos = Noticia.objects.filter(
            data_publicacao__date__gte=inicio.date()
        ).order_by('-acessos')[:10].values('id', 'titulo', 'acessos', 'fonte__nome')
        
        return Response({
            'total_noticias': total_noticias,
            'noticias_por_fonte': list(noticias_por_fonte),
            'top_pautas': list(top_pautas),
            'top_acessos': list(top_acessos),
        })