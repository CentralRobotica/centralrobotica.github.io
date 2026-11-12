# -*- coding: utf-8 -*-
"""
Central Robótica — coletor de notícias.

Busca notícias de robótica do mundo todo em feeds RSS (Brasil, EUA, Europa,
América Latina, China, Japão, Coreia...), traduz para português o que vier em
outro idioma, classifica por categoria de robô, marca lançamentos, junta a
mesma notícia publicada por vários sites, calcula a relevância e grava o
histórico em dados/json/AAAA-MM.json (+ dados/meses/AAAA-MM.js lidos pelo site).

Uso:  python coletor/atualizar.py
Só usa a biblioteca padrão do Python (3.9+).
"""
import concurrent.futures as cf
import email.utils
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_JSON = os.path.join(RAIZ, "dados", "json")
PASTA_JS = os.path.join(RAIZ, "dados", "meses")
ARQ_INDICE = os.path.join(RAIZ, "dados", "indice.js")

BRASILIA = timezone(timedelta(hours=-3))  # Brasil sem horário de verão
AGORA = datetime.now(BRASILIA)
DIAS_MAX_ATRAS = 45  # ignora notícias mais antigas que isso
LIMITE_GOOGLE = 220  # links do Google Notícias resolvidos por execução (em fila, devagar)
INTERVALO_GOOGLE = 3.0  # segundos entre pedidos ao Google (evita bloqueio 429)
LIMITE_COMPLETAR = 400  # notícias completadas (imagem/resumo) por execução
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

# --------------------------------------------------------------------------- #
# FONTES (do mundo todo)
# --------------------------------------------------------------------------- #
REGIOES = {
    "pt": "hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "en": "hl=en-US&gl=US&ceid=US:en",
    "en-gb": "hl=en-GB&gl=GB&ceid=GB:en",
    "en-in": "hl=en-IN&gl=IN&ceid=IN:en",
    "en-au": "hl=en-AU&gl=AU&ceid=AU:en",
    "en-ca": "hl=en-CA&gl=CA&ceid=CA:en",
    "en-sg": "hl=en-SG&gl=SG&ceid=SG:en",
    "en-za": "hl=en-ZA&gl=ZA&ceid=ZA:en",
    "es": "hl=es-419&gl=MX&ceid=MX:es-419",
    "es-es": "hl=es&gl=ES&ceid=ES:es",
    "fr": "hl=fr&gl=FR&ceid=FR:fr",
    "de": "hl=de&gl=DE&ceid=DE:de",
    "it": "hl=it&gl=IT&ceid=IT:it",
    "zh": "hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    "zh-tw": "hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
    "ja": "hl=ja&gl=JP&ceid=JP:ja",
    "ko": "hl=ko&gl=KR&ceid=KR:ko",
}


def gnews(q, regiao="pt"):
    return {
        "url": "https://news.google.com/rss/search?q=" + urllib.parse.quote(q + " when:7d") + "&" + REGIOES[regiao],
        "filtrar": True,
        "lingua": "pt" if regiao == "pt" else "x",
    }


# filtrar=True  -> feed genérico; só entra o que for de robótica
# especial=True -> fonte especializada em robótica (ganha peso na relevância)
# lingua="pt"   -> já vem em português; qualquer outro valor -> traduzir
FONTES = [
    # Só veículos com credibilidade e reconhecimento mundial. Nada do Brasil.
    # ---------------- Grandes veículos de referência mundial (via Google Notícias, restrito aos sites) ----------------
    gnews('robot OR robotics OR humanoid (site:reuters.com OR site:apnews.com OR site:bloomberg.com OR site:ft.com OR site:wsj.com)', "en"),
    gnews('robot OR robotics OR humanoid (site:nytimes.com OR site:washingtonpost.com OR site:theguardian.com OR site:bbc.com OR site:cnn.com OR site:cnbc.com)', "en"),
    gnews('robot OR robotics OR humanoid (site:economist.com OR site:nature.com OR site:science.org OR site:technologyreview.com OR site:wired.com OR site:theverge.com)', "en"),
    gnews('robot OR robotics OR humanoid (site:scmp.com OR site:asia.nikkei.com OR site:dw.com OR site:aljazeera.com OR site:france24.com OR site:afp.com)', "en"),
    gnews('robot OR robotics OR humanoid (site:techcrunch.com OR site:spectrum.ieee.org OR site:arstechnica.com OR site:engadget.com OR site:newscientist.com OR site:forbes.com)', "en"),
    gnews('robot OR robotics OR humanoid (site:fortune.com OR site:businessinsider.com OR site:axios.com OR site:time.com OR site:npr.org OR site:latimes.com)', "en"),
    gnews('"robot dog" OR quadruped OR drone OR robotaxi OR "surgical robot" (site:reuters.com OR site:bloomberg.com OR site:theverge.com OR site:techcrunch.com OR site:wired.com OR site:cnbc.com)', "en"),
    gnews('robot OR robotique OR Roboter OR robot humanoide (site:lemonde.fr OR site:spiegel.de OR site:elpais.com OR site:dw.com OR site:france24.com)', "en"),
    # ---------------- Grandes veículos por região (buscas restritas a esses sites) ----------------
    # Américas
    gnews('robot OR robotics OR humanoid OR drone (site:usatoday.com OR site:nbcnews.com OR site:abcnews.go.com OR site:cbsnews.com OR site:politico.com OR site:apnews.com)', "en"),
    gnews('robot OR robotics OR humanoid OR drone (site:cbc.ca OR site:theglobeandmail.com OR site:thestar.com OR site:ctvnews.ca)', "en-ca"),
    gnews('robot OR robótica OR humanoide OR dron (site:eluniversal.com.mx OR site:milenio.com OR site:elfinanciero.com.mx OR site:clarin.com OR site:lanacion.com.ar OR site:infobae.com OR site:latercera.com OR site:eltiempo.com)', "es"),
    # Europa
    gnews('robot OR robotics OR humanoid OR drone (site:thetimes.co.uk OR site:telegraph.co.uk OR site:independent.co.uk OR site:news.sky.com OR site:euronews.com OR site:politico.eu)', "en-gb"),
    gnews('robot OR robotique OR humanoïde OR drone (site:lemonde.fr OR site:lefigaro.fr OR site:lesechos.fr OR site:france24.com OR site:liberation.fr)', "fr"),
    gnews('Roboter OR Robotik OR humanoid OR Drohne (site:spiegel.de OR site:zeit.de OR site:faz.net OR site:sueddeutsche.de OR site:handelsblatt.com OR site:dw.com)', "de"),
    gnews('robot OR robótica OR humanoide OR dron (site:elpais.com OR site:elmundo.es OR site:lavanguardia.com OR site:abc.es)', "es-es"),
    gnews('robot OR robotica OR umanoide OR drone (site:corriere.it OR site:repubblica.it OR site:ansa.it OR site:ilsole24ore.com)', "it"),
    gnews('robot OR robotics OR humanoid (site:nzz.ch OR site:swissinfo.ch OR site:nos.nl OR site:euronews.com)', "en"),
    # Ásia e Oriente Médio
    gnews('robot OR robotics OR humanoid OR drone (site:japantimes.co.jp OR site:nhk.or.jp OR site:kyodonews.net OR site:koreaherald.com OR site:koreajoongangdaily.joins.com OR site:yna.co.kr)', "en"),
    gnews('robot OR robotics OR humanoid OR drone (site:straitstimes.com OR site:channelnewsasia.com OR site:scmp.com OR site:caixinglobal.com OR site:taipeitimes.com OR site:focustaiwan.tw)', "en-sg"),
    gnews('robot OR robotics OR humanoid OR drone (site:timesofindia.indiatimes.com OR site:thehindu.com OR site:hindustantimes.com OR site:economictimes.indiatimes.com OR site:ndtv.com)', "en-in"),
    gnews('ロボット OR ヒューマノイド OR ドローン (site:nikkei.com OR site:asahi.com OR site:yomiuri.co.jp OR site:mainichi.jp OR site:nhk.or.jp)', "ja"),
    gnews('로봇 OR 휴머노이드 OR 드론 (site:yna.co.kr OR site:chosun.com OR site:joongang.co.kr OR site:donga.com OR site:hankyung.com)', "ko"),
    gnews('機器人 OR 人形機器人 OR 無人機 (site:cna.com.tw OR site:udn.com OR site:ltn.com.tw OR site:caixin.com)', "zh-tw"),
    gnews('robot OR robotics OR humanoid OR drone (site:aljazeera.com OR site:thenationalnews.com OR site:arabnews.com OR site:gulfnews.com OR site:timesofisrael.com OR site:haaretz.com)', "en"),
    # Oceania
    gnews('robot OR robotics OR humanoid OR drone (site:abc.net.au OR site:smh.com.au OR site:theaustralian.com.au OR site:nzherald.co.nz OR site:rnz.co.nz OR site:stuff.co.nz)', "en-au"),
    # África
    gnews('robot OR robotics OR humanoid OR drone (site:news24.com OR site:businesslive.co.za OR site:mg.co.za OR site:nation.africa OR site:ahram.org.eg)', "en-za"),
    # ---------------- Sites especializados e de tecnologia por região (buscas restritas) ----------------
    gnews('robot OR robotics OR humanoid OR drone (site:gizmodo.com OR site:mashable.com OR site:tomshardware.com OR site:digitaltrends.com OR site:venturebeat.com OR site:fastcompany.com)', "en"),
    gnews('robot OR robotics OR humanoid OR drone (site:robotics247.com OR site:automate.org OR site:automationworld.com OR site:dronexl.co OR site:popularmechanics.com OR site:electrek.co)', "en"),
    gnews('robot OR robotics OR humanoid OR drone (site:betakit.com OR site:mobilesyrup.com OR site:assemblymag.com OR site:techrepublic.com)', "en-ca"),
    gnews('robot OR robótica OR humanoide OR dron (site:xataka.com.mx OR site:fayerwayer.com OR site:xataka.com OR site:hipertextual.com)', "es"),
    gnews('robot OR robotics OR humanoid OR drone (site:theregister.com OR site:techradar.com OR site:sifted.eu OR site:tech.eu OR site:theengineer.co.uk OR site:eandt.theiet.org)', "en-gb"),
    gnews('Roboter OR Robotik OR humanoid OR Drohne (site:heise.de OR site:golem.de OR site:t3n.de OR site:robotik-produktion.de)', "de"),
    gnews('robot OR robotique OR humanoïde OR drone (site:01net.com OR site:numerama.com OR site:lesnumeriques.com OR site:usinenouvelle.com OR site:futura-sciences.com)', "fr"),
    gnews('robot OR robotica OR umanoide OR drone (site:wired.it OR site:tweakers.net)', "it"),
    gnews('ロボット OR ヒューマノイド OR ドローン (site:itmedia.co.jp OR site:watch.impress.co.jp OR site:ascii.jp OR site:robotstart.info)', "ja"),
    gnews('로봇 OR 휴머노이드 OR 드론 (site:zdnet.co.kr OR site:etnews.com OR site:thelec.net OR site:irobotnews.com)', "ko"),
    gnews('机器人 OR 人形机器人 OR 无人机 (site:36kr.com OR site:ithome.com OR site:leiphone.com OR site:jiqizhixin.com OR site:ofweek.com OR site:gg-robot.com)', "zh"),
    gnews('robot OR robotics OR humanoid OR drone (site:technode.com OR site:pandaily.com OR site:digitimes.com OR site:techinasia.com OR site:kr-asia.com OR site:e27.co)', "en-sg"),
    gnews('robot OR robotics OR humanoid OR drone (site:analyticsindiamag.com OR site:inc42.com OR site:yourstory.com OR site:gadgets360.com)', "en-in"),
    gnews('robot OR robotics OR humanoid OR drone (site:calcalistech.com OR site:wamda.com OR site:itnews.com.au OR site:startupdaily.net OR site:createdigital.org.au OR site:sciencealert.com)', "en-au"),
    gnews('robot OR robotics OR humanoid OR drone (site:techcabal.com OR site:techpoint.africa OR site:techcentral.co.za OR site:mybroadband.co.za OR site:disrupt-africa.com)', "en-za"),
    # ---------------- Busca geral em inglês (só entram os veículos aprovados) ----------------
    gnews('humanoid robot', "en"),
    gnews('"robot dog" OR "quadruped robot"', "en"),
    gnews('unveils robot OR launches robot OR "new robot"', "en"),
    gnews('"industrial robot" OR cobot OR "warehouse robot"', "en"),
    gnews('"surgical robot" OR exoskeleton', "en"),
    gnews('robotaxi OR "autonomous vehicle"', "en"),
    gnews('robotics startup funding', "en"),
    gnews('"robot documentary" OR "history of robots" OR "how robots work"', "en"),
    gnews('humanoid robot OR robotics', "en-gb"),
    # ---------------- Sites especializados em robótica (ficam todos, independente do tamanho) ----------------
    {"url": "https://www.therobotreport.com/feed/", "especial": True, "nome": "The Robot Report"},
    {"url": "https://www.humanoidsdaily.com/feed.xml", "especial": True, "nome": "Humanoids Daily"},
    {"url": "https://interestingengineering.com/news-sitemap.xml", "tipo": "sitemap", "secao": "/ai-robotics/",
     "especial": True, "filtrar": True, "nome": "Interesting Engineering"},
    {"url": "https://newatlas.com/robotics/index.rss", "especial": True, "nome": "New Atlas"},
    {"url": "https://robohub.org/feed/", "especial": True, "nome": "Robohub"},
    {"url": "https://techxplore.com/rss-feed/robotics-news/", "especial": True, "nome": "Tech Xplore"},
    {"url": "https://www.sciencedaily.com/rss/computers_math/robotics.xml", "especial": True, "nome": "ScienceDaily"},
    {"url": "https://www.livescience.com/feeds/tag/robots", "especial": True, "nome": "Live Science"},
    {"url": "https://roboticsandautomationnews.com/feed/", "especial": True, "nome": "Robotics & Automation News"},
    {"url": "https://www.roboticsbusinessreview.com/feed/", "especial": True, "nome": "Robotics Business Review"},
    {"url": "https://www.roboticstomorrow.com/rss/news.xml", "especial": True, "nome": "Robotics Tomorrow"},
    {"url": "https://www.mobilerobotguide.com/feed/", "especial": True, "nome": "Mobile Robot Guide"},
    {"url": "https://humanoid.guide/feed/", "especial": True, "nome": "Humanoid.guide"},
    {"url": "https://www.irobotnews.com/rss/allArticle.xml", "especial": True, "nome": "Robot Newspaper (Coreia)"},
    {"url": "https://dronedj.com/feed/", "especial": True, "nome": "DroneDJ"},
    {"url": "https://dronelife.com/feed/", "especial": True, "nome": "DroneLife"},
    {"url": "https://www.suasnews.com/feed/", "especial": True, "nome": "sUAS News"},
    # ---------------- Grandes veículos de ciência e tecnologia ----------------
    {"url": "https://spectrum.ieee.org/feeds/topic/robotics.rss", "especial": True, "nome": "IEEE Spectrum"},
    {"url": "https://techcrunch.com/category/robotics/feed/", "especial": True, "nome": "TechCrunch"},
    {"url": "https://www.zdnet.com/topic/robotics/rss.xml", "especial": True, "nome": "ZDNET"},
    {"url": "https://www.newscientist.com/subject/robotics/feed/", "especial": True, "nome": "New Scientist"},
    # ---------------- Grandes veículos (feeds diretos, filtrados por robótica) ----------------
    {"url": "https://www.theguardian.com/technology/robots/rss", "especial": True, "nome": "The Guardian"},
    {"url": "https://feeds.bbci.co.uk/news/technology/rss.xml", "filtrar": True, "nome": "BBC News"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "filtrar": True, "nome": "The New York Times"},
    {"url": "https://www.ft.com/technology?format=rss", "filtrar": True, "nome": "Financial Times"},
    {"url": "https://www.economist.com/science-and-technology/rss.xml", "filtrar": True, "nome": "The Economist"},
    {"url": "https://www.cnbc.com/id/19854910/device/rss/rss.html", "filtrar": True, "nome": "CNBC"},
    {"url": "https://www.technologyreview.com/feed/", "filtrar": True, "nome": "MIT Technology Review"},
    {"url": "https://feeds.arstechnica.com/arstechnica/index", "filtrar": True, "nome": "Ars Technica"},
    {"url": "https://www.theverge.com/rss/index.xml", "filtrar": True, "nome": "The Verge"},
    {"url": "https://www.engadget.com/rss.xml", "filtrar": True, "nome": "Engadget"},
    {"url": "https://www.scmp.com/rss/36/feed", "filtrar": True, "nome": "South China Morning Post"},
]

