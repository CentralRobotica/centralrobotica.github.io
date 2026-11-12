# -*- coding: utf-8 -*-
"""
Central Robótica — coletor da BIBLIOTECA.

Alimenta duas guias do site:
  • +1000 Curiosidades — matérias sobre robôs e robótica de revistas, sites e
    universidades do mundo todo (Live Science, New Scientist, Popular Science,
    Robohub, New Atlas, MIT, Berkeley, Pesquisa FAPESP...).
  • Universidades — notícias de pesquisa publicadas pelas próprias universidades,
    periódicos científicos e os artigos novos de robótica do arXiv (cs.RO).

Tudo é traduzido para o português. A cada execução:
  1. lê a página mais recente de cada fonte (novidades);
  2. avança algumas páginas no arquivo antigo das fontes que permitem
     (histórico cresce sozinho até o limite de cada fonte);
  3. traduz o que estiver pendente (com limite por execução) e busca imagens.

Uso:  python coletor/biblioteca.py   (o gerenciador.py já chama este script)
"""
import concurrent.futures as cf
import hashlib
import json
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atualizar as A  # noqa: E402  (reaproveita leitura de feeds, tradução, imagens, categorias)

PASTA = os.path.join(A.RAIZ, "dados", "biblioteca")
ARQ_ITENS = os.path.join(PASTA, "itens.json")
ARQ_JS = os.path.join(PASTA, "biblioteca.js")
ARQ_ESTADO = os.path.join(PASTA, "estado.json")
PASTA_ARXIV = os.path.join(PASTA, "arxiv")

LIMITE_TRADUCAO = 450   # matérias traduzidas por execução (o resto fica para a próxima)
LIMITE_IMAGENS = 300    # imagens buscadas por execução
PAGINAS_POR_EXECUCAO = 3  # páginas do arquivo antigo lidas por fonte a cada execução
PAGINAS_PRIMEIRA = 8      # na primeira vez, para já começar com bastante conteúdo

# tipo: universidade | revista | site | periodico | pesquisa
# paginas: quantas páginas de histórico a fonte permite ({n} = número da página)
FONTES = [
    # ---------------- Universidades ----------------
    {"nome": "MIT News — Robótica", "inst": "MIT", "pais": "EUA", "tipo": "universidade", "url": "https://news.mit.edu/topic/mitrobotics-rss.xml"},
    {"nome": "MIT News — Pesquisa", "inst": "MIT", "pais": "EUA", "tipo": "universidade", "url": "https://news.mit.edu/rss/research", "filtrar": True},
    {"nome": "MIT CSAIL", "inst": "MIT", "pais": "EUA", "tipo": "universidade", "url": "https://www.csail.mit.edu/rss.xml", "filtrar": True},
    {"nome": "Carnegie Mellon University", "inst": "Carnegie Mellon", "pais": "EUA", "tipo": "universidade", "url": "https://www.cmu.edu/news/rss/news.xml", "filtrar": True},
    {"nome": "UC Berkeley", "inst": "UC Berkeley", "pais": "EUA", "tipo": "universidade", "url": "https://news.berkeley.edu/?s=robot&feed=rss2&paged={n}", "paginas": 20, "filtrar": True},
    {"nome": "Berkeley AI Research (BAIR)", "inst": "UC Berkeley", "pais": "EUA", "tipo": "universidade", "url": "https://bair.berkeley.edu/blog/feed.xml", "filtrar": True},
    {"nome": "University of Washington", "inst": "Univ. de Washington", "pais": "EUA", "tipo": "universidade", "url": "https://www.washington.edu/news/?s=robot&feed=rss2&paged={n}", "paginas": 20, "filtrar": True},
    {"nome": "Caltech", "inst": "Caltech", "pais": "EUA", "tipo": "universidade", "url": "https://www.caltech.edu/about/news/rss", "filtrar": True},
    {"nome": "ETH Zurich", "inst": "ETH Zurich", "pais": "Suíça", "tipo": "universidade", "url": "https://ethz.ch/en/news-and-events/eth-news/news/_jcr_content.feed", "filtrar": True},
    {"nome": "EPFL", "inst": "EPFL", "pais": "Suíça", "tipo": "universidade", "url": "https://actu.epfl.ch/feeds/rss/mediacom/en/", "filtrar": True},
    {"nome": "Institute of Science Tokyo", "inst": "Science Tokyo", "pais": "Japão", "tipo": "universidade", "url": "https://www.titech.ac.jp/english/news/rss.xml", "filtrar": True},
    {"nome": "National University of Singapore", "inst": "NUS", "pais": "Singapura", "tipo": "universidade", "url": "https://news.nus.edu.sg/feed/", "filtrar": True},
    # ---------------- Revistas ----------------
    {"nome": "Live Science", "pais": "EUA", "tipo": "revista", "url": "https://www.livescience.com/feeds/tag/robots"},
    {"nome": "New Scientist", "pais": "Reino Unido", "tipo": "revista", "url": "https://www.newscientist.com/subject/robotics/feed/"},
    {"nome": "Popular Science", "pais": "EUA", "tipo": "revista", "url": "https://www.popsci.com/feed/?paged={n}", "paginas": 15, "filtrar": True},
    {"nome": "MIT Technology Review", "pais": "EUA", "tipo": "revista", "url": "https://www.technologyreview.com/feed/", "filtrar": True},
    {"nome": "Scientific American", "pais": "EUA", "tipo": "revista", "url": "http://rss.sciam.com/ScientificAmerican-Global", "filtrar": True},
    {"nome": "Smithsonian Magazine", "pais": "EUA", "tipo": "revista", "url": "https://www.smithsonianmag.com/rss/science-nature/", "filtrar": True},
    {"nome": "Popular Mechanics", "pais": "EUA", "tipo": "revista", "url": "https://www.popularmechanics.com/rss/all.xml/", "filtrar": True},
    {"nome": "The Conversation", "pais": "Internacional", "tipo": "revista", "url": "https://theconversation.com/global/topics/robots-388/articles.atom", "filtrar": True},
    # ---------------- Sites especializados ----------------
    {"nome": "Robohub", "pais": "Internacional", "tipo": "site", "url": "https://robohub.org/feed/?paged={n}", "paginas": 16},
    {"nome": "New Atlas", "pais": "Austrália", "tipo": "site", "url": "https://newatlas.com/robotics/index.rss?page={n}", "paginas": 10},
    {"nome": "ScienceAlert", "pais": "Austrália", "tipo": "site", "url": "https://www.sciencealert.com/feed?s=robot&paged={n}", "paginas": 10, "filtrar": True},
    {"nome": "Phys.org", "pais": "Reino Unido", "tipo": "site", "url": "https://phys.org/rss-feed/technology-news/robotics/"},
    {"nome": "Frontiers in Robotics and AI", "inst": "Frontiers", "pais": "Suíça", "tipo": "periodico", "url": "https://www.frontiersin.org/journals/robotics-and-ai/rss"},
    {"nome": "BBC", "pais": "Reino Unido", "tipo": "site", "url": "https://www.bbc.co.uk/news/science_and_environment/rss.xml", "filtrar": True},
]

