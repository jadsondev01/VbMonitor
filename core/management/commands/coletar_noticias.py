import feedparser
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from dateutil import parser as date_parser
from core.models import Noticia, Fonte, Pauta

# ================== CONFIGURAÇÃO ==================
RSS_FEEDS = {
    "G1": "https://g1.globo.com/rss/g1/ultimas-noticias.xml",
    "UOL": "https://www.uol.com.br/rss.xml",
    "Estadão": "https://rss.estadao.com.br/estadao/internacional.xml",
}

PAUTAS_KEYWORDS = {
    "política": ["política", "governo", "presidente", "senado", "prefeito"],
    "economia": ["economia", "mercado", "inflação", "câmbio", "investimento"],
    "esportes": ["futebol", "esporte", "olimpíadas", "campeonato", "jogo"],
    "educação": ["educação", "escola", "universidade", "ensino", "professor"],
}

# ================== FUNÇÕES AUXILIARES ==================
def extrair_conteudo(url):
    """
    Tenta extrair o conteúdo completo da notícia usando BeautifulSoup.
    Retorna texto limpo.
    """
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        # Pega todos os parágrafos
        artigos = soup.find_all("p")
        texto = " ".join([p.get_text() for p in artigos])
        return texto.strip()
    except Exception:
        return ""

# ================== COMANDO DJANGO ==================
class Command(BaseCommand):
    help = "Coleta notícias de várias fontes automaticamente e associa a pautas"

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando coleta de notícias multi-fonte...")
        novas_total = 0

        for nome_fonte, url_rss in RSS_FEEDS.items():
            self.stdout.write(f"Coletando {nome_fonte}...")
            feed = feedparser.parse(url_rss)
            fonte_obj, _ = Fonte.objects.get_or_create(nome=nome_fonte, url_base=url_rss)
            novas = 0

            for entry in feed.entries:
                # ===== Tentativa segura de extrair dados =====
                titulo = getattr(entry, "title", None) or getattr(entry, "headline", None)
                url = getattr(entry, "link", None)
                resumo = getattr(entry, "summary", None) or getattr(entry, "description", None) or ""

                # Ignora entradas sem título ou URL
                if not titulo or not url:
                    continue

                # Parse da data da notícia
                data_pub = timezone.now()
                if hasattr(entry, "published"):
                    try:
                        data_pub = date_parser.parse(entry.published)
                    except:
                        pass
                elif hasattr(entry, "updated"):
                    try:
                        data_pub = date_parser.parse(entry.updated)
                    except:
                        pass

                # Evitar duplicatas por URL ou título
                if Noticia.objects.filter(url=url).exists() or Noticia.objects.filter(titulo=titulo).exists():
                    continue

                # Extrair conteúdo completo
                conteudo = extrair_conteudo(url)

                # Criar notícia
                noticia = Noticia.objects.create(
                    titulo=titulo,
                    url=url,
                    texto_resumo=resumo,
                    conteudo=conteudo,
                    data_publicacao=data_pub,
                    coletado_em=timezone.now(),
                    fonte=fonte_obj,
                )

                # Associar pautas automaticamente
                for nome_pauta, keywords in PAUTAS_KEYWORDS.items():
                    if any(keyword.lower() in titulo.lower() for keyword in keywords):
                        pauta_obj, _ = Pauta.objects.get_or_create(nome=nome_pauta)
                        noticia.classificacaopauta_set.create(pauta=pauta_obj)

                novas += 1

            self.stdout.write(self.style.SUCCESS(f"{novas} novas notícias coletadas de {nome_fonte}."))
            novas_total += novas

        self.stdout.write(self.style.SUCCESS(f"Coleta finalizada! Total de notícias adicionadas: {novas_total}."))