# --------------------------------------------------------------------------- #
# CATEGORIAS (regex aplicadas ao título original + título traduzido + resumo)
# --------------------------------------------------------------------------- #
CATEGORIAS = {
    "humanoides": [
        r"humanoid", r"humanóide", r"humanoide", r"humanoïde", r"umanoide", r"optimus", r"figure ?0\d",
        r"figure ai", r"unitree (?:g1|h1|h2|r1)", r"agility robotics", r"digit robot", r"apptronik",
        r"apollo robot", r"1x (?:neo|technologies)", r"neo gamma", r"ubtech", r"walker s", r"agibot",
        r"fourier gr", r"xpeng iron", r"tesla bot", r"atlas (?:humanoid|robot)", r"robô atlas",
        r"sanctuary ai", r"boston dynamics.{0,40}atlas", r"robôs? bípede", r"bipedal", r"android robot",
        r"robô androide", r"ameca", r"engineered arts", r"booster t1", r"galbot", r"kepler k2",
        r"人形", r"ヒューマノイド", r"휴머노이드",
    ],
    "quadrupedes": [
        r"robot dogs?\b", r"robotic dogs?\b", r"robo-?dogs?\b", r"quadruped", r"quadrúpede",
        r"c[ãa]es?[- ]rob[ôo]", r"cachorros?[- ]rob[ôo]", r"cachorro robótico", r"cão robótico",
        r"perros? robot", r"chiens? robot", r"roboterhund", r"cane robot",
        r"unitree (?:go\d|b\d|a2)", r"spot robot", r"robô spot", r"boston dynamics.{0,40}spot\b",
        r"anymal", r"anybotics", r"deep robotics", r"ghost robotics", r"vision 60", r"lite3",
        r"legged robot", r"robôs? com pernas", r"robô de quatro patas", r"four-legged",
        r"机器狗", r"機器狗", r"四足", r"로봇개", r"사족",
    ],
    "industriais": [
        r"industrial robot", r"robôs? industria", r"robotic arm", r"braços? robótico", r"braço mecânico",
        r"manufactur", r"fábrica", r"factory", r"linha de montagem", r"assembly line", r"fanuc", r"abb robotics",
        r"kuka", r"yaskawa", r"kawasaki robotics", r"automação industrial", r"industrial automation",
        r"welding robot", r"robôs? de solda", r"chão de fábrica", r"indústria 4\.0", r"industry 4\.0",
        r"montadora", r"automaker", r"工业机器人", r"産業用ロボット", r"Industrieroboter",
    ],
    "drones": [
        r"drones?\b", r"vants?\b", r"uavs?\b", r"quadric[oó]ptero", r"quadcopter", r"\bdji\b",
        r"multicopter", r"evtol", r"carros? voador", r"flying car", r"aeronave não tripulada", r"无人机", r"ドローン", r"드론",
    ],
    "casa": [
        r"robot vacuum", r"robotic vacuum", r"aspirador robô", r"robôs? aspirador", r"roomba", r"irobot",
        r"roborock", r"ecovacs", r"dreame", r"robot (?:lawn ?)?mower", r"cortador de grama", r"lawn mower",
        r"home robot", r"household robot", r"robôs? doméstico", r"robô para casa", r"tarefas domésticas",
        r"household chores", r"house ?work", r"lavar louça", r"dishwash", r"laundry", r"dobrar roupa",
        r"pool clean", r"limpador de piscina", r"window clean", r"limpa-vidros", r"smart home", r"casa inteligente",
        r"扫地机器人", r"掃除ロボット",
    ],
    "medicina": [
        r"surgical robot", r"robotic surgery", r"robot-assisted surg", r"cirurgias? robótica",
        r"robôs? cirúrgico", r"da vinci", r"intuitive surgical", r"medical robot", r"robôs? médico",
        r"hospital", r"cirurgião", r"surgeon", r"surgery", r"cirurgia", r"patient", r"paciente",
        r"healthcare", r"saúde", r"pharmacy", r"farmácia", r"diagnos", r"medtronic", r"stryker",
    ],
    "autonomos": [
        r"robotaxi", r"robotáxi", r"robo-?taxi", r"self-driving", r"driverless", r"autonomous vehicle",
        r"autonomous car", r"autonomous truck", r"veículos? autônomo", r"carros? autônomo",
        r"caminhões? autônomo", r"ônibus autônomo", r"waymo", r"zoox", r"tesla fsd",
        r"full self-driving", r"pony\.ai", r"baidu apollo", r"aurora innovation", r"sem motorista", r"自动驾驶",
    ],
    "espaco": [
        r"space robot", r"robôs? espacia", r"rover", r"\bnasa\b", r"esa\b", r"mars\b", r"marte\b", r"lunar",
        r"moon\b", r"\blua\b", r"estação espacial", r"space station", r"\biss\b", r"satélite", r"satellite",
        r"asteroid", r"órbita", r"orbit", r"spacecraft", r"nave espacial", r"astronaut", r"astronauta", r"jaxa",
    ],
    "cobots": [
        r"cobots?\b", r"collaborative robot", r"robôs? colaborativo", r"universal robots", r"fanuc crx",
        r"doosan robotics", r"techman robot", r"franka", r"neura robotics", r"standard bots", r"work alongside humans",
        r"trabalhar ao lado", r"human-robot collaboration", r"colaboração humano-robô",
    ],
    "logistica": [
        r"warehouse", r"armazém", r"armazens", r"centro de distribuição", r"distribution center", r"fulfil?lment",
        r"logístic", r"logistics", r"intralogist", r"palletiz", r"paletiz", r"amrs?\b", r"agvs?\b",
        r"autonomous mobile robot", r"robôs? móve(?:l|is)", r"picking", r"order picking", r"sorting robot",
        r"amazon robotics", r"proteus", r"locus robotics", r"symbotic", r"ocado", r"geek\+", r"geekplus",
        r"forklift", r"empilhadeira", r"truck unloading", r"descarreg", r"supply chain", r"cadeia de suprimentos",
        r"parcel", r"encomendas", r"stretch robot",
    ],
    "entrega": [
        r"delivery robot", r"robôs? de entrega", r"robôs? entregador", r"last[- ]mile", r"última milha",
        r"starship technologies", r"serve robotics", r"kiwibot", r"\bnuro\b", r"coco robotics", r"sidewalk robot",
        r"drone delivery", r"delivery drone", r"entrega por drone", r"drones? de entrega", r"zipline", r"wing aviation",
        r"food delivery", r"entrega de comida", r"doordash", r"uber eats", r"meituan", r"entregas? (?:de|por|com) robôs?",
    ],
    "servico": [
        r"service robots?", r"robôs? de serviço", r"waiter robot", r"garçom robô", r"robô garçom", r"serving robot",
        r"restaurant", r"restaurante", r"hotel", r"aeroporto", r"airport", r"varejo", r"retail", r"supermarket",
        r"supermercado", r"convenience store", r"loja de conveniência", r"cleaning robot", r"robôs? de limpeza",
        r"receptionist", r"recepcionista", r"pudu", r"keenon", r"bear robotics", r"bellabot", r"barista",
        r"robot chef", r"robotic kitchen", r"cozinha robótica", r"hospitality", r"hotelaria", r"shopping mall",
    ],
    "companhia": [
        r"companion robot", r"robô de companhia", r"social robot", r"robôs? socia", r"elderly", r"idosos?",
        r"terceira idade", r"elder care", r"cuidado de idosos", r"loneliness", r"solidão", r"emotional", r"emoç",
        r"pet robot", r"robô de estimação", r"aibo", r"caregiver", r"cuidador", r"therapy robot", r"terapia",
        r"autism", r"autismo", r"\bparo\b", r"empath", r"empatia", r"friendship", r"amizade",
    ],
    "exoesqueletos": [
        r"exoskeleton", r"exoesqueleto", r"exosuit", r"prosthe", r"prótese", r"bionic (?:arm|leg|hand)",
        r"braço biônico", r"perna biônica", r"mão biônica", r"rehabilitation", r"reabilitação", r"wearable robot",
        r"robô vestível", r"paraplegi", r"paraplég", r"spinal cord", r"medula", r"ekso", r"rewalk", r"cyberdyne",
        r"amputee", r"amputad",
    ],
    "agricolas": [
        r"agricultur", r"agrícola", r"agronegócio", r"\bfarm", r"fazenda", r"harvest", r"colheita", r"tractor",
        r"trator", r"\bcrops?\b", r"lavoura", r"plantação", r"weeding", r"capina", r"pulveriz", r"crop spraying",
        r"dairy", r"ordenha", r"milking", r"orchard", r"pomar", r"greenhouse", r"estufa", r"john deere",
        r"carbon robotics", r"monarch tractor", r"agras", r"livestock", r"pecuária", r"vineyard", r"vinhedo",
        r"agtech", r"agritech",
    ],
    "construcao": [
        r"construction", r"construção civil", r"canteiro de obras", r"building site", r"bricklay", r"alvenaria",
        r"tijolos?", r"3d[- ]print(?:ed|ing)? (?:house|home|building)", r"impressão 3d de (?:casas?|prédios?)",
        r"excavator", r"escavadeira", r"demolition", r"demolição", r"concrete", r"concreto", r"built robotics",
        r"dusty robotics", r"canvas construction", r"hilti", r"construction site", r"obras? civis?",
    ],
    "inspecao": [
        r"inspection", r"inspeção", r"inspect", r"patrol", r"patrulha", r"security robot", r"robôs? de segurança",
        r"surveillance", r"vigilância", r"power plant", r"usina", r"pipeline", r"oleoduto", r"gasoduto",
        r"oil and gas", r"petróleo e gás", r"substation", r"subestação", r"tunnel", r"túnel", r"nuclear",
        r"anybotics", r"anymal", r"knightscope", r"maintenance robot", r"robôs? de manutenção", r"offshore",
    ],
    "defesa": [
        r"military", r"militar", r"defen[cs]e", r"defesa", r"army", r"exército", r"soldier", r"soldado",
        r"battlefield", r"campo de batalha", r"pentagon", r"pentágono", r"darpa", r"unmanned ground vehicle",
        r"\bugvs?\b", r"weapon", r"armamento", r"combat", r"combate", r"ghost robotics", r"anduril",
        r"loitering munition", r"navy", r"marinha", r"air force", r"força aérea", r"warfare",
    ],
    "resgate": [
        r"rescue", r"resgate", r"disaster", r"desastre", r"firefight", r"bombeiro", r"incêndio", r"wildfire",
        r"earthquake", r"terremoto", r"search and rescue", r"busca e salvamento", r"emergency", r"emergência",
        r"flood", r"enchente", r"inundação", r"lifeguard", r"salva-vidas", r"hazmat", r"first responder",
        r"socorrista", r"collapsed building", r"escombros",
    ],
    "subaquaticos": [
        r"underwater", r"subaquático", r"submarin", r"\bocean", r"oceano", r"marine", r"marinho", r"\brov\b",
        r"\bauvs?\b", r"seabed", r"fundo do mar", r"deep sea", r"mar profundo", r"autonomous (?:boat|ship|vessel)",
        r"barcos? autônomo", r"navios? autônomo", r"robotic fish", r"peixe robô", r"saildrone", r"coral reef",
        r"recife de coral", r"shipwreck", r"naufrágio",
    ],
    "microrrobos": [
        r"microrobot", r"micro-robot", r"microrrobô", r"nanorobot", r"nanorrobô", r"nanorobô", r"soft robot",
        r"robôs? macio", r"robô mole", r"swarm", r"enxame", r"bioinspired", r"bio-inspired", r"bioinspirad",
        r"insect robot", r"robô inseto", r"tiny robot", r"minúsculo", r"microscópic", r"origami robot",
        r"jellyfish robot", r"shape-shifting", r"artificial muscle", r"músculo artificial",
    ],
    "educacao": [
        r"educational robot", r"robôs? educaciona", r"school", r"escola", r"students?", r"alunos?", r"estudantes",
        r"classroom", r"sala de aula", r"\bstem\b", r"\blego\b", r"\bkids\b", r"crianças", r"toy robot",
        r"brinquedo", r"teaching", r"ensino", r"vex robotics", r"makeblock", r"robot kit", r"kit de robótica",
    ],
    "competicoes": [
        r"competition", r"competição", r"campeonato", r"championship", r"olympic", r"olimpíada", r"robot games",
        r"jogos mundiais", r"marathon", r"maratona", r"tournament", r"torneio", r"robocup", r"robot soccer",
        r"futebol de robôs", r"boxing", r"boxe", r"robot race", r"corrida de robôs", r"darpa .{0,15}challenge",
        r"\bexpo\b", r"feira", r"conference", r"conferência", r"summit", r"\bces\b", r"world robot conference",
        r"\biros\b", r"\bicra\b", r"automatica", r"robobusiness", r"exhibition", r"exposição", r"fair\b",
    ],
    "ia": [
        r"embodied ai", r"physical ai", r"ia física", r"ia incorporada", r"inteligência artificial física",
        r"robot learning", r"foundation model", r"modelo de fundação", r"vla\b", r"vision-language-action",
        r"gemini robotics", r"nvidia (?:isaac|gr00t|cosmos|jetson)", r"gr00t", r"reinforcement learning",
        r"aprendizado por reforço", r"pesquisador", r"researcher", r"universidade", r"university",
        r"laboratório", r"laboratory", r"\bmit\b", r"stanford", r"carnegie mellon", r"eth zurich",
        r"soft robot", r"robôs? mole", r"robôs? macio", r"estudo", r"study", r"artigo científico",
        r"open-source", r"código aberto", r"具身智能", r"inteligência incorporada", r"inteligente incorporad",
        r"robôs? inteligentes", r"intelligent robot", r"embodied intelligence", r"modelo de robô", r"cérebro de robô",
        r"robot brain", r"world model", r"modelo de mundo", r"simulação", r"simulation",
    ],
    "negocios": [
        r"funding", r"raises \$", r"raised \$", r"investment", r"investimento", r"aporte", r"rodada",
        r"series [a-e]\b", r"série [a-e]\b", r"acquisition", r"acquires", r"aquisição", r"adquire",
        r"\bipo\b", r"valuation", r"avaliada em", r"bilhões", r"billion", r"milhões", r"million",
        r"startup", r"mercado de robôs", r"robotics market", r"ações", r"shares", r"receita",
        r"revenue", r"parceria", r"partnership", r"contrato", r"tarifa", r"tariff", r"融资",
    ],
}