ARXIV = {"nome": "arXiv — Robótica (cs.RO)", "url": "https://rss.arxiv.org/rss/cs.RO"}


# --------------------------------------------------------------------------- #
def carregar(caminho, padrao):
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    return padrao


def salvar_json(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=0)


def ident(url):
    return hashlib.sha1(A.normalizar_url(url).encode()).hexdigest()[:14]


def ler_pagina(fonte, url):
    """Lê uma página de feed (RSS ou Atom) e devolve itens crus."""
    try:
        raiz = ET.fromstring(A.baixar(url, timeout=40, limite=16_000_000))
    except Exception as e:
        print(f"  ! {fonte['nome']}: {str(e)[:80]}", file=sys.stderr)
        return None
    itens = []
    for el in raiz.iter():
        if A._nome_local(el.tag) not in ("item", "entry"):
            continue
        titulo = A.limpar_html(A._texto(el, "title"))
        link = A._texto(el, "link")
        if not link:
            l = A._filho(el, "link")
            if l is not None:
                link = l.get("href", "")
        corpo = ""
        for nome in ("description", "summary", "encoded", "content"):
            c = A._filho(el, nome)
            if c is not None and (c.text or "").strip():
                corpo = c.text
                break
        data = A.data_item(A._texto(el, "pubdate") or A._texto(el, "published") or A._texto(el, "updated") or A._texto(el, "date"))
        if not (titulo and link and data):
            continue
        resumo = A.cortar(A.limpar_html(corpo), 320)
        if fonte.get("filtrar") and not A.BASE_ROBOTICA.search(titulo + " " + resumo[:300]):
            continue
        if A.EXCLUIR.search(titulo):
            continue
        itens.append({"titulo": titulo, "link": link.strip(), "data": data, "resumo": resumo, "imagem": A._imagem_do_item(el, corpo)})
    return itens


