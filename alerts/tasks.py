# alerts/tasks.py
import feedparser
from core.models import Noticia, Fonte
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# URL do feed RSS do G1
G1_FEED_URL = "https://g1.globo.com/rss/g1/"  # ajuste se precisar do feed de outra seção

def processar_noticias():
    # Fonte do G1 no banco (cria se não existir)
    fonte, _ = Fonte.objects.get_or_create(nome="G1")

    # Lê o feed
    feed = feedparser.parse(G1_FEED_URL)

    # Pega cada notícia do feed
    for entry in feed.entries:
        try:
            # Evita duplicar notícias pelo campo 'url'
            if Noticia.objects.filter(url=getattr(entry, 'link', '')).exists():
                continue

            # Cria a notícia preenchendo todos os campos obrigatórios
            noticia = Noticia.objects.create(
                titulo=getattr(entry, 'title', 'Sem título'),
                url=getattr(entry, 'link', ''),
                conteudo=getattr(entry, 'summary', '') or '',
                texto_resumo=(getattr(entry, 'summary', '')[:200] if getattr(entry, 'summary', None) else ''),
                data_publicacao=getattr(entry, 'published_parsed', None) and timezone.make_aware(
                    timezone.datetime(*entry.published_parsed[:6])
                ) or timezone.now(),
                fonte=fonte
            )

            # Envia atualização para WebSocket se estiver ativo
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    "noticias",  # nome do grupo
                    {
                        "type": "nova_noticia",
                        "message": {
                            "id": noticia.id,
                            "titulo": noticia.titulo,
                            "url": noticia.url
                        }
                    }
                )
        except Exception as e:
            # Não quebra o loop, apenas registra
            print(f"Erro ao processar notícia: {e}")