# Lançamento = verbo de lançamento PERTO de um produto robótico (evita "lança plano", "revela estudo")
_VERBO_LANC = (
    r"(?:lança|lançou|lançam|lançamento|lançará|lançada|lançado|apresenta|apresentou|apresentam|revela|revelou|"
    r"estreia|estreou|anuncia|anunciou|chega ao mercado|chegou ao mercado|começa a vender|pré-venda|à venda|"
    r"unveil|launch|debut|introduc|reveal|announc|goes on sale|on sale|pre-order|preorder|first look|"
    r"releases|released|rolls out|showcases|presenta|lanza|dévoile|lance|stellt|vorgestellt|präsentiert)"
)
_ADJ_NOVO = r"(?:novo|nova|novos|novas|new|next-gen|next generation|nueva|nuevo|nouveau|nouvelle|neue[rn]?|latest|última|último)"
_PRODUTO = (
    r"(?:rob[ôo]s?|robots?|robotic|humanoid\w*|humanóide\w*|humanoide\w*|cães?-rob[ôo]|robot ?dogs?|quadruped\w*|"
    r"quadrúpede\w*|drones?|aspirador\w*|vacuum|cobots?|braço|robotic arm|exoesqueleto|exoskeleton|"
    r"robotáxi|robotaxi|androide|android robot|mão robótica|robotic hand|gera[çc][ãa]o|generation|gen ?\d|"
    r"vers[ãa]o|version|modelo|model|optimus|atlas|spot|unitree|figure 0\d|digit|apollo|neo|walker|"
    r"cyberdog|aibo|roomba|da vinci|cybercab)"
)
LANCAMENTO = re.compile(
    r"(?<!\w)" + _VERBO_LANC + r"\b(?:\W+\w+){0,6}?\W+" + _PRODUTO + r"(?!\w)"
    r"|(?<!\w)" + _PRODUTO + r"\b(?:\W+\w+){0,6}?\W+" + _VERBO_LANC
    + r"|(?<!\w)" + _ADJ_NOVO + r"\b(?:\W+\w+){0,2}?\W+" + _PRODUTO + r"(?!\w)"
    + r"|(?<!\w)" + _PRODUTO + r"\W+" + _ADJ_NOVO + r"(?!\w)"
    + r"|(?:发布|発表|발표|출시|公開|亮相|推出)",
    re.I,
)
_NAO_LANC = re.compile(
    r"(?<!\w)(?:plano|plan|programa|program|estudo|study|pesquisa revela|parceria|partnership|fundo|fund|"
    r"relatório|report|competição|competition|campeonato|olimpíada|olympics|feira|festival|curso|course|"
    r"edital|política|policy|lei\b|law\b|regulation|regulamenta)",
    re.I,
)