def coletar_fonte(fonte, estado):
    """Página mais recente + algumas páginas do histórico (se a fonte permitir)."""
    paginas = [1]
    st = estado.setdefault(fonte["nome"], {"proxima": 2, "fim": False})
    if "{n}" in fonte["url"] and not st["fim"]:
        qtd = PAGINAS_PRIMEIRA if st["proxima"] == 2 else PAGINAS_POR_EXECUCAO
        paginas += list(range(st["proxima"], min(st["proxima"] + qtd, fonte.get("paginas", 1) + 1)))
    todos = []
    for p in paginas:
        url = fonte["url"].replace("{n}", str(p))
        lidos = ler_pagina(fonte, url)
        if lidos is None or (p > 1 and not lidos):
            if p > 1:
                st["fim"] = True
            break
        todos += lidos
        if p > 1:
            st["proxima"] = p + 1
            if p >= fonte.get("paginas", 1):
                st["fim"] = True
    return fonte, todos


def ler_arxiv():
    """Artigos científicos novos de robótica (arXiv cs.RO)."""
    try:
        raiz = ET.fromstring(A.baixar(ARXIV["url"], timeout=40))
    except Exception as e:
        print(f"  ! arXiv: {e}", file=sys.stderr)
        return []
    out = []
    for el in raiz.iter():
        if A._nome_local(el.tag) != "item":
            continue
        titulo = A.limpar_html(A._texto(el, "title"))
        link = A._texto(el, "link")
        desc = A.limpar_html(A._texto(el, "description"))
        desc = re.sub(r"^arXiv:\S+\s+Announce Type:\s*\w+\s*Abstract:\s*", "", desc)
        autores = A._texto(el, "creator")
        data = A.data_item(A._texto(el, "pubdate"))
        tipo_anuncio = A._texto(el, "announce_type")
        if not (titulo and link and data) or tipo_anuncio not in ("", "new"):
            continue
        out.append({"titulo": titulo, "link": link, "data": data, "resumo": A.cortar(desc, 420), "autores": A.cortar(autores, 160)})
    return out


def traduzir_item(x):
    t, ok1, lg = A.traduzir(x["to"])
    r, ok2, _ = A.traduzir(x["ro"]) if x.get("ro") else ("", True, "")
    if ok1 and ok2:
        x["t"], x["r"] = t, r
        x["lg"] = (lg or "en").split("-")[0].lower()
        x.pop("nt", None)
    return x


