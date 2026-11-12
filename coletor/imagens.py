# -*- coding: utf-8 -*-
"""
Central Robótica — banco de FOTOS.

Garante que nenhum card do site fique sem imagem. Ordem usada pelo site:
  1. a foto da própria matéria (og:image) — sempre a preferida;
  2. a foto da mesma notícia em outro site;
  3. uma FOTO ILUSTRATIVA real, com licença livre (Creative Commons), escolhida
     pelo assunto (robô citado, fabricante, categoria, marco da história...),
     sempre marcada como "Imagem ilustrativa" e com o crédito do autor.

As fotos ilustrativas vêm do Openverse (api.openverse.org), buscador de imagens
abertas. Fabricantes e sites especializados usam a imagem oficial do próprio site.
O banco cresce aos poucos (limite de buscas por execução) e fica em dados/imagens.js.

Uso:  python coletor/imagens.py   (o gerenciador.py já chama este script)
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atualizar as A  # noqa: E402

ARQ_JSON = os.path.join(A.RAIZ, "dados", "imagens.json")
ARQ_JS = os.path.join(A.RAIZ, "dados", "imagens.js")
ARQ_CATALOGO = os.path.join(A.RAIZ, "dados", "catalogo.js")
ARQ_CONTEUDO = os.path.join(A.RAIZ, "dados", "conteudo.js")

BUSCAS_POR_EXECUCAO = 45
INTERVALO = 1.5
UA_OPENVERSE = "CentralRobotica/1.0 (site de noticias de robotica)"

CATEGORIAS = {
    "cat:humanoides": "humanoid robot",
    "cat:quadrupedes": "robot dog",
    "cat:industriais": "industrial robot arm",
    "cat:drones": "drone quadcopter",
    "cat:casa": "service robot",
    "cat:medicina": "surgical robot",
    "cat:autonomos": "self-driving car",
    "cat:espaco": "mars rover",
    "cat:ia": "artificial intelligence robot",
    "cat:negocios": "robotics factory automation",
    "cat:geral": "robot",
    "cat:cobots": "collaborative robot",
    "cat:logistica": "warehouse robot",
    "cat:entrega": "delivery robot",
    "cat:servico": "restaurant robot",
    "cat:companhia": "social robot",
    "cat:exoesqueletos": "exoskeleton",
    "cat:agricolas": "agricultural robot",
    "cat:construcao": "construction robot",
    "cat:inspecao": "inspection robot",
    "cat:defesa": "military robot",
    "cat:resgate": "rescue robot",
    "cat:subaquaticos": "underwater robot",
    "cat:microrrobos": "soft robot",
    "cat:educacao": "educational robot",
    "cat:competicoes": "robot competition",
}

HISTORIA = {
    "O pombo de Arquitas": "Archytas", "Os autômatos de Heron": "Heron of Alexandria",
    "O livro de Al-Jazari": "Al-Jazari automata", "O cavaleiro de Leonardo": "Leonardo da Vinci robot",
    "O pato de Vaucanson": "Vaucanson duck", "Os autômatos Jaquet-Droz": "Jaquet-Droz automaton",
    "O tear programável": "Jacquard loom", "O barco de Tesla": "Nikola Tesla",
    "Nasce a palavra “robô”": "Karel Capek", "O robô vai ao cinema": "Metropolis 1927",
    "Elektro": "Elektro robot", "As Três Leis da Robótica": "Isaac Asimov",
    "As tartarugas de Grey Walter": "Grey Walter tortoise", "A patente de Devol": "Unimate",
    "Unimate entra na fábrica": "Unimate robot", "Shakey, o robô que pensa": "Shakey robot",
    "O braço de Stanford": "Stanford arm", "Lunokhod 1 na Lua": "Lunokhod",
    "WABOT-1 e o FAMULUS": "WABOT", "Braços robóticos em Marte": "Viking lander",
    "PUMA": "PUMA robot", "Canadarm": "Canadarm", "Honda começa os humanoides": "Honda robot P2",
    "Sojourner em Marte": "Sojourner rover", "LEGO Mindstorms": "LEGO Mindstorms",
    "AIBO": "Sony AIBO", "ASIMO e da Vinci": "ASIMO", "Roomba": "Roomba",
    "Spirit e Opportunity": "Opportunity rover", "Stanley e BigDog": "BigDog robot",
    "Começa o carro do Google": "Google self-driving car", "Robonaut 2 no espaço": "Robonaut",
    "Curiosity, Baxter e Kiva": "Curiosity rover", "Atlas": "Atlas robot",
    "Pepper": "Pepper robot", "HUBO vence o DARPA": "DARPA Robotics Challenge",
    "Sophia": "Sophia robot", "O mortal do Atlas": "Boston Dynamics Atlas",
    "Spot à venda e robotáxi sem motorista": "Boston Dynamics Spot",
    "Voo em Marte e Optimus": "Ingenuity helicopter", "IA generativa": "artificial intelligence",
    "Boom dos humanoides": "humanoid robot", "Atlas elétrico e humanoides acessíveis": "Unitree robot",
    "Robôs nas pistas e nas casas": "humanoid robot",
}
FATOS = {
    "A palavra “robô” nasceu no teatro": "Karel Capek", "“Robótica” foi inventada por um escritor": "Isaac Asimov",
    "O primeiro robô industrial foi para uma montadora": "Unimate", "Leonardo da Vinci projetou um robô": "Leonardo da Vinci robot",
    "Robôs há mais de 800 anos": "Al-Jazari automata", "O primeiro rover não foi em Marte": "Lunokhod",
    "Um helicóptero voou em outro planeta": "Ingenuity helicopter", "Um robô que andava e fumava em 1939": "Elektro robot",
    "Coreia do Sul lidera em robôs por trabalhador": "industrial robots factory", "A China instala mais da metade dos robôs industriais": "industrial robot",
    "Uma robô recebeu cidadania": "Sophia robot", "Cirurgia robótica desde 2000": "da Vinci surgical robot",
    "Pombo a vapor na Grécia Antiga": "Archytas", "Robôs-tartaruga pensavam sozinhos em 1948": "Grey Walter tortoise",
    "O pato que “digeria”": "Vaucanson duck", "Um autômato que escreve há 250 anos": "Jaquet-Droz automaton",
    "Carro sem motorista venceu no deserto em 2005": "Stanley Stanford car", "Robôs já correram meia maratona": "humanoid robot",
    "Cão-robô de estimação desde 1999": "Sony AIBO", "Programação antes dos computadores": "Jacquard loom",
}
DOCS = {
    "Good Night Oppy": "Opportunity rover", "Roving Mars": "Spirit rover", "Hi, AI": "android robot",
    "Robolove": "android robot", "Plug & Pray": "Joseph Weizenbaum", "NOVA: Rise of the Robots": "DARPA Robotics Challenge",
    "The Truth About Killer Robots": "military robot", "The Age of A.I.": "artificial intelligence",
    "Lo and Behold: Reveries of the Connected World": "robot soccer", "AlphaGo": "AlphaGo",
    "The Thinking Game": "DeepMind", "iHuman": "artificial intelligence", "BattleBots": "BattleBots",
}


def ler_catalogo():
    """Extrai robôs, fabricantes e sites do dados/catalogo.js (uma entrada por linha)."""
    txt = open(ARQ_CATALOGO, encoding="utf-8").read()
    robos, fabs, sites = [], [], []
    for linha in txt.splitlines():
        m = re.search(r'\{ nome: "([^"]+)", fab: "([^"]+)", tipo: "([^"]+)"', linha)
        if m:
            b = re.search(r'busca: "([^"]+)"', linha)
            robos.append({"nome": m.group(1), "fab": m.group(2), "tipo": m.group(3), "busca": (b.group(1) if b else m.group(1)).split("|")[0]})
            continue
        m = re.search(r'\{ id: "([^"]+)", nome: "([^"]+)".*?site: "([^"]+)"', linha)
        if m:
            fabs.append({"id": m.group(1), "nome": m.group(2), "site": m.group(3)})
            continue
        m = re.search(r'\{ nome: "([^"]+)", url: "([^"]+)"', linha)
        if m:
            sites.append({"nome": m.group(1), "url": m.group(2)})
    return robos, fabs, sites


def buscar_openverse(q, n=8):
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({"q": q, "page_size": 20, "mature": "false"})
    req = urllib.request.Request(url, headers={"User-Agent": UA_OPENVERSE, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        dados = json.loads(r.read().decode("utf-8"))
    out = []
    for x in dados.get("results", []):
        if not x.get("id") or not x.get("url"):
            continue
        lic = (x.get("license") or "").upper()
        lic = "CC0" if lic == "CC0" else ("Domínio público" if lic == "PDM" else f"CC {lic} {x.get('license_version') or ''}".strip())
        out.append({
            "u": f"https://api.openverse.org/v1/images/{x['id']}/thumb/",
            "o": x["url"],
            "a": (x.get("creator") or "autor desconhecido")[:60],
            "l": lic,
            "p": x.get("foreign_landing_url") or x["url"],
        })
        if len(out) >= n:
            break
    return out


def main():
    print(f"Fotos — banco de imagens em {A.AGORA:%d/%m/%Y %H:%M}")
    banco = json.load(open(ARQ_JSON, encoding="utf-8")) if os.path.exists(ARQ_JSON) else {}
    robos, fabs, sites = ler_catalogo()

    # fila de buscas, por prioridade: categorias, história, curiosidades, documentários, robôs
    fila = list(CATEGORIAS.items())
    fila += [("hist:" + k, v) for k, v in HISTORIA.items()]
    fila += [("fato:" + k, v) for k, v in FATOS.items()]
    fila += [("doc:" + k, v) for k, v in DOCS.items()]
    fila += [("robo:" + r["nome"], r["busca"] + ("" if re.search(r"robot|drone|rover|car|vacuum|surg", r["busca"], re.I) else " robot")) for r in robos]
    fila += [("fabq:" + f["id"], f["nome"].split("(")[0].split("/")[0].strip() + " robot") for f in fabs]

    # mesmas buscas compartilham o resultado
    cache_q = {v["q"]: v["fotos"] for v in banco.values() if isinstance(v, dict) and v.get("q") and v.get("fotos")}
    feitas, bloqueado = 0, False
    for chave, q in fila:
        if chave in banco:
            continue
        if q in cache_q:
            banco[chave] = {"q": q, "fotos": cache_q[q]}
            continue
        if feitas >= BUSCAS_POR_EXECUCAO or bloqueado:
            continue
        try:
            fotos = buscar_openverse(q)
            banco[chave] = {"q": q, "fotos": fotos}
            cache_q[q] = fotos
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                bloqueado = True
                print("  Openverse limitou as buscas — continua na próxima execução")
            else:
                banco[chave] = {"q": q, "fotos": []}
        except Exception as e:
            print(f"  ! {q}: {str(e)[:60]}")
        feitas += 1
        if feitas % 10 == 0:
            salvar(banco)
            print(f"  {feitas} buscas feitas...")
        time.sleep(INTERVALO)

    salvar(banco)

    # imagem oficial dos fabricantes e dos sites especializados (og:image da página inicial), em paralelo
    alvos = [("fab:" + f["id"], "https://" + f["site"], f["nome"], "imagem do site oficial") for f in fabs]
    alvos += [("site:" + s["nome"], s["url"], s["nome"], "imagem do site") for s in sites]
    alvos = [a for a in alvos if a[0] not in banco]

    def og(alvo):
        k, url, nome, rot = alvo
        img, _ = A.meta_pagina(url)
        return k, {"q": url, "fotos": [{"u": img, "a": nome, "l": rot, "p": url}] if img else []}

    if alvos:
        import concurrent.futures as cf
        with cf.ThreadPoolExecutor(max_workers=12) as ex:
            for k, v in ex.map(og, alvos):
                banco[k] = v

    pub = salvar(banco)
    faltam = sum(1 for k, _ in fila if k not in banco)
    print(f"Banco de fotos: {len(pub)} assuntos com foto | buscas nesta rodada: {feitas} | assuntos ainda na fila: {faltam}")


def salvar(banco):
    with open(ARQ_JSON, "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=0)
    pub = {k: v["fotos"] for k, v in banco.items() if v.get("fotos")}
    with open(ARQ_JS, "w", encoding="utf-8") as f:
        f.write("window.CR_IMAGENS=" + json.dumps(pub, ensure_ascii=False, separators=(",", ":")) + ";\n")
    return pub


if __name__ == "__main__":
    main()