CURIOSIDADE = re.compile(
    r"(?<!\w)(?:curiosidade|você sabia|sabia que|como funciona|entenda|explica|explicad|história d[aeo]s? rob|"
    r"história da robótica|documentário|série documental|museu|recorde|record-breaking|world record|bizarr|"
    r"incrível|surpreendente|impressionante|fun fact|did you know|how .{0,40}works?|explained|explainer|"
    r"history of|documentary|docuseries|museum|world'?s first|primeir[oa] .{0,25}do mundo|"
    r"maior robô|menor robô|smallest robot|largest robot|tiniest|weird|strange|inspirad[oa] em animal|"
    r"bioinspired|bio-inspired|inspired by (?:nature|animals|insects)|curious|fascinating)",
    re.I,
)
DOCUMENTARIO = re.compile(r"(?<!\w)(?:documentário|documentary|docuseries|série documental|documental|documentaire|dokumentarfilm)", re.I)


_CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯＀-￯]+")


def eh_lancamento(texto):
    # títulos em chinês/japonês/coreano são avaliados pela tradução em português
    texto = _CJK.sub(" ", texto)
    m = LANCAMENTO.search(texto)
    if not m:
        return False
    # se o trecho do "lançamento" fala de plano/estudo/parceria, não é lançamento de robô
    trecho = texto[max(0, m.start() - 20): m.end() + 30]
    return not _NAO_LANC.search(trecho)

BASE_ROBOTICA = re.compile(
    r"(?<!\w)(?:rob[ôoó]|robot|humanoid|humanoide|humanóide|humanoïde|umanoide|drone|cobot|exoesqueleto|"
    r"exoskeleton|robotáxi|robotaxi|self-driving|carro autônomo|veículo autônomo|autonomous vehicle|"
    r"quadruped|quadrúpede|vant\b|uav\b|braço mecânico|automação|robotique|roboter|robotik|robótica|"
    r"robotica)|机器|機器|ロボット|ヒューマノイド|로봇|휴머노이드",
    re.I,
)

EXCLUIR = re.compile(
    r"(?<!\w)(?:forex|day ?trade|trading|apostas?\b|bet\b|bets\b|cassino|casino|criptomoeda|bitcoin|"
    r"robôs? investidor|robôs? de investimento|robô do pix|golpe do robô|mr\.? robot|robocall|"
    r"robocop|transformers|robô trader|robôs? de trade|chatbot|robô de whatsapp|robô de mensagens|"
    r"horóscopo|robozão)",
    re.I,
)

GUERRA = re.compile(
    r"(?<!\w)(?:ataques?|attacks?|strikes?|abatid|shot down|guerra|war\b|míssil|missile|kamikaze|bomb|"
    r"ucrânia|ukrain|rússia|russia|israel|gaza|irã|iran|militar|military|exército|army|pentagon|defesa aérea)",
    re.I,
)

# ataques e mortes com drones (guerra): fora do escopo do site, mesmo na aba Defesa
ATAQUE = re.compile(
    r"ataques? (?:de|com) drones?|drones? (?:attack|strike)s?|drone strikes?|interceptad|abatid|shot down|"
    r"mort[oa]s? em ataque|killed in .{0,25}attack|deixa \d+ (?:soldados )?mortos|mata \d+",
    re.I,
)

ESPECIAL_CATS = {"humanoides": 0.8, "quadrupedes": 0.8}
FISICAS = {"humanoides", "quadrupedes", "industriais", "drones", "casa", "medicina", "autonomos", "espaco",
           "cobots", "logistica", "entrega", "servico", "companhia", "exoesqueletos", "agricolas", "construcao",
           "inspecao", "defesa", "resgate", "subaquaticos", "microrrobos", "educacao"}

_CAT_RX = {c: re.compile(r"(?<!\w)(?:" + "|".join(lst) + ")", re.I) for c, lst in CATEGORIAS.items()}

STOP = set(
    "a o e de da do das dos em no na nos nas um uma para por com que se ao à as os é foi ser seu sua "
    "the and of to in on for with by at from is are as its it this that new novo nova after how why "
    "robot robots robô robôs robotics robótica".split()
)

# --------------------------------------------------------------------------- #
# UTILITÁRIOS
# --------------------------------------------------------------------------- #
def baixar(url, timeout=20, limite=4_000_000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(limite)


def limpar_html(txt):
    if not txt:
        return ""
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", txt)
    txt = re.sub(r"(?s)<[^>]+>", " ", txt)
    txt = html.unescape(html.unescape(txt))
    txt = re.sub(r"\s+", " ", txt).strip()
    txt = re.sub(r"The post .{0,250}? appeared first on .{0,120}?\.?$", "", txt).strip()
    txt = re.sub(r"O post .{0,250}? apareceu primeiro em .{0,120}?\.?$", "", txt).strip()
    txt = re.sub(r"(?:Continue reading|Read more|Leia mais|Continue lendo).{0,80}$", "", txt).strip()
    txt = re.sub(r"\[\s*(?:…|\.\.\.)\s*\]", "…", txt)
    return txt


def cortar(txt, n=300):
    if len(txt) <= n:
        return txt
    corte = txt[:n].rsplit(" ", 1)[0]
    return corte.rstrip(",.;:—-") + "…"


def normalizar_url(u):
    try:
        p = urllib.parse.urlsplit(u.strip())
        q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not k.lower().startswith(("utm_", "fbclid", "gclid"))]
        return urllib.parse.urlunsplit((p.scheme, p.netloc.lower(), p.path.rstrip("/"), urllib.parse.urlencode(q), ""))
    except Exception:
        return u


def dominio(url):
    try:
        d = urllib.parse.urlsplit(url).netloc.lower()
        return d[4:] if d.startswith("www.") else d
    except Exception:
        return ""


def tokens(titulo):
    palavras = re.findall(r"[a-zà-ÿ0-9]+", (titulo or "").lower())
    return {w for w in palavras if len(w) > 2 and w not in STOP}


def parecido(a, b):
    """Semelhança entre dois títulos. Exige ao menos 2 palavras em comum: títulos em chinês,
    japonês ou coreano só têm números/siglas latinas ("2026") e não podem ser juntados por isso."""
    if not a or not b or len(a & b) < 2:
        return 0.0
    return len(a & b) / len(a | b)


def idioma(txt):
    """Heurística simples: devolve 'pt' só quando há sinal claro de português."""
    t = " " + txt.lower() + " "
    if re.search(r"[぀-ヿ一-鿿가-힯]", t):
        return "outro"
    pt = sum(t.count(w) for w in (" de ", " do ", " da ", " que ", " um ", " uma ", " para ", " com ", " não ", " os ", " no ", " na ", " em "))
    pt += 2 * len(re.findall(r"ção|ções|ões|ã|õ", t))
    en = sum(t.count(w) for w in (" the ", " and ", " of ", " to ", " with ", " for ", " is ", " its ", " on ", " in ", " new ", " how "))
    es = sum(t.count(w) for w in (" el ", " los ", " las ", " del ", " y ", " es ", " una ", " con ", " por el ")) + 2 * t.count("ñ")
    return "pt" if pt >= 2 and pt > en and pt > es else "outro"


def data_item(txt):
    if not txt:
        return None
    txt = txt.strip()
    try:
        d = email.utils.parsedate_to_datetime(txt)
    except Exception:
        d = None
    if d is None:
        try:
            d = datetime.fromisoformat(txt.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(BRASILIA)


def limpar_fonte(nome):
    nome = re.sub(r"\s*[-–|:]\s*(Robotics|Robótica|RSS|Feed|Notícias|Latest).*$", "", nome or "", flags=re.I)
    return nome.strip()[:60] or "Fonte desconhecida"


# --------------------------------------------------------------------------- #
# LEITURA DOS FEEDS
# --------------------------------------------------------------------------- #
def _nome_local(tag):
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


def _filho(el, nome):
    for c in el:
        if _nome_local(c.tag) == nome:
            return c
    return None


def _texto(el, nome):
    c = _filho(el, nome)
    return (c.text or "").strip() if c is not None and c.text else ""


def _imagem_do_item(el, html_bruto):
    for c in el.iter():
        n = _nome_local(c.tag)
        if n in ("content", "thumbnail") and c.get("url"):
            if n == "thumbnail" or (c.get("medium") in (None, "image") and not (c.get("type") or "").startswith("video")):
                return c.get("url")
        if n == "enclosure" and (c.get("type") or "").startswith("image") and c.get("url"):
            return c.get("url")
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html_bruto or "", re.I)
    if m and not m.group(1).startswith("data:"):
        return html.unescape(m.group(1))
    return ""


def ler_sitemap(fonte, raiz):
    """Lê um 'news sitemap' (Google News) e fica só com a seção pedida."""
    itens = []
    for el in raiz:
        if _nome_local(el.tag) != "url":
            continue
        loc = _texto(el, "loc")
        if fonte.get("secao") and fonte["secao"] not in loc:
            continue
        titulo = data = imagem = ""
        for c in el.iter():
            n = _nome_local(c.tag)
            if n == "title" and c.text:
                titulo = limpar_html(c.text)
            elif n == "publication_date" and c.text:
                data = c.text
            elif n == "loc" and c is not el and c.text and "image" in (c.tag or ""):
                imagem = c.text.strip()
        data = data_item(data or _texto(el, "lastmod"))
        if not (loc and titulo and data):
            continue
        p = urllib.parse.urlsplit(loc)
        itens.append({
            "titulo": titulo, "link": loc, "data": data, "resumo": "", "imagem": imagem,
            "fonte": fonte.get("nome", p.netloc), "site": f"{p.scheme}://{p.netloc}",
            "especial": fonte.get("especial", False), "filtrar": fonte.get("filtrar", False),
            "google": False, "lingua_feed": fonte.get("lingua", "x"),
        })
    print(f"  {len(itens):3d} itens  {fonte.get('nome', fonte['url'])[:60]}")
    return itens