def main():
    print(f"Biblioteca — coleta em {A.AGORA:%d/%m/%Y %H:%M}")
    itens = carregar(ARQ_ITENS, [])
    estado = carregar(ARQ_ESTADO, {})
    # só fontes da lista (universidades de renome e grandes revistas) — nada do Brasil
    permitidas = {f["nome"] for f in FONTES}
    antes = len(itens)
    itens = [x for x in itens if x.get("f") in permitidas and x.get("pais") != "Brasil"]
    if antes != len(itens):
        print(f"Removidas {antes - len(itens)} matérias de fontes fora da lista")
    por_id = {x["id"]: x for x in itens}
    titulos = {re.sub(r"\W+", "", x.get("to", x["t"]).lower())[:80] for x in itens}

    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        resultados = list(ex.map(lambda f: coletar_fonte(f, estado), FONTES))

    novos = 0
    for fonte, lidos in resultados:
        for it in lidos:
            i = ident(it["link"])
            chave_t = re.sub(r"\W+", "", it["titulo"].lower())[:80]
            if i in por_id or chave_t in titulos:
                continue
            pt = fonte.get("lingua") == "pt" and A.idioma(it["titulo"] + " " + it["resumo"]) == "pt"
            x = {
                "id": i, "u": it["link"], "f": fonte["nome"], "tipo": fonte["tipo"], "pais": fonte["pais"],
                "d": it["data"].isoformat(timespec="minutes"), "i": it["imagem"] or "",
            }
            if fonte.get("inst"):
                x["inst"] = fonte["inst"]
            if pt:
                x["t"], x["r"] = it["titulo"], it["resumo"]
            else:
                x["to"], x["ro"], x["nt"] = it["titulo"], it["resumo"], 1
                x["t"], x["r"] = it["titulo"], it["resumo"]
            por_id[i] = x
            titulos.add(chave_t)
            itens.append(x)
            novos += 1
    print(f"Matérias novas: {novos}")

    # tradução pendente (mais recentes primeiro)
    pend = sorted([x for x in itens if x.get("nt")], key=lambda x: x["d"], reverse=True)[:LIMITE_TRADUCAO]
    if pend:
        print(f"Traduzindo {len(pend)} matérias...")
        with cf.ThreadPoolExecutor(max_workers=5) as ex:
            list(ex.map(traduzir_item, pend))

    # imagens que faltam (busca a imagem de destaque na página original)
    sem_img = sorted([x for x in itens if not x.get("i") and x.get("mx", 0) < 2], key=lambda x: x["d"], reverse=True)[:LIMITE_IMAGENS]
    if sem_img:
        print(f"Buscando imagem de {len(sem_img)} matérias...")

        def img(x):
            x["mx"] = x.get("mx", 0) + 1
            i, desc = A.meta_pagina(x["u"])
            if i:
                x["i"] = i
            if desc and not x.get("r") and not x.get("ro"):
                x["ro"] = desc
                x["nt"] = 1
            return x

        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            list(ex.map(img, sem_img))

    # categorias (mesmas regras das notícias) e curiosidade
    for x in itens:
        tt = x.get("to", "") + " | " + x["t"]
        x["c"] = A.classificar(tt, x.get("ro", "") + " " + x.get("r", ""))

    itens.sort(key=lambda x: x["d"], reverse=True)
    salvar_json(ARQ_ITENS, itens)
    salvar_json(ARQ_ESTADO, estado)

    # arquivo lido pelo site: só o que já está em português
    prontos = [{k: v for k, v in x.items() if k not in ("ro", "mx")} for x in itens if not x.get("nt")]
    meta = {"atualizado": A.AGORA.isoformat(timespec="minutes"), "total": len(prontos), "pendentes": len(itens) - len(prontos)}

    # arXiv: um arquivo por mês
    artigos = ler_arxiv()
    meses_arxiv = {}
    if artigos:
        chaves = {a["data"].strftime("%Y-%m") for a in artigos}
        for k in chaves:
            meses_arxiv[k] = carregar(os.path.join(PASTA_ARXIV, k + ".json"), [])
        ja = {a["id"] for lst in meses_arxiv.values() for a in lst}
        novos_art = []
        for a in artigos:
            i = ident(a["link"])
            if i in ja:
                continue
            novos_art.append({"id": i, "u": a["link"], "to": a["titulo"], "ro": a["resumo"], "au": a["autores"],
                              "d": a["data"].isoformat(timespec="minutes")})
        print(f"Artigos novos no arXiv: {len(novos_art)} (traduzindo...)")

        def trad_art(a):
            a["t"], ok1, _ = A.traduzir(a["to"])
            a["r"], ok2, _ = A.traduzir(a["ro"])
            if not (ok1 and ok2):
                a["nt"] = 1
            return a

        with cf.ThreadPoolExecutor(max_workers=5) as ex:
            novos_art = list(ex.map(trad_art, novos_art))
        for a in novos_art:
            a["c"] = A.classificar(a["to"] + " | " + a["t"], a["ro"])
            meses_arxiv[a["d"][:7]].append(a)
    # retraduz artigos que falharam antes e grava
    os.makedirs(PASTA_ARXIV, exist_ok=True)
    for nome in os.listdir(PASTA_ARXIV):
        if nome.endswith(".json") and nome[:-5] not in meses_arxiv:
            meses_arxiv[nome[:-5]] = carregar(os.path.join(PASTA_ARXIV, nome), [])
    resumo_arxiv = {}
    for k, lst in meses_arxiv.items():
        for a in lst:
            if a.get("nt"):
                t, ok1, _ = A.traduzir(a["to"])
                r, ok2, _ = A.traduzir(a["ro"])
                if ok1 and ok2:
                    a["t"], a["r"] = t, r
                    a.pop("nt", None)
        lst.sort(key=lambda a: a["d"], reverse=True)
        salvar_json(os.path.join(PASTA_ARXIV, k + ".json"), lst)
        pub = [{kk: vv for kk, vv in a.items() if kk not in ("ro",)} for a in lst if not a.get("nt")]
        with open(os.path.join(PASTA_ARXIV, k + ".js"), "w", encoding="utf-8") as f:
            f.write('window.CR_ARXIV=window.CR_ARXIV||{};CR_ARXIV["' + k + '"]=' + json.dumps(pub, ensure_ascii=False, separators=(",", ":")) + ";\n")
        resumo_arxiv[k] = len(pub)
    meta["arxiv"] = dict(sorted(resumo_arxiv.items()))

    with open(ARQ_JS, "w", encoding="utf-8") as f:
        f.write("window.CR_BIBLIOTECA=" + json.dumps({"meta": meta, "itens": prontos}, ensure_ascii=False, separators=(",", ":")) + ";\n")
    # resumo pequeno, carregado em todas as páginas (contadores das abas)
    meta_curta = {
        "atualizado": meta["atualizado"], "total": meta["total"],
        "universidades": sum(1 for x in prontos if x["tipo"] in ("universidade", "pesquisa", "periodico")),
        "arxiv": sum(resumo_arxiv.values()),
    }
    with open(os.path.join(PASTA, "meta.js"), "w", encoding="utf-8") as f:
        f.write("window.CR_BIB_META=" + json.dumps(meta_curta, ensure_ascii=False) + ";\n")
    print(f"Biblioteca: {meta['total']} matérias prontas | {meta['pendentes']} aguardando tradução | arXiv: {sum(resumo_arxiv.values())} artigos")


if __name__ == "__main__":
    main()