def ler_feed(fonte):
    url = fonte["url"]
    try:
        raiz = ET.fromstring(baixar(url, timeout=60, limite=16_000_000))
    except Exception as e:
        print(f"  ! falhou {url[:90]}: {e}", file=sys.stderr)
        STATUS_FONTES[fonte.get("nome") or url[:80]] = -1
        return []
    STATUS_FONTES[fonte.get("nome") or url[:80]] = 1
    if fonte.get("tipo") == "sitemap":
        return ler_sitemap(fonte, raiz)
    eh_google = "news.google.com" in url
    canal = _filho(raiz, "channel")
    titulo_canal = _texto(canal, "title") if canal is not None else _texto(raiz, "title")
    if fonte.get("nome"):
        titulo_canal = fonte["nome"]
    itens = []
    for el in raiz.iter():
        if _nome_local(el.tag) not in ("item", "entry"):
            continue
        titulo = limpar_html(_texto(el, "title"))
        link = _texto(el, "link")
        if not link:
            l = _filho(el, "link")
            if l is not None:
                link = l.get("href", "")
        corpo = ""
        for nome in ("encoded", "description", "summary", "content"):
            c = _filho(el, nome)
            if c is not None and (c.text or "").strip():
                corpo = c.text
                break
        data = data_item(_texto(el, "pubdate") or _texto(el, "published") or _texto(el, "updated") or _texto(el, "date"))
        fonte_nome, site = titulo_canal, ""
        resumo = limpar_html(corpo)
        imagem = _imagem_do_item(el, corpo)
        if eh_google:
            src = _filho(el, "source")
            if src is not None and src.text:
                fonte_nome = src.text.strip()
                site = src.get("url", "")
                titulo = re.sub(r"\s+[-–—|]\s+" + re.escape(fonte_nome) + r"\s*$", "", titulo)
            resumo, imagem = "", ""  # a descrição do Google Notícias é só uma lista de links
        if not titulo or not link or not data:
            continue
        if not site:
            p = urllib.parse.urlsplit(link)
            site = f"{p.scheme}://{p.netloc}"
        itens.append({
            "titulo": titulo, "link": link, "data": data, "resumo": cortar(resumo, 320), "imagem": imagem,
            "fonte": limpar_fonte(fonte_nome), "site": site, "especial": fonte.get("especial", False),
            "filtrar": fonte.get("filtrar", False), "google": eh_google, "lingua_feed": fonte.get("lingua", "x"),
        })
    print(f"  {len(itens):3d} itens  {(limpar_fonte(titulo_canal) or url)[:60]}")
    return itens


# --------------------------------------------------------------------------- #
# IMAGENS (og:image) E TRADUÇÃO
# --------------------------------------------------------------------------- #
def meta_pagina(url):
    """Abre a página original e devolve (imagem, descrição) das meta tags."""
    imagem, descricao, _ = pagina_artigo(url)
    return imagem, descricao


_LIXO_PARAGRAFO = re.compile(
    r"cookie|subscribe|newsletter|sign up|log ?in|all rights reserved|©|copyright|advertis|javascript|"
    r"your browser|privacy policy|terms of (?:use|service)|follow us|click here|read more|related:|"
    r"assine|inscreva|publicidade|todos os direitos|版权|著作権|무단|저작권|광고|免责声明|責任編輯|记者|記者",
    re.I)


def paragrafos_artigo(pagina):
    """Primeiros parágrafos do texto da matéria (sem menus, avisos e rodapés)."""
    corpo = pagina
    m = re.search(r"(?is)<article\b.*?</article>", pagina)
    if m and len(m.group(0)) > 1500:
        corpo = m.group(0)
    corpo = re.sub(r"(?is)<(script|style|nav|header|footer|aside|figure|form|noscript)\b.*?</\1>", " ", corpo)
    saida = []
    for bruto in re.findall(r"(?is)<p\b[^>]*>(.*?)</p>", corpo):
        t = limpar_html(bruto)
        cjk = len(_CJK.findall(t)) and sum(len(x) for x in _CJK.findall(t)) > len(t) * 0.3
        if len(t) < (35 if cjk else 90) or _LIXO_PARAGRAFO.search(t):
            continue
        if any(t[:60] in x for x in saida):
            continue
        saida.append(t)
        if sum(len(x) for x in saida) > 40000:
            break
    return saida


def pagina_artigo(url, titulo=""):
    """Abre a página original e devolve (imagem, descrição, resumo da matéria inteira)."""
    try:
        pagina = baixar(url, timeout=12, limite=1_500_000).decode("utf-8", "ignore")
    except Exception:
        return "", "", ""
    imagem = descricao = ""
    for padrao in (
        r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)',
    ):
        m = re.search(padrao, pagina, re.I)
        if m:
            imagem = urllib.parse.urljoin(url, html.unescape(m.group(1)))
            break
    for padrao in (
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:description',
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)',
    ):
        m = re.search(padrao, pagina, re.I)
        if m:
            descricao = cortar(limpar_html(m.group(1)), 320)
            break
    return imagem, descricao, resumir(titulo, descricao, paragrafos_artigo(pagina))


_PARADAS = set("""
the and for that with this from have has had was were are been being will would could should into about after
before over under than then them they their there these those which while where when what who whom whose also
just more most such only very said says can its it's not but our out new one two all any how why his her she
him you your we us may might must per via de la le les des du un une et est pour dans par sur que qui avec
pas plus ses son aux die der das und den dem des ein eine ist mit von für auf nicht sich auch als bei wie
el los las del por con una para que como más sus son está fue han ser il lo gli della dei per con che non
una sono come più anche nel alla delle dos das uma com por para que como mais seus suas são está foi
""".split())
_FRASES = re.compile(r"(?<=[.!?…])(?<!\s[A-Z]\.)(?<!Mr\.)(?<!Dr\.)(?<!Ms\.)(?<!St\.)(?<!Inc\.)(?<!Co\.)(?<!vs\.)\s+(?=[\"“'A-ZÀ-Ý0-9가-힯])|(?<=[。！？])")
_PALAVRA = re.compile(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’\-]{2,}|[0-9]+(?:[.,][0-9]+)?%?|[가-힯]{2,}")


_LEGENDA = re.compile(r"(?i)(?:credit|crédito|image|photo|foto|source|getty images|shutterstock)\s*:|\s\|\s|^\(?(?:photo|foto|image)")


def _tokens(frase):
    """Palavras importantes de uma frase (letras latinas, coreano) + pares de caracteres (chinês/japonês)."""
    toks = [w.lower() for w in _PALAVRA.findall(frase)]
    toks = [w for w in toks if w not in _PARADAS and len(w) >= 3 or w[:1].isdigit() or "가" <= w[:1] <= "힯"]
    for bloco in re.findall(r"[぀-ヿ㐀-鿿]{2,}", frase):
        toks += [bloco[i:i + 2] for i in range(len(bloco) - 1)]
    return toks


def resumir(titulo, descricao, paragrafos, limite=900):
    """Resumo da matéria inteira: dá nota a cada frase pelas palavras mais repetidas no texto
    (e as do título) e junta as frases mais importantes, na ordem em que aparecem."""
    frases = []
    for i, p in enumerate(paragrafos):
        for f in _FRASES.split(p):
            f = f.strip()
            if 25 <= len(f) <= 600 and not _LEGENDA.search(f):
                frases.append((i, f))
    if not frases:
        return descricao
    # chinês/japonês dizem muito mais em poucos caracteres
    texto_todo = "".join(f for _, f in frases)
    if sum(len(x) for x in re.findall(r"[぀-ヿ㐀-鿿]+", texto_todo)) > len(texto_todo) * 0.4:
        limite = int(limite * 0.3)
    freq = {}
    for _, f in frases:
        for t in set(_tokens(f)):
            freq[t] = freq.get(t, 0) + 1
    tit = set(_tokens(titulo)) | set(_tokens(descricao))
    total = len(frases)
    notas = []
    for n, (par, f) in enumerate(frases):
        toks = _tokens(f)
        if len(toks) < 3:
            notas.append(0)
            continue
        nota = sum(freq.get(t, 0) for t in set(toks)) / (len(set(toks)) ** 0.6)
        nota *= 1 + 0.25 * len(tit & set(toks)) ** 0.5     # fala do assunto do título
        nota *= 1.35 if n < 3 else 1.15 if n < total * 0.25 else 1.0  # o começo costuma ter o essencial
        if re.search(r"\d", f):
            nota *= 1.1                                   # números, datas, preços, metas
        notas.append(nota)
    escolhidas, tam = set(), 0
    for n in sorted(range(total), key=lambda k: -notas[k]):
        f = frases[n][1]
        if notas[n] <= 0 or any(f[:50] in frases[k][1] for k in escolhidas):
            continue
        if tam and tam + len(f) > limite:
            continue
        escolhidas.add(n)
        tam += len(f)
        if tam >= limite * 0.8 or len(escolhidas) >= 7:
            break
    ordem = sorted(escolhidas)
    # junta em 2 ou 3 parágrafos, seguindo os parágrafos da matéria
    blocos, atual, ultimo_par = [], [], None
    for n in ordem:
        par, f = frases[n]
        if atual and (len(" ".join(atual)) > limite / 2.5) and par != ultimo_par:
            blocos.append(" ".join(atual))
            atual = []
        atual.append(f)
        ultimo_par = par
    if atual:
        blocos.append(" ".join(atual))
    texto = "\n".join(blocos).strip()
    return texto or descricao


def traduzir_longo(texto, max_bytes=1500):
    """Traduz um texto longo em pedaços de frases (cada pedido ao tradutor tem limite de tamanho)."""
    pedacos, atual = [], ""
    for f in re.split(r"(?<=[.!?。！？\n])", texto):
        if atual and len((atual + f).encode("utf-8")) > max_bytes:
            pedacos.append(atual)
            atual = ""
        atual += f
    if atual.strip():
        pedacos.append(atual)
    saida = []
    for pedaco in pedacos[:4]:
        pedaco = _cabe_no_tradutor(pedaco, max_bytes)
        quebra = pedaco.endswith("\n")
        t, ok, _ = traduzir(pedaco.strip())
        if not ok:
            return texto, False
        saida.append(t + ("\n" if quebra else " "))
    return "".join(saida).strip(), True


def _cabe_no_tradutor(texto, max_bytes=1600):
    """O tradutor recebe o texto pelo endereço: corta textos longos (CJK ocupa 3 bytes por letra)."""
    while len(texto.encode("utf-8")) > max_bytes:
        texto = texto[: int(len(texto) * 0.85)]
        corte = max(texto.rfind(". "), texto.rfind("。"), texto.rfind("\n"))
        if corte > len(texto) * 0.5:
            texto = texto[:corte + 1]
    return texto


IMAGENS_GENERICAS = set()


class GoogleBloqueou(Exception):
    pass


_GOOGLE = {"bloqueado": False, "ultimo": 0.0, "ok": 0, "falhas": 0}


def resolver_google(link):
    """Converte um link news.google.com/rss/articles/... no endereço real da notícia.
    Respeita um intervalo entre pedidos e para tudo se o Google limitar (HTTP 429)."""
    if _GOOGLE["bloqueado"]:
        raise GoogleBloqueou()
    espera = INTERVALO_GOOGLE - (time.time() - _GOOGLE["ultimo"])
    if espera > 0:
        time.sleep(espera)
    _GOOGLE["ultimo"] = time.time()
    try:
        return _resolver_google(link)
    except urllib.error.HTTPError as e:
        if e.code in (429, 503):
            _GOOGLE["bloqueado"] = True
            raise GoogleBloqueou()
        return ""


def _resolver_google(link):
    try:
        gid = urllib.parse.urlsplit(link).path.rstrip("/").split("/")[-1]
        pagina = baixar(f"https://news.google.com/articles/{gid}", timeout=20, limite=3_000_000).decode("utf-8", "ignore")
        sg = re.search(r'data-n-a-sg="([^"]+)"', pagina)
        ts = re.search(r'data-n-a-ts="([^"]+)"', pagina)
        if not (sg and ts):
            return ""
        pedido = ["Fbv4je", '["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],'
                  f'"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{gid}",{ts.group(1)},"{sg.group(1)}"]']
        corpo = ("f.req=" + urllib.parse.quote(json.dumps([[pedido]]))).encode()
        req = urllib.request.Request(
            "https://news.google.com/_/DotsSplashUi/data/batchexecute", data=corpo,
            headers={"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            resp = r.read().decode("utf-8", "ignore")
        dados = json.loads(resp.split("\n\n")[1])[:-2]
        real = json.loads(dados[0][2])[1]
        return real if isinstance(real, str) and real.startswith("http") else ""
    except urllib.error.HTTPError:
        raise
    except Exception:
        return ""


def completar_item(item_salvo):
    """Completa uma notícia já salva: imagem e resumo a partir do link original
    (ou, se faltar imagem, a partir das outras fontes que publicaram a mesma notícia)."""
    alvos = []
    if "news.google.com" not in item_salvo["u"]:
        alvos.append(item_salvo["u"])
    alvos += [o["u"] for o in item_salvo.get("o", []) if "news.google.com" not in o["u"]]
    item_salvo["mx"] = item_salvo.get("mx", 0) + 1  # tentativas
    for alvo in alvos[:4]:
        img, desc, texto = pagina_artigo(alvo, item_salvo.get("to") or item_salvo.get("t", ""))
        if img in IMAGENS_GENERICAS:
            img = ""
        if img and not item_salvo.get("i"):
            item_salvo["i"] = img
        if texto and not item_salvo.get("rx"):
            # resumo em português da notícia (página da notícia no site)
            lingua = item_salvo.get("lg") or "x"
            ok = True
            if lingua != "pt":
                texto, ok = traduzir_longo(texto)
            if ok:
                item_salvo["rx"] = texto
                if not item_salvo.get("r"):
                    item_salvo["r"] = cortar(texto.split("\n")[0], 320)
            elif _TRAD["bloqueado"]:
                item_salvo["mx"] -= 1  # tradutor ocupado: a tentativa não conta
        if item_salvo.get("i") and item_salvo.get("rx"):
            break
    item_salvo["p"] = relevancia(item_salvo)


def resolver_links_salvos(itens, limite):
    """Troca links do Google pelo endereço real, em fila (para no primeiro bloqueio)."""
    feitos = 0
    for x in itens:
        if feitos >= limite:
            break
        alvos = [x] if "news.google.com" in x["u"] else []
        alvos += [o for o in x.get("o", []) if "news.google.com" in o["u"]][:2]
        for alvo in alvos:
            try:
                real = resolver_google(alvo["u"])
            except GoogleBloqueou:
                return feitos
            feitos += 1
            if real:
                alvo["u"] = real
                alvo["s"] = dominio(real) or alvo.get("s", "")
                _GOOGLE["ok"] += 1
            else:
                _GOOGLE["falhas"] += 1
                if alvo is x:
                    x["gx"] = x.get("gx", 0) + 1
    return feitos


_TRAD = {"bloqueado": False, "ultimo": 0.0, "feitas": 0}
_TRAD_LOCK = __import__("threading").Lock()
INTERVALO_TRADUCAO = 0.35  # segundos entre pedidos ao tradutor (ritmo educado)


def traduzir(texto):
    """Traduz para o português. Retorna (texto, ok, idioma_detectado).
    Se o tradutor limitar os pedidos (HTTP 429), para de traduzir nesta execução:
    o que faltar fica marcado como pendente e é traduzido na próxima rodada."""
    if not texto:
        return texto, True, ""
    if _TRAD["bloqueado"]:
        return texto, False, ""
    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
        {"client": "gtx", "sl": "auto", "tl": "pt", "dt": "t", "q": texto}
    )
    for tentativa in range(2):
        with _TRAD_LOCK:
            espera = INTERVALO_TRADUCAO - (time.time() - _TRAD["ultimo"])
            if espera > 0:
                time.sleep(espera)
            _TRAD["ultimo"] = time.time()
        try:
            dados = json.loads(baixar(url, timeout=15).decode("utf-8"))
            trad = "".join(seg[0] for seg in dados[0] if seg and seg[0]).strip()
            detectado = dados[2] if len(dados) > 2 and isinstance(dados[2], str) else ""
            _TRAD["feitas"] += 1
            return trad, True, detectado
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                if not _TRAD["bloqueado"]:
                    print("  tradutor limitou os pedidos — o restante fica para a próxima rodada", file=sys.stderr)
                _TRAD["bloqueado"] = True
                return texto, False, ""
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return texto, False, ""


def retraduzir_pendentes(itens, limite=250):
    """Traduz notícias que ficaram pendentes em rodadas anteriores."""
    pend = [x for x in itens if x.get("nt")][:limite]
    for x in pend:
        if _TRAD["bloqueado"]:
            break
        t, ok1, lg = traduzir(x.get("to") or x["t"])
        r, ok2, _ = traduzir(x["r"]) if x.get("r") else ("", True, "")
        if ok1 and ok2:
            x["t"], x["r"] = t, r
            if lg:
                x["lg"] = lg.split("-")[0].lower()
            x.pop("nt", None)
    return len(pend)


# --------------------------------------------------------------------------- #
# CLASSIFICAÇÃO E RELEVÂNCIA
# --------------------------------------------------------------------------- #
def classificar(texto_titulo, texto_resumo):
    pontos = {}
    for cat, rx in _CAT_RX.items():
        n = 3 * len(rx.findall(texto_titulo)) + len(rx.findall(texto_resumo))
        if n:
            pontos[cat] = n
    tem_fisica = any(c in FISICAS for c in pontos)
    # categorias de contexto fracas não "roubam" a notícia de uma categoria de robô
    for ctx in ("ia", "negocios", "competicoes"):
        if ctx in pontos and tem_fisica and pontos[ctx] < 3:
            pontos.pop(ctx)
    ordem = sorted(pontos, key=lambda c: (-pontos[c], c not in FISICAS))
    return ordem[:4] or ["geral"]


# --------------------------------------------------------------------------- #
# CREDIBILIDADE DAS FONTES (3 = referência mundial, 2 = grande veículo internacional de tecnologia/ciência)
# Só veículos com reconhecimento mundial. Sites brasileiros nunca entram nos destaques.
# --------------------------------------------------------------------------- #
CREDIBILIDADE = {
    # agências, jornais e TVs de referência mundial
    "reuters.com": (3, "Reuters"), "apnews.com": (3, "Associated Press"), "afp.com": (3, "AFP"),
    "bloomberg.com": (3, "Bloomberg"), "ft.com": (3, "Financial Times"), "wsj.com": (3, "The Wall Street Journal"),
    "nytimes.com": (3, "The New York Times"), "washingtonpost.com": (3, "The Washington Post"),
    "theguardian.com": (3, "The Guardian"), "bbc.com": (3, "BBC"), "bbc.co.uk": (3, "BBC"),
    "economist.com": (3, "The Economist"), "cnn.com": (3, "CNN"), "cnbc.com": (3, "CNBC"),
    "nikkei.com": (3, "Nikkei Asia"), "scmp.com": (3, "South China Morning Post"), "nature.com": (3, "Nature"),
    "science.org": (3, "Science"), "npr.org": (3, "NPR"), "dw.com": (3, "DW"), "france24.com": (3, "France 24"),
    "aljazeera.com": (3, "Al Jazeera"), "lemonde.fr": (3, "Le Monde"), "spiegel.de": (3, "Der Spiegel"),
    "elpais.com": (3, "El País"), "time.com": (3, "TIME"), "axios.com": (3, "Axios"), "latimes.com": (3, "Los Angeles Times"),
    "theatlantic.com": (3, "The Atlantic"), "yna.co.kr": (3, "Yonhap"), "kyodonews.net": (3, "Kyodo News"),
    # sites especializados em robótica, ciência e tecnologia (todos, independente do tamanho)
    "therobotreport.com": (3, "The Robot Report"), "humanoidsdaily.com": (3, "Humanoids Daily"),
    "interestingengineering.com": (3, "Interesting Engineering"), "newatlas.com": (3, "New Atlas"),
    "robohub.org": (3, "Robohub"), "techxplore.com": (3, "Tech Xplore"), "sciencedaily.com": (3, "ScienceDaily"),
    "livescience.com": (3, "Live Science"), "roboticsandautomationnews.com": (3, "Robotics & Automation News"),
    "roboticsbusinessreview.com": (3, "Robotics Business Review"), "roboticstomorrow.com": (3, "Robotics Tomorrow"),
    "mobilerobotguide.com": (3, "Mobile Robot Guide"), "humanoid.guide": (3, "Humanoid.guide"),
    "irobotnews.com": (3, "Robot Newspaper (Coreia)"), "dronedj.com": (3, "DroneDJ"), "dronelife.com": (3, "DroneLife"),
    "suasnews.com": (3, "sUAS News"), "spectrum.ieee.org": (3, "IEEE Spectrum"), "phys.org": (3, "Phys.org"),
    # grandes veículos por região — Américas
    "usatoday.com": (3, "USA Today"), "nbcnews.com": (3, "NBC News"), "abcnews.go.com": (3, "ABC News"), "cbsnews.com": (3, "CBS News"),
    "politico.com": (3, "Politico"), "cbc.ca": (3, "CBC"), "theglobeandmail.com": (3, "The Globe and Mail"), "thestar.com": (3, "Toronto Star"),
    "ctvnews.ca": (3, "CTV News"), "eluniversal.com.mx": (3, "El Universal"), "milenio.com": (3, "Milenio"), "elfinanciero.com.mx": (3, "El Financiero"),
    "clarin.com": (3, "Clarín"), "lanacion.com.ar": (3, "La Nación"), "infobae.com": (3, "Infobae"), "latercera.com": (3, "La Tercera"),
    "eltiempo.com": (3, "El Tiempo"),
    # Europa
    "thetimes.co.uk": (3, "The Times"), "telegraph.co.uk": (3, "The Telegraph"), "independent.co.uk": (3, "The Independent"),
    "news.sky.com": (3, "Sky News"), "euronews.com": (3, "Euronews"), "politico.eu": (3, "Politico Europe"), "lefigaro.fr": (3, "Le Figaro"),
    "lesechos.fr": (3, "Les Echos"), "liberation.fr": (3, "Libération"), "zeit.de": (3, "Die Zeit"), "faz.net": (3, "FAZ"),
    "sueddeutsche.de": (3, "Süddeutsche Zeitung"), "handelsblatt.com": (3, "Handelsblatt"), "elmundo.es": (3, "El Mundo"),
    "lavanguardia.com": (3, "La Vanguardia"), "abc.es": (3, "ABC (Espanha)"), "corriere.it": (3, "Corriere della Sera"),
    "repubblica.it": (3, "La Repubblica"), "ansa.it": (3, "ANSA"), "ilsole24ore.com": (3, "Il Sole 24 Ore"), "nzz.ch": (3, "NZZ"),
    "swissinfo.ch": (3, "Swissinfo"), "nos.nl": (3, "NOS"),
    # Ásia e Oriente Médio
    "japantimes.co.jp": (3, "The Japan Times"), "nhk.or.jp": (3, "NHK"), "asahi.com": (3, "Asahi Shimbun"), "yomiuri.co.jp": (3, "Yomiuri Shimbun"),
    "mainichi.jp": (3, "Mainichi"), "koreaherald.com": (3, "The Korea Herald"), "koreajoongangdaily.joins.com": (3, "Korea JoongAng Daily"),
    "joongang.co.kr": (3, "JoongAng Ilbo"), "chosun.com": (3, "Chosun Ilbo"), "donga.com": (3, "Dong-A Ilbo"), "hankyung.com": (3, "Korea Economic Daily"),
    "caixinglobal.com": (3, "Caixin"), "caixin.com": (3, "Caixin"), "taipeitimes.com": (3, "Taipei Times"), "focustaiwan.tw": (3, "Focus Taiwan (CNA)"),
    "cna.com.tw": (3, "CNA Taiwan"), "udn.com": (3, "United Daily News"), "ltn.com.tw": (3, "Liberty Times"),
    "timesofindia.indiatimes.com": (3, "The Times of India"), "economictimes.indiatimes.com": (3, "The Economic Times"),
    "thehindu.com": (3, "The Hindu"), "hindustantimes.com": (3, "Hindustan Times"), "ndtv.com": (3, "NDTV"),
    "straitstimes.com": (3, "The Straits Times"), "channelnewsasia.com": (3, "CNA (Singapura)"), "thenationalnews.com": (3, "The National"),
    "arabnews.com": (3, "Arab News"), "gulfnews.com": (3, "Gulf News"), "timesofisrael.com": (3, "The Times of Israel"), "haaretz.com": (3, "Haaretz"),
    # Oceania
    "abc.net.au": (3, "ABC News (Austrália)"), "smh.com.au": (3, "The Sydney Morning Herald"), "theaustralian.com.au": (3, "The Australian"),
    "nzherald.co.nz": (3, "NZ Herald"), "rnz.co.nz": (3, "RNZ"), "stuff.co.nz": (3, "Stuff"),
    # África
    "news24.com": (3, "News24"), "businesslive.co.za": (3, "BusinessDay"), "mg.co.za": (3, "Mail & Guardian"), "nation.africa": (3, "Nation Africa"),
    "ahram.org.eg": (3, "Ahram Online"),
    # grandes veículos de tecnologia e ciência
    "technologyreview.com": (2, "MIT Technology Review"), "spectrum.ieee.org": (2, "IEEE Spectrum"),
    "wired.com": (2, "WIRED"), "theverge.com": (2, "The Verge"), "techcrunch.com": (2, "TechCrunch"),
    "arstechnica.com": (2, "Ars Technica"), "engadget.com": (2, "Engadget"), "zdnet.com": (2, "ZDNET"),
    "newscientist.com": (2, "New Scientist"), "scientificamerican.com": (2, "Scientific American"),
    "businessinsider.com": (2, "Business Insider"), "fortune.com": (2, "Fortune"), "forbes.com": (2, "Forbes"),
    "cnet.com": (2, "CNET"), 
    "nationalgeographic.com": (2, "National Geographic"),
}
# a lista oficial vem da tabela única (coletor/fontes_aprovadas.py)
from fontes_aprovadas import APROVADAS, NIVEL  # noqa: E402
CREDIBILIDADE = {d: (NIVEL[g], n) for d, n, g, r, pais in APROVADAS}
_NOMES_CRED = {v[1].lower(): v for v in CREDIBILIDADE.values()}
_NOMES_CRED.update({"bloomberg.com": (3, "Bloomberg"), "the wall street journal": (3, "The Wall Street Journal"),
                    "wsj": (3, "The Wall Street Journal"), "bbc news": (3, "BBC"),
                    "ap news": (3, "Associated Press"), "the new york times": (3, "The New York Times")})


def credibilidade(dominio_, nome=""):
    d = (dominio_ or "").lower()
    if d.endswith(".br"):
        return (0, "")  # nada do Brasil
    for chave, v in CREDIBILIDADE.items():
        if d == chave or d.endswith("." + chave):
            return v
    return _NOMES_CRED.get((nome or "").strip().lower(), (0, ""))


def aplicar_credibilidade(x):
    """Marca o nível de credibilidade da notícia e, se a mesma notícia saiu num veículo mais
    confiável, passa esse veículo a ser o link principal."""
    melhor_nivel, melhor_nome = credibilidade(x.get("s"), x.get("f"))
    melhor_o = None
    for o in x.get("o", []):
        n, nome = credibilidade(o.get("s"), o.get("f"))
        if n > melhor_nivel:
            melhor_nivel, melhor_nome, melhor_o = n, nome, o
    if melhor_o is not None:
        x["o"].remove(melhor_o)
        x["o"].insert(0, {"f": x["f"], "u": x["u"], "s": x.get("s", ""), "id": x["id"]})
        x["f"], x["u"], x["s"] = melhor_o["f"], melhor_o["u"], melhor_o.get("s", "")
        if melhor_o.get("id"):
            x.setdefault("xid", []).append(melhor_o["id"])
    if melhor_nivel:
        x["cr"], x["cv"] = melhor_nivel, melhor_nome
    else:
        x.pop("cr", None)
        x.pop("cv", None)


def relevancia(item):
    p = 1.0
    if item.get("l"):
        p += 6  # lançamentos de robôs têm prioridade máxima
    p += {3: 2.5, 2: 1.2}.get(item.get("cr", 0), 0)  # veículos de credibilidade mundial
    p += 1.5 * len(item.get("o", []))
    if item.get("i"):
        p += 1
    if item.get("esp"):
        p += 0.8
    if item.get("r"):
        p += 0.3
    p += max([ESPECIAL_CATS.get(c, 0) for c in item.get("c", [])] or [0])
    return round(p, 2)


# --------------------------------------------------------------------------- #
# HISTÓRICO
# --------------------------------------------------------------------------- #
def carregar_mes(chave):
    caminho = os.path.join(PASTA_JSON, chave + ".json")
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar_mes(chave, dados):
    os.makedirs(PASTA_JSON, exist_ok=True)
    os.makedirs(PASTA_JS, exist_ok=True)
    ordenado = {}
    for d in sorted(dados, reverse=True):
        ordenado[d] = sorted(dados[d], key=lambda x: (-x["p"], x["d"]))
    with open(os.path.join(PASTA_JSON, chave + ".json"), "w", encoding="utf-8") as f:
        json.dump(ordenado, f, ensure_ascii=False, indent=0)
    js = json.dumps(ordenado, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(PASTA_JS, chave + ".js"), "w", encoding="utf-8") as f:
        f.write('window.CR_DADOS=window.CR_DADOS||{};CR_DADOS["' + chave + '"]=' + js + ";\n")


def gravar_fontes_aprovadas():
    """dados/fontes.js: a mesma lista fechada usada pelo robô, para o site filtrar igual."""
    lista = {d: [NIVEL[g], n, g, r, pais] for d, n, g, r, pais in APROVADAS}
    with open(os.path.join(RAIZ, "dados", "fontes.js"), "w", encoding="utf-8") as f:
        f.write("window.CR_FONTES_OK=" + json.dumps(lista, ensure_ascii=False) + ";" + chr(10))


def gerar_indice(fontes_vistas):
    gravar_fontes_aprovadas()
    meses, total = {}, 0
    if os.path.isdir(PASTA_JSON):
        for nome in sorted(os.listdir(PASTA_JSON)):
            if nome.endswith(".json"):
                chave = nome[:-5]
                dados = carregar_mes(chave)
                meses[chave] = {dia: len(lst) for dia, lst in sorted(dados.items())}
                total += sum(meses[chave].values())
    # lista de fontes já usadas (acumulada)
    fontes = {}
    if os.path.exists(ARQ_INDICE):
        try:
            antigo = json.loads(open(ARQ_INDICE, encoding="utf-8").read().split("=", 1)[1].rstrip().rstrip(";"))
            fontes = antigo.get("fontes", {})
        except Exception:
            fontes = {}
    for nome, site in fontes_vistas.items():
        if site:
            fontes[nome] = site
    indice = {"atualizado": AGORA.isoformat(timespec="minutes"), "total": total, "meses": meses, "fontes": fontes}
    with open(ARQ_INDICE, "w", encoding="utf-8") as f:
        f.write("window.CR_INDICE=" + json.dumps(indice, ensure_ascii=False) + ";\n")
    return total


STATUS_FONTES = {}
ARQ_STATUS = os.path.join(RAIZ, "dados", "status.js")


def salvar_status(st):
    with open(ARQ_STATUS, "w", encoding="utf-8") as f:
        f.write("window.CR_STATUS=" + json.dumps(st, ensure_ascii=False) + ";\n")


def main():
    print(f"Central Robótica — coleta em {AGORA:%d/%m/%Y %H:%M}")
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        brutos = [i for lst in ex.map(ler_feed, FONTES) for i in lst]
    print(f"Total bruto: {len(brutos)}")

    limite_antigo = AGORA - timedelta(days=DIAS_MAX_ATRAS)
    candidatos = []
    for it in brutos:
        if it["data"] > AGORA + timedelta(hours=1):
            it["data"] = AGORA
        if it["data"] < limite_antigo:
            continue
        texto = it["titulo"] + " " + it["resumo"]
        if EXCLUIR.search(texto):
            continue
        if it["filtrar"] and not BASE_ROBOTICA.search(it["titulo"] + " " + it["resumo"][:200]):
            continue
        candidatos.append(it)

    meses = {}

    def mes(chave):
        if chave not in meses:
            meses[chave] = carregar_mes(chave)
        return meses[chave]

    for it in candidatos:
        d = it["data"]
        mes(d.strftime("%Y-%m"))
        mes((d - timedelta(days=1)).strftime("%Y-%m"))

    vistos_url = set()
    tit_por_dia = {}
    for chave in list(meses):
        for dia, lst in meses[chave].items():
            for x in lst:
                vistos_url.add(x["id"])
                vistos_url.update(x.get("xid", []))
                for o in x.get("o", []):
                    vistos_url.add(o.get("id") or hashlib.sha1(normalizar_url(o["u"]).encode()).hexdigest()[:14])
                tit_por_dia.setdefault(dia, []).append((tokens(x["t"]), tokens(x.get("to", "")), x))

    # novos itens, sem duplicatas (fontes especializadas primeiro)
    novos, ids_lote = [], set()
    for it in sorted(candidatos, key=lambda x: (not x["especial"], x["google"])):
        ident = hashlib.sha1(normalizar_url(it["link"]).encode()).hexdigest()[:14]
        if ident in vistos_url or ident in ids_lote:
            continue
        ids_lote.add(ident)
        it["id"] = ident
        novos.append(it)
    print(f"Novos candidatos: {len(novos)} (traduzindo e buscando imagens...)")

    def preparar(it):
        if (not it["imagem"] or not it["resumo"]) and not it["google"]:
            img, desc = meta_pagina(it["link"])
            it["imagem"] = it["imagem"] or img
            it["resumo"] = it["resumo"] or desc
        it["titulo_pt"], it["resumo_pt"], it["traduzido"], it["lingua"] = it["titulo"], it["resumo"], True, "pt"
        precisa = it["lingua_feed"] != "pt" or idioma(it["titulo"] + " " + it["resumo"]) != "pt"
        if precisa:
            t, ok1, lg = traduzir(it["titulo"])
            r, ok2, _ = traduzir(it["resumo"]) if it["resumo"] else ("", True, "")
            lg = (lg or "").lower()
            if not (ok1 and lg.startswith("pt")):
                it["titulo_pt"], it["resumo_pt"] = t, r
                it["traduzido"] = ok1 and ok2
                it["lingua"] = lg.split("-")[0] if lg else "?"
        return it

    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        novos = list(ex.map(preparar, novos))

    adicionados = agrupados = 0
    fontes_vistas = {}
    for it in sorted(novos, key=lambda x: x["data"]):
        txt_t = it["titulo"] + " | " + it["titulo_pt"]
        txt_r = it["resumo"] + " | " + it["resumo_pt"]
        if EXCLUIR.search(txt_t):
            continue
        cats = classificar(txt_t, txt_r)
        if (cats[0] == "drones" and GUERRA.search(txt_t + " " + txt_r)) or ATAQUE.search(txt_t):
            continue  # notícia de guerra com drones: fora do escopo
        if cats == ["geral"] and not BASE_ROBOTICA.search(txt_t):
            continue
        dia = it["data"].strftime("%Y-%m-%d")
        tk, tko = tokens(it["titulo_pt"]), tokens(it["titulo"])
        fontes_vistas[it["fonte"]] = dominio(it["site"])

        # mesma notícia em outro site? (mesmo dia ou dia anterior)
        dia_ant = (it["data"] - timedelta(days=1)).strftime("%Y-%m-%d")
        repetida = None
        for d in (dia, dia_ant):
            for tk2, tko2, x in tit_por_dia.get(d, []):
                if max(parecido(tk, tk2), parecido(tko, tko2)) >= 0.5:
                    repetida = x
                    break
            if repetida:
                break
        if repetida:
            outras = repetida.setdefault("o", [])
            if it["fonte"] != repetida["f"] and all(o["f"] != it["fonte"] for o in outras) and len(outras) < 10:
                outras.append({"f": it["fonte"], "u": it["link"], "s": dominio(it["site"]), "id": it["id"]})
                if not repetida.get("i") and it["imagem"]:
                    repetida["i"] = it["imagem"]
                if not repetida.get("r") and it["resumo_pt"]:
                    repetida["r"] = it["resumo_pt"]
                if it["especial"]:
                    repetida["esp"] = 1
                repetida["p"] = relevancia(repetida)
                agrupados += 1
            continue

        novo = {
            "id": it["id"],
            "t": it["titulo_pt"],
            "r": it["resumo_pt"],
            "u": it["link"],
            "f": it["fonte"],
            "s": dominio(it["site"]),
            "i": it["imagem"],
            "d": it["data"].isoformat(timespec="minutes"),
            "c": cats,
            "l": 1 if eh_lancamento(it["titulo"] + " | " + it["titulo_pt"]) else 0,
        }
        if it["lingua"] != "pt":
            novo["to"] = it["titulo"]
            novo["lg"] = it["lingua"]
            if not it["traduzido"]:
                novo["nt"] = 1
        if it["especial"]:
            novo["esp"] = 1
        novo["p"] = relevancia(novo)
        mes(dia[:7]).setdefault(dia, []).append(novo)
        tit_por_dia.setdefault(dia, []).append((tk, tko, novo))
        adicionados += 1

    # carrega TODO o arquivo para aplicar as regras (inclusive a lista fechada de veículos)
    if os.path.isdir(PASTA_JSON):
        for nome in os.listdir(PASTA_JSON):
            if nome.endswith(".json"):
                mes(nome[:-5])

    # só sites especializados e os maiores veículos do mundo: genéricos e brasileiros saem (inclusive do arquivo antigo)
    removidas = 0
    for dados in meses.values():
        for dia in list(dados):
            ficam = []
            for x in dados[dia]:
                x["o"] = [o for o in x.get("o", []) if credibilidade(o.get("s"), o.get("f"))[0] >= 2 or credibilidade(x.get("s"), x.get("f"))[0] < 2]
                aplicar_credibilidade(x)
                x["o"] = [o for o in x.get("o", []) if credibilidade(o.get("s"), o.get("f"))[0] >= 2]
                if not x["o"]:
                    x.pop("o")
                if x.get("cr", 0) >= 2:
                    ficam.append(x)
                else:
                    removidas += 1
            if ficam:
                dados[dia] = ficam
            else:
                del dados[dia]
    if removidas:
        print(f"Removidas {removidas} notícias de sites genéricos, pouco reconhecidos ou brasileiros")

    # reclassifica todo o histórico carregado (regras novas valem para o passado)
    for dados in meses.values():
        for lst in dados.values():
            for x in lst:
                tt = x.get("to", "") + " | " + x["t"]
                x["c"] = classificar(tt, x.get("r", ""))
                x["l"] = 1 if eh_lancamento(tt) else 0
                x.pop("cur", None)
                x.pop("doc", None)
                if CURIOSIDADE.search(tt + " " + x.get("r", "")[:200]):
                    x["cur"] = 1
                if DOCUMENTARIO.search(tt):
                    x["doc"] = 1
                    x["cur"] = 1
                aplicar_credibilidade(x)
                x["p"] = relevancia(x)

    todos = [x for dados in meses.values() for lst in dados.values() for x in lst]

    # 0) traduz as notícias que ficaram pendentes (tradutor limitado em rodadas anteriores)
    n_pend = sum(1 for x in todos if x.get("nt"))
    if n_pend:
        print(f"Traduzindo notícias pendentes ({n_pend})...")
        retraduzir_pendentes(sorted(todos, key=lambda x: x["d"], reverse=True))

    # 1) troca links do Google pelo endereço do site original (em fila, devagar)
    pend = [x for x in todos if x.get("gx", 0) < 3 and ("news.google.com" in x["u"] or any("news.google.com" in o["u"] for o in x.get("o", [])))]
    pend.sort(key=lambda x: (-(x.get("l") or 0), -int(x["d"][:10].replace("-", "")), -x["p"]))
    if pend:
        print(f"Buscando o link original de notícias do Google ({len(pend)} pendentes)...")
        feitos = resolver_links_salvos(pend, LIMITE_GOOGLE)
        print(f"  resolvidos: {_GOOGLE['ok']} | sem sucesso: {_GOOGLE['falhas']} | pedidos: {feitos}"
              + (" | Google limitou os pedidos — continua na próxima execução" if _GOOGLE["bloqueado"] else ""))

    # 2) descarta imagens genéricas (logotipo do site repetido em várias notícias)
    freq = {}
    for x in todos:
        if x.get("i"):
            freq[x["i"]] = freq.get(x["i"], 0) + 1
    genericas = {u for u, n in freq.items() if n >= 3}
    for x in todos:
        if x.get("i") in genericas:
            x["i"] = ""
            x["mx"] = 9  # não adianta buscar de novo no mesmo site
            for o in x.get("o", []):
                if "news.google.com" not in o["u"]:
                    x["mx"] = 0  # mas pode vir de outra fonte
    IMAGENS_GENERICAS.update(genericas)

    # 3) imagem de destaque (e resumo) para quem ainda não tem
    falta = [x for x in todos if (not x.get("i") or not x.get("rx")) and x.get("mx", 0) < 3
             and ("news.google.com" not in x["u"] or any("news.google.com" not in o["u"] for o in x.get("o", [])))]
    falta.sort(key=lambda x: (-int(x["d"][:10].replace("-", "")), bool(x.get("i")), -(x.get("l") or 0), -x["p"]))
    falta = falta[:LIMITE_COMPLETAR]
    if falta:
        print(f"Buscando imagem de destaque e resumo para {len(falta)} notícias...")
        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            list(ex.map(completar_item, falta))
    com_img = sum(1 for x in todos if x.get("i"))
    print(f"  notícias com imagem: {com_img}/{len(todos)} nos meses carregados")

    for chave, dados in meses.items():
        if dados:
            salvar_mes(chave, dados)
    total = gerar_indice(fontes_vistas)
    print(f"Adicionadas: {adicionados} | agrupadas (mesma notícia em outro site): {agrupados} | total no histórico: {total}")
    salvar_status({
        "inicio": AGORA.isoformat(timespec="seconds"),
        "fim": datetime.now(BRASILIA).isoformat(timespec="seconds"),
        "fontes_ok": sum(1 for v in STATUS_FONTES.values() if v >= 0),
        "fontes_falha": sorted(k for k, v in STATUS_FONTES.items() if v < 0),
        "fontes_total": len(FONTES),
        "lidos": len(brutos),
        "novas": adicionados,
        "agrupadas": agrupados,
        "total": total,
        "imagens": [com_img, len(todos)],
        "google_resolvidos": _GOOGLE["ok"],
        "google_limitado": _GOOGLE["bloqueado"],
    })


if __name__ == "__main__":
    main()
