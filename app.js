/* ==========================================================================
   CENTRAL ROBÓTICA — lógica da página
   Lê dados/indice.js (CR_INDICE) e carrega sob demanda dados/meses/AAAA-MM.js
   ========================================================================== */
(function () {
  "use strict";

  // ------------------------------------------------------------------ ícones
  const ICONES = {
    inicio: '<path d="M12 3l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 16.4 6.7 19.4l1.2-6L3.4 9.3l6-.7z"/>',
    lancamentos: '<path d="M5 19c0-3 1-5 3-6M14 4c3 0 6 3 6 6-2 4-6 7-9 8l-5-5c1-3 4-7 8-9z"/><circle cx="14.5" cy="9.5" r="1.6"/><path d="M8 16l-3 3"/>',
    humanoides: '<circle cx="12" cy="4.5" r="2.3"/><rect x="8" y="8" width="8" height="7" rx="1.5"/><path d="M8 10l-3 4M16 10l3 4M10 15v6M14 15v6"/>',
    quadrupedes: '<rect x="5" y="9" width="11" height="5" rx="1.5"/><path d="M16 10h3l2-3M6 14v6M9 14v6M13 14v6M16 14v6M5 10l-2-2"/><circle cx="19.5" cy="9" r=".6"/>',
    industriais: '<path d="M4 21h8M8 21v-4l4-6 6-3"/><circle cx="12" cy="11" r="1.6"/><circle cx="8" cy="17" r="1.6"/><path d="M18 8l2-2M18 8l1 3"/>',
    drones: '<rect x="9" y="10" width="6" height="4" rx="1"/><path d="M9 11L5 7M15 11l4-4M9 13l-4 4M15 13l4 4"/><path d="M2 7h6M16 7h6M2 17h6M16 17h6"/>',
    casa: '<path d="M3 11l9-7 9 7M5 9.5V20h14V9.5"/><circle cx="12" cy="15" r="3"/><circle cx="12" cy="15" r=".6"/>',
    medicina: '<path d="M12 21s-8-4.6-8-11a4.5 4.5 0 018-2.8A4.5 4.5 0 0120 10c0 6.4-8 11-8 11z"/><path d="M12 9v6M9 12h6"/>',
    autonomos: '<path d="M5 16l1.5-5A2 2 0 018.4 9.5h7.2a2 2 0 011.9 1.5L19 16"/><rect x="3" y="16" width="18" height="4" rx="1"/><circle cx="7.5" cy="18" r=".6"/><circle cx="16.5" cy="18" r=".6"/><path d="M9 6a5 5 0 016 0M7 3.8a8 8 0 0110 0"/>',
    espaco: '<circle cx="12" cy="12" r="5"/><ellipse cx="12" cy="12" rx="10" ry="3.5" transform="rotate(-20 12 12)"/>',
    ia: '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    negocios: '<path d="M3 20h18M6 16v-4M10 16V8M14 16v-6M18 16V5"/>',
    geral: '<rect x="5" y="7" width="14" height="11" rx="3"/><circle cx="9.5" cy="12.5" r="1.3"/><circle cx="14.5" cy="12.5" r="1.3"/><path d="M12 7V4"/>',
    catalogo: '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>',
    fabricantes: '<path d="M3 21V10l5 3V10l5 3V6l8 4v11z"/><path d="M7 17h2M12 17h2M17 17h1"/>',
    sites: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    curiosidades: '<path d="M9 18h6M10 21h4M12 3a6 6 0 00-3.5 10.9c.6.5 1 1.2 1 2V16h5v-.1c0-.8.4-1.5 1-2A6 6 0 0012 3z"/>',
    historia: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    ranking: '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 01-10 0z"/><path d="M7 6H4a3 3 0 003 4M17 6h3a3 3 0 01-3 4"/>',
    universidades: '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5M22 9v6"/>',
    cobots: '<path d="M4 20h7M7 20v-5l4-5 5-2"/><circle cx="11" cy="10" r="1.5"/><circle cx="18" cy="5" r="2"/><path d="M18 7v4M16 13h4"/>',
    logistica: '<rect x="3" y="9" width="9" height="8"/><path d="M12 13h4l3 3v1h-7M7 9V6h4v3"/><circle cx="7" cy="19" r="1.5"/><circle cx="16" cy="19" r="1.5"/>',
    entrega: '<rect x="5" y="6" width="14" height="10" rx="2"/><path d="M9 6V4h6v2M12 9v4"/><circle cx="8" cy="19" r="1.5"/><circle cx="16" cy="19" r="1.5"/>',
    servico: '<path d="M4 16h16M6 16a6 6 0 0112 0M12 8V6M3 19h18"/>',
    companhia: '<rect x="6" y="8" width="12" height="9" rx="3"/><path d="M12 8V5"/><path d="M12 15s-2.5-1.5-2.5-3a1.3 1.3 0 012.5-.5 1.3 1.3 0 012.5.5c0 1.5-2.5 3-2.5 3z"/>',
    exoesqueletos: '<circle cx="12" cy="4" r="2"/><path d="M12 6v6l-3 4v5M12 12l3 4v5M8 9h8M8 14h2M14 14h2"/>',
    agricolas: '<path d="M12 20V10M12 14c-3 0-5-2-5-5 3 0 5 2 5 5zM12 12c0-3 2-5 5-5 0 3-2 5-5 5z"/><path d="M4 20h16"/>',
    construcao: '<path d="M5 21V4h2v17M7 5h12l-3 3M15 5v6M13 11h4v3h-4zM3 21h8"/>',
    inspecao: '<circle cx="10" cy="10" r="6"/><path d="M15 15l5 5M10 7v3l2 2"/>',
    defesa: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    resgate: '<path d="M7 18h10M8 18v-5a4 4 0 018 0v5M12 5V3M5 8L3.5 6.5M19 8l1.5-1.5M5 21h14"/>',
    subaquaticos: '<path d="M3 17c2 0 2-1.5 4.5-1.5S10 17 12 17s2.5-1.5 4.5-1.5S19 17 21 17"/><path d="M6 10c2-3 7-3 9 0-2 3-7 3-9 0zM15 10l3-2v4z"/>',
    microrrobos: '<ellipse cx="12" cy="13" rx="4" ry="5"/><path d="M12 8V5M9 6L7 4M15 6l2-2M8 12H4M20 12h-4M8 16l-3 2M16 16l3 2"/>',
    educacao: '<path d="M4 5h7a2 2 0 012 2v12a2 2 0 00-2-2H4zM20 5h-7a2 2 0 00-2 2M20 5v12h-7"/>',
    competicoes: '<path d="M8 4h8v5a4 4 0 01-8 0zM8 6H5a3 3 0 003 4M16 6h3a3 3 0 01-3 4M12 13v4M8 20h8M10 17h4"/>',
  };

  // categorias de robôs (classificação da IFR — industriais e de serviço — e do noticiário mundial)
  const CATEGORIAS = [
    { id: "inicio", nome: "Destaques" },
    { id: "ranking", nome: "Ranking", especial: true },
    { id: "lancamentos", nome: "Lançamentos" },
    { id: "humanoides", nome: "Humanoides" },
    { id: "quadrupedes", nome: "Cães-robô" },
    { id: "industriais", nome: "Industriais" },
    { id: "cobots", nome: "Cobots" },
    { id: "logistica", nome: "Logística e Armazéns" },
    { id: "drones", nome: "Drones" },
    { id: "autonomos", nome: "Veículos Autônomos" },
    { id: "entrega", nome: "Entrega" },
    { id: "casa", nome: "Casa" },
    { id: "servico", nome: "Serviço" },
    { id: "companhia", nome: "Companhia e Sociais" },
    { id: "medicina", nome: "Medicina" },
    { id: "exoesqueletos", nome: "Exoesqueletos e Próteses" },
    { id: "agricolas", nome: "Agrícolas" },
    { id: "construcao", nome: "Construção" },
    { id: "inspecao", nome: "Inspeção e Segurança" },
    { id: "defesa", nome: "Defesa" },
    { id: "resgate", nome: "Resgate e Emergência" },
    { id: "espaco", nome: "Espaço" },
    { id: "subaquaticos", nome: "Subaquáticos" },
    { id: "microrrobos", nome: "Microrrobôs e Soft Robots" },
    { id: "educacao", nome: "Educação" },
    { id: "competicoes", nome: "Competições e Eventos" },
    { id: "ia", nome: "IA e Pesquisa" },
    { id: "negocios", nome: "Negócios" },
    { id: "catalogo", nome: "Catálogo de robôs", especial: true },
    { id: "fabricantes", nome: "Fabricantes", especial: true },
    { id: "sites", nome: "Sites do mundo", especial: true },
    { id: "curiosidades", nome: "+1000 Curiosidades", especial: true },
    { id: "universidades", nome: "Universidades", especial: true },
    { id: "historia", nome: "História da robótica", especial: true },
  ];
  const ESPECIAIS = new Set(CATEGORIAS.filter((c) => c.especial).map((c) => c.id));
  const TIPOS = ["humanoides", "quadrupedes", "industriais", "cobots", "logistica", "drones", "autonomos", "entrega", "casa", "servico",
    "companhia", "medicina", "exoesqueletos", "agricolas", "construcao", "inspecao", "defesa", "resgate", "espaco", "subaquaticos",
    "microrrobos", "educacao"];
  const NOME_CAT = Object.fromEntries(CATEGORIAS.map((c) => [c.id, c.nome]));
  NOME_CAT.geral = "Robótica";
  NOME_CAT.quadrupedes = "Cães-robô e Quadrúpedes";

  const IDIOMAS = {
    en: "inglês", es: "espanhol", fr: "francês", de: "alemão", it: "italiano", zh: "chinês",
    ja: "japonês", ko: "coreano", ru: "russo", nl: "holandês", pl: "polonês", tr: "turco",
    ar: "árabe", hi: "híndi", sv: "sueco", uk: "ucraniano", cs: "tcheco", ro: "romeno",
  };
  const MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
  const SEMANA = ["domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"];
  const POR_PAGINA = 40;

  const INDICE = window.CR_INDICE || { meses: {}, fontes: {}, total: 0 };
  window.CR_DADOS = window.CR_DADOS || {};
  const $ = (s) => document.querySelector(s);

  // ------------------------------------------------------------------ datas
  function hojeBR() {
    return new Intl.DateTimeFormat("en-CA", { timeZone: "America/Sao_Paulo", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  }
  const paraData = (s) => { const [a, m, d] = s.split("-").map(Number); return new Date(Date.UTC(a, m - 1, d)); };
  const deData = (dt) => dt.toISOString().slice(0, 10);
  const somaDias = (s, n) => { const d = paraData(s); d.setUTCDate(d.getUTCDate() + n); return deData(d); };
  function somaMeses(s, n) {
    const d = paraData(s); const dia = d.getUTCDate(); d.setUTCDate(1); d.setUTCMonth(d.getUTCMonth() + n);
    const ult = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 0)).getUTCDate();
    d.setUTCDate(Math.min(dia, ult)); return deData(d);
  }
  function inicioSemana(s) { const d = paraData(s); const w = (d.getUTCDay() + 6) % 7; return somaDias(s, -w); }
  function fmtDiaLongo(s) { const d = paraData(s); return `${SEMANA[d.getUTCDay()]}, ${d.getUTCDate()} de ${MESES[d.getUTCMonth()]} de ${d.getUTCFullYear()}`; }
  function fmtDiaCurto(s) { const [a, m, d] = s.split("-"); return `${d}/${m}/${a}`; }
  function fmtHora(iso) { return iso.slice(11, 16); }

  function intervalo(p, d) {
    if (p === "semana") { const i = inicioSemana(d); return [i, somaDias(i, 6)]; }
    if (p === "mes") { const i = d.slice(0, 8) + "01"; return [i, somaDias(somaMeses(i, 1), -1)]; }
    if (p === "ano") return [d.slice(0, 4) + "-01-01", d.slice(0, 4) + "-12-31"];
    return [d, d];
  }
  function rotulo(p, d) {
    const [i, f] = intervalo(p, d);
    if (p === "semana") return `Semana ${fmtDiaCurto(i).slice(0, 5)} – ${fmtDiaCurto(f)}`;
    if (p === "mes") return `${MESES[+d.slice(5, 7) - 1]} de ${d.slice(0, 4)}`;
    if (p === "ano") return `Ano de ${d.slice(0, 4)}`;
    return fmtDiaLongo(d);
  }

  // ------------------------------------------------------------------ estado
  const estado = { c: "inicio", p: "hoje", d: hojeBR(), q: "", pagina: 1, f: "", g: "", n: "", em: "" };
  function lerHash() {
    const h = new URLSearchParams(location.hash.slice(1));
    estado.c = NOME_CAT[h.get("c")] ? h.get("c") : "inicio";
    estado.p = ["hoje", "dia", "semana", "mes", "ano"].includes(h.get("p")) ? h.get("p") : "hoje";
    estado.d = /^\d{4}-\d{2}-\d{2}$/.test(h.get("d") || "") ? h.get("d") : hojeBR();
    if (estado.p === "hoje") estado.d = hojeBR();
    estado.q = h.get("q") || "";
    estado.f = h.get("f") || "";
    estado.g = h.get("g") || "";
    estado.n = h.get("n") || "";
    estado.em = /^\d{4}-\d{2}-\d{2}$/.test(h.get("em") || "") ? h.get("em") : "";
    estado.pagina = 1;
  }
  function irPara(mud) {
    if (!("n" in mud)) estado.n = "";
    Object.assign(estado, mud);
    const h = new URLSearchParams();
    if (estado.n) { h.set("n", estado.n); if (estado.em) h.set("em", estado.em); }
    if (estado.c !== "inicio") h.set("c", estado.c);
    if (estado.p !== "hoje") { h.set("p", estado.p); h.set("d", estado.d); }
    if (estado.q) h.set("q", estado.q);
    if (estado.f && ESPECIAIS.has(estado.c)) h.set("f", estado.f);
    if (estado.g && ESPECIAIS.has(estado.c)) h.set("g", estado.g);
    const novo = "#" + h.toString();
    if (location.hash !== novo && !(novo === "#" && !location.hash)) history.pushState(null, "", novo || "#");
    render();
  }

  // ------------------------------------------------------------------ dados
  const carregando = {};
  function carregarMes(chave) {
    if (window.CR_DADOS[chave]) return Promise.resolve();
    if (!INDICE.meses[chave]) return Promise.resolve();
    if (!carregando[chave]) {
      carregando[chave] = new Promise((ok) => {
        const s = document.createElement("script");
        s.src = `dados/meses/${chave}.js?v=${encodeURIComponent(INDICE.atualizado || "")}`;
        s.onload = s.onerror = () => ok();
        document.head.appendChild(s);
      });
    }
    return carregando[chave];
  }
  function mesesEntre(i, f) {
    const r = []; let k = i.slice(0, 7);
    while (k <= f.slice(0, 7)) { r.push(k); const [a, m] = k.split("-").map(Number); k = m === 12 ? `${a + 1}-01` : `${a}-${String(m + 1).padStart(2, "0")}`; }
    return r;
  }
  function diasDisponiveis() {
    const dias = [];
    for (const m of Object.keys(INDICE.meses)) for (const d of Object.keys(INDICE.meses[m])) if (INDICE.meses[m][d] > 0) dias.push(d);
    return dias.sort();
  }
  // ---------------- lista fechada: SÓ os maiores veículos do mundo (nada do Brasil, nada de sites menores)
  // 3 = agências, jornais e TVs de referência mundial · 2 = maiores veículos de ciência e tecnologia
  const MAIORES = {
    // sites especializados em robótica, ciência e tecnologia (todos, independente do tamanho)
    "therobotreport.com": [3, "The Robot Report"], "humanoidsdaily.com": [3, "Humanoids Daily"], "interestingengineering.com": [3, "Interesting Engineering"],
    "newatlas.com": [3, "New Atlas"], "robohub.org": [3, "Robohub"], "techxplore.com": [3, "Tech Xplore"], "sciencedaily.com": [3, "ScienceDaily"],
    "livescience.com": [3, "Live Science"], "roboticsandautomationnews.com": [3, "Robotics & Automation News"], "roboticsbusinessreview.com": [3, "Robotics Business Review"],
    "roboticstomorrow.com": [3, "Robotics Tomorrow"], "mobilerobotguide.com": [3, "Mobile Robot Guide"], "humanoid.guide": [3, "Humanoid.guide"],
    "irobotnews.com": [3, "Robot Newspaper (Coreia)"], "dronedj.com": [3, "DroneDJ"], "dronelife.com": [3, "DroneLife"], "suasnews.com": [3, "sUAS News"],
    "phys.org": [3, "Phys.org"],
    // grandes veículos de reconhecimento mundial
    "reuters.com": [3, "Reuters"], "apnews.com": [3, "Associated Press"], "afp.com": [3, "AFP"], "bloomberg.com": [3, "Bloomberg"],
    "ft.com": [3, "Financial Times"], "wsj.com": [3, "The Wall Street Journal"], "nytimes.com": [3, "The New York Times"],
    "washingtonpost.com": [3, "The Washington Post"], "theguardian.com": [3, "The Guardian"], "bbc.com": [3, "BBC"], "bbc.co.uk": [3, "BBC"],
    "economist.com": [3, "The Economist"], "cnn.com": [3, "CNN"], "cnbc.com": [3, "CNBC"], "nikkei.com": [3, "Nikkei Asia"],
    "scmp.com": [3, "South China Morning Post"], "nature.com": [3, "Nature"], "science.org": [3, "Science"], "npr.org": [3, "NPR"],
    "dw.com": [3, "DW"], "france24.com": [3, "France 24"], "aljazeera.com": [3, "Al Jazeera"], "lemonde.fr": [3, "Le Monde"],
    "spiegel.de": [3, "Der Spiegel"], "elpais.com": [3, "El País"], "time.com": [3, "TIME"], "axios.com": [3, "Axios"],
    "latimes.com": [3, "Los Angeles Times"], "theatlantic.com": [3, "The Atlantic"], "yna.co.kr": [3, "Yonhap"], "kyodonews.net": [3, "Kyodo News"],
    "technologyreview.com": [2, "MIT Technology Review"], "spectrum.ieee.org": [3, "IEEE Spectrum"], "wired.com": [2, "WIRED"],
    "theverge.com": [2, "The Verge"], "techcrunch.com": [2, "TechCrunch"], "arstechnica.com": [2, "Ars Technica"], "engadget.com": [2, "Engadget"],
    "zdnet.com": [2, "ZDNET"], "newscientist.com": [2, "New Scientist"], "scientificamerican.com": [2, "Scientific American"],
    "businessinsider.com": [2, "Business Insider"], "fortune.com": [2, "Fortune"], "forbes.com": [2, "Forbes"], "cnet.com": [2, "CNET"],
    "nationalgeographic.com": [2, "National Geographic"],
  };
  // a lista oficial vem da tabela única do robô (dados/fontes.js); a de cima é só reserva
  if (window.CR_FONTES_OK) { for (const k in MAIORES) delete MAIORES[k]; Object.assign(MAIORES, window.CR_FONTES_OK); }
  const MAIORES_NOMES = Object.fromEntries(Object.values(MAIORES).map((v) => [v[1].toLowerCase(), v]));
  Object.assign(MAIORES_NOMES, { "bloomberg.com": [3, "Bloomberg"], "bbc news": [3, "BBC"], "ap news": [3, "Associated Press"], "wsj": [3, "The Wall Street Journal"] });
  function credDe(dom, nome) {
    const d = (dom || "").toLowerCase();
    if (d.endsWith(".br")) return [0, ""];
    for (const k in MAIORES) if (d === k || d.endsWith("." + k)) return MAIORES[k];
    return MAIORES_NOMES[(nome || "").trim().toLowerCase()] || [0, ""];
  }
  // aprova a notícia se ela saiu num dos maiores veículos; esse veículo vira o link principal
  function aprovar(it) {
    if (it._ok !== undefined) return it._ok;
    let [n, nome] = credDe(it.s, it.f);
    const outras = (it.o || []).filter((o) => credDe(o.s, o.f)[0] >= 2);
    if (n < 2 && outras.length) {
      const melhor = outras.sort((a, b) => credDe(b.s, b.f)[0] - credDe(a.s, a.f)[0])[0];
      outras.splice(outras.indexOf(melhor), 1);
      [it.u, it.f, it.s] = [melhor.u, melhor.f, melhor.s];
      [n, nome] = credDe(it.s, it.f);
    }
    it.o = outras;
    it._cred = [n, nome];
    return (it._ok = n >= 2);
  }
  const nivel = (it) => (it._cred || credDe(it.s, it.f))[0];

  async function itensDoPeriodo(i, f) {
    await Promise.all(mesesEntre(i, f).map(carregarMes));
    const out = [];
    for (const m of mesesEntre(i, f)) {
      const dados = window.CR_DADOS[m] || {};
      // só notícias já traduzidas e publicadas pelos maiores veículos do mundo
      for (const dia in dados) if (dia >= i && dia <= f) for (const it of dados[dia]) { if (it.nt || !aprovar(it)) continue; it.dia = dia; out.push(it); }
    }
    return out;
  }
  const semAcento = (s) => (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  function passaCategoria(it, c) {
    if (c === "inicio") return true;
    if (c === "lancamentos") return !!it.l;
    return (it.c || []).includes(c);
  }

  // ------------------------------------------------------------------ html
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
  function placeholder(cat) {
    const ic = ICONES[cat] || ICONES.geral;
    return `<svg class="ph" viewBox="0 0 320 180" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1a0605"/><stop offset=".6" stop-color="#0b0b0d"/><stop offset="1" stop-color="#050506"/></linearGradient>
      <pattern id="p" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#e10600" stroke-opacity=".09"/></pattern></defs>
      <rect width="320" height="180" fill="url(#g)"/><rect width="320" height="180" fill="url(#p)"/>
      <circle cx="160" cy="84" r="46" fill="none" stroke="#e10600" stroke-opacity=".25"/>
      <g transform="translate(130 54) scale(2.5)" fill="none" stroke="#ff2a1f" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">${ic}</g>
      <text x="160" y="160" text-anchor="middle" fill="#7d7d88" font-family="Orbitron, sans-serif" font-size="9" letter-spacing="3">${esc((NOME_CAT[cat] || "ROBÓTICA").toUpperCase())}</text></svg>`;
  }
  // ---------------- fotos: própria da matéria > ilustrativa (licença livre, com crédito) ----------------
  const POOL = () => window.CR_IMAGENS || {};
  function hashStr(s) { let h = 7; for (const ch of String(s)) h = (h * 31 + ch.charCodeAt(0)) | 0; return Math.abs(h); }
  function escolherFoto(chaves, semente) {
    const P = POOL();
    for (const k of chaves) { const l = P[k]; if (l && l.length) return l[hashStr(semente + k) % l.length]; }
    return null;
  }
  let MATCH = null;
  function matchers() {
    if (MATCH) return MATCH;
    MATCH = [];
    for (const r of CAT.robos) MATCH.push({ k: "robo:" + r.nome, rx: rxTermos(termosRobo(r)) });
    for (const f of CAT.fabricantes) MATCH.push({ k: "fabq:" + f.id, rx: rxTermos(termosFab(f)) });
    return MATCH;
  }
  const _chaves = {};
  function chavesDe(it) {
    const id = it.id || it.u;
    if (_chaves[id]) return _chaves[id];
    const t = `${it.t || ""} ${it.to || ""}`;
    const ks = [];
    for (const m of matchers()) if (m.rx.test(t)) { ks.push(m.k); if (ks.length >= 2) break; }
    for (const c of it.c || []) ks.push("cat:" + c);
    ks.push("cat:geral");
    return (_chaves[id] = ks);
  }
  function htmlFoto(f, ilustrativa = true) {
    const oficial = /site/.test(f.l || "");
    const rot = oficial ? `Imagem: ${f.a}` : `Imagem ilustrativa · ${f.a} · ${f.l}`;
    return `<img src="${esc(f.u)}" alt="" loading="lazy" referrerpolicy="no-referrer" data-o="${esc(f.o || "")}" onerror="CR_falhaFoto(this)">` +
      (ilustrativa ? `<a class="credito" href="${esc(f.p)}" target="_blank" rel="noopener" title="${esc(rot)}">${esc(oficial ? "Imagem do site oficial" : "Imagem ilustrativa")}</a>` : "");
  }
  // foto para qualquer card: chaves = assuntos em ordem de preferência
  function foto(chaves, semente, cat) {
    const f = escolherFoto(chaves, semente);
    return f ? htmlFoto(f) : placeholder(cat || "geral");
  }
  function imagem(it) {
    const cat = (it.c || ["geral"])[0];
    const f = escolherFoto(chavesDe(it), it.id || it.u);
    const alt = f ? encodeURIComponent(JSON.stringify(f)) : "";
    if (it.i) return `<img src="${esc(it.i)}" alt="" loading="lazy" referrerpolicy="no-referrer" data-cat="${esc(cat)}" data-alt="${alt}" onerror="CR_falhaImagem(this)">`;
    return f ? htmlFoto(f) : placeholder(cat);
  }
  // a foto abre a página da notícia (o link cobre a foto; não pode envolver o link do crédito)
  const capa = (it) => `<div class="capa">${imagem(it)}<a class="capa__link" href="${hrefNoticia(it)}" tabindex="-1" aria-hidden="true"></a></div>`;
  // a foto da matéria não carregou: usa a ilustrativa (e, em último caso, a arte da categoria)
  window.CR_falhaImagem = (img) => {
    const f = img.dataset.alt ? JSON.parse(decodeURIComponent(img.dataset.alt)) : null;
    img.outerHTML = f ? htmlFoto(f) : placeholder(img.dataset.cat);
  };
  window.CR_falhaFoto = (img) => {
    if (img.dataset.o && img.src !== img.dataset.o) { img.src = img.dataset.o; img.dataset.o = ""; return; }
    const cred = img.nextElementSibling;
    if (cred && cred.classList.contains("credito")) cred.remove();
    img.outerHTML = placeholder("geral");
  };
  const miniFoto = (it) => `<span class="mini__foto">${imagem(it)}</span>`;

  function chips(it, max = 2) {
    let h = "";
    if (it.l) h += `<span class="chip chip--lanc" data-cat="lancamentos">Lançamento</span>`;
    for (const c of (it.c || []).slice(0, max)) if (c !== "geral") h += `<span class="chip" data-cat="${c}">${esc(NOME_CAT[c] || c)}</span>`;
    return `<div class="chips">${h}</div>`;
  }
  function meta(it, comDia) {
    const partes = [];
    partes.push(`<span>${comDia ? fmtDiaCurto(it.dia) + " · " : ""}${fmtHora(it.d)}</span>`);
    if (it.lg && it.lg !== "pt") partes.push(`<span class="trad" title="${esc(it.to || "")}">Traduzido do ${esc(IDIOMAS[it.lg] || "idioma original")}</span>`);
    return `<div class="meta">${partes.join("")}</div>`;
  }
  function fonte(it, curto) {
    const dom = it.s ? `<span class="fonte__dom">${esc(it.s)}</span>` : "";
    let h = `<div class="fonte"><div class="fonte__linha"><span class="fonte__rot">Fonte</span>
      <a class="fonte__site" href="${esc(it.u)}" target="_blank" rel="noopener">${esc(it.f)}</a>${dom}
      <a class="fonte__ler" href="${esc(it.u)}" target="_blank" rel="noopener">Ler no site original ↗</a></div>`;
    if (it.o && it.o.length) {
      const lim = curto ? 3 : 8;
      const links = it.o.slice(0, lim).map((o) => `<a href="${esc(o.u)}" target="_blank" rel="noopener" title="${esc(o.s || "")}">${esc(o.f)}</a>`).join(" ");
      const resto = it.o.length > lim ? ` <span>+${it.o.length - lim}</span>` : "";
      h += `<div class="fonte__tambem"><span class="fonte__rot">Também em</span> ${links}${resto}</div>`;
    }
    return h + "</div>";
  }
  const hrefNoticia = (it) => `#n=${encodeURIComponent(it.id)}&em=${it.dia || (it.d || "").slice(0, 10)}`;
  const link = (it, txt) => `<a href="${hrefNoticia(it)}" title="Ler o resumo em português">${esc(txt)}</a>`;

  function htmlPrincipal(it, comDia) {
    return `<article class="principal">
      <span class="principal__rot">Destaque principal</span>
      ${capa(it)}
      <div class="principal__corpo">${chips(it, 3)}<h2>${link(it, it.t)}</h2>${it.r ? `<p>${esc(it.r)}</p>` : ""}${meta(it, comDia)}${fonte(it)}</div>
    </article>`;
  }
  function htmlSec(it, comDia) {
    return `<article class="sec">${capa(it)}<div class="sec__corpo">${chips(it, 1)}<h3>${link(it, it.t)}</h3>${meta(it, comDia)}${fonte(it, true)}</div></article>`;
  }
  function htmlCard(it, comDia) {
    return `<article class="card"><div class="capa">${imagem(it)}${chips(it, 2)}</div>
      <div class="card__corpo"><h3>${link(it, it.t)}</h3>${it.r ? `<p>${esc(it.r)}</p>` : ""}${meta(it, comDia)}${fonte(it, true)}</div></article>`;
  }
  function htmlMenor(it) {
    return `<li class="menor">${capa(it)}<div class="menor__corpo"><div class="menor__topo">${chips(it, 1)}${meta(it, false)}</div>
      <h4>${link(it, it.t)}</h4>${fonte(it, true)}</div></li>`;
  }

  // ------------------------------------------------------------------ mesma notícia em vários sites
  // Os títulos já estão todos em português: dá para reconhecer a mesma história publicada por
  // sites de países diferentes (3 palavras importantes em comum, até 3 dias de distância).
  const PARADAS_RANK = new Set(semAcento(`a o as os um uma uns umas de da do das dos em no na nos nas por para com sem sob sobre entre ate e ou que se seu sua seus suas como mais menos muito ja nao ao aos pelo pela pelos pelas este esta isso essa esse novo nova novos novas primeiro primeira diz afirma segundo apos contra durante ser foi sao tem vai pode podem sera ano anos dia hoje agora ainda mas tambem
    robo robos robotica robotico roboticos humanoide humanoides empresa empresas mundo tecnologia inteligencia artificial 2025 2026 milhoes bilhoes dolares noticias the and for with from news`).split(/\s+/));
  function tokensTitulo(it) {
    if (!it._tk) it._tk = new Set((semAcento(it.t).match(/[a-z0-9]+/g) || []).filter((w) => w.length > 2 && !PARADAS_RANK.has(w)).map((w) => w.slice(0, 6)));
    return it._tk;
  }
  function mesmaHistoria(a, b) {
    const ta = tokensTitulo(a), tb = tokensTitulo(b);
    let c = 0;
    for (const w of ta) if (tb.has(w)) c++;
    return c >= 3 && c / (ta.size + tb.size - c) >= 0.25;
  }
  const domDe = (f) => (f.s || f.f || "").replace(/^www\./, "").toLowerCase();
  function agruparNoticias(itens) {
    const grupos = [];
    for (const it of [...itens].sort((a, b) => a.d.localeCompare(b.d))) {
      const t0 = Date.parse(it.d);
      let g = null;
      // os grupos estão em ordem de data: basta olhar os dos últimos 3 dias
      for (let k = grupos.length - 1; k >= 0 && t0 - grupos[k].t0 <= 3 * 864e5; k--) {
        if (grupos[k].itens.some((x) => mesmaHistoria(it, x))) { g = grupos[k]; break; }
      }
      if (g) g.itens.push(it); else grupos.push({ t0, itens: [it] });
    }
    // segunda passada: junta grupos da mesma história que ficaram separados
    for (let i = 0; i < grupos.length; i++) {
      for (let j = i + 1; j < grupos.length; j++) {
        const a = grupos[i], b = grupos[j];
        if (b.t0 - a.t0 > 4 * 864e5) break;
        let liga = 0;
        for (const x of a.itens) for (const y of b.itens) if (mesmaHistoria(x, y)) liga++;
        // precisa de mais de uma ligação quando os dois grupos já são grandes
        if (liga && liga >= Math.min(2, Math.min(a.itens.length, b.itens.length))) { a.itens.push(...b.itens); grupos.splice(j, 1); j = i; }
      }
    }
    for (const g of grupos) {
      const fontes = new Map();
      for (const it of g.itens) for (const f of [{ f: it.f, u: it.u, s: it.s }, ...(it.o || [])]) if (f.u && !fontes.has(domDe(f))) fontes.set(domDe(f), f);
      g.fontes = [...fontes.values()];
      g.n = g.fontes.length;
      // a notícia que representa o grupo: a mais confiável, com resumo e foto
      g.it = [...g.itens].sort((a, b) => nivel(b) - nivel(a) || (b.rx ? 1 : 0) - (a.rx ? 1 : 0) || (b.i ? 1 : 0) - (a.i ? 1 : 0) || b.p - a.p)[0];
      g.ultima = g.itens.reduce((m, x) => (x.d > m ? x.d : m), "");
      // fonte original = o site que publicou primeiro
      const primeiro = g.itens.reduce((m, x) => (x.d < m.d ? x : m), g.itens[0]);
      g.orig = { f: primeiro.f, u: primeiro.u, s: primeiro.s };
      g.outras = g.fontes.filter((f) => domDe(f) !== domDe(g.orig));
      const comResumo = [g.it, ...g.itens].find((x) => x.rx) || [g.it, ...g.itens].find((x) => x.r);
      g.resumo = comResumo ? comResumo.rx || comResumo.r : "";
      g.cats = [...new Set(g.itens.flatMap((x) => x.c || []))];
      g.lanc = g.itens.some((x) => x.l);
      for (const it of g.itens) it._grupo = g;
    }
    return grupos;
  }
  // a notícia que vai para a tela: uma por história, com todos os sites que a publicaram
  function representante(g) {
    const it = g.it;
    return Object.assign(Object.create(Object.getPrototypeOf(it)), it, {
      f: g.orig.f, u: g.orig.u, s: g.orig.s, o: g.outras,
      r: (g.resumo || it.r || "").split("\n")[0], c: g.cats.slice(0, 4), l: g.lanc ? 1 : it.l,
      _ok: true, _cred: it._cred, _grupo: g, _ids: g.itens.map((x) => x.id),
    });
  }

  // ------------------------------------------------------------------ ranking das mais citadas
  const RANKING = { "24h": ["Últimas 24 horas", 1], semana: ["Última semana", 7], mes: ["Último mês", 30], ano: ["Último ano", 365] };
  let rankAtual = "24h";
  const rankCache = { chave: "", listas: {} };
  // calcula só o período pedido (o do ano carrega o arquivo inteiro, então fica para quando for aberto)
  async function dadosRanking() {
    if (rankCache.chave !== INDICE.atualizado) { rankCache.chave = INDICE.atualizado; rankCache.listas = {}; }
    const k = rankAtual;
    if (!rankCache.listas[k]) {
      const dias = RANKING[k][1];
      const todos = await itensDoPeriodo(somaDias(hojeBR(), -(dias + 1)), hojeBR());
      const agora = Date.now(), lim = dias * 864e5;
      const janela = todos.filter((it) => agora - Date.parse(it.d) <= lim);
      rankCache.listas[k] = agruparNoticias(janela)
        .sort((a, b) => b.n - a.n || (b.it.l || 0) - (a.it.l || 0) || nivel(b.it) - nivel(a.it) || b.it.p - a.it.p || b.ultima.localeCompare(a.ultima))
        .slice(0, 15);
    }
    return rankCache;
  }
  function htmlRanking(listas, completo) {
    const lista = listas[rankAtual] || [];
    const abas = Object.entries(RANKING).map(([k, [nome]]) => `<button data-rank="${k}" class="${k === rankAtual ? "ativo" : ""}">${nome}</button>`).join("");
    const quadros = lista.map((g, i) => {
      const it = g.it;
      const resumo = (g.resumo || "").split("\n").filter(Boolean);
      const outras = g.outras.slice(0, 10).map((f) => `<a href="${esc(f.u)}" target="_blank" rel="noopener" title="${esc(f.s || "")}">${esc(f.f)}</a>`).join("");
      const mais = g.outras.length > 10 ? `<span class="rq__mais">+${g.outras.length - 10}</span>` : "";
      const chipsG = chips({ l: g.lanc, c: g.cats }, i === 0 ? 4 : 2);
      return `<li class="rq${i === 0 ? " rq--primeiro" : i < 3 ? " rq--top" : ""}">
        <div class="rq__foto">${imagem(it)}<a class="capa__link" href="${hrefNoticia(it)}" tabindex="-1" aria-hidden="true"></a>
          <span class="rq__pos">${String(i + 1).padStart(2, "0")}</span>
          <span class="rq__n"><b>${g.n}</b>${g.n > 1 ? "sites" : "site"}</span></div>
        <div class="rq__corpo">
          ${chipsG}
          <h3 class="rq__titulo"><a href="${hrefNoticia(it)}">${esc(it.t)}</a></h3>
          <div class="rq__data">${fmtDiaLongo(it.dia)} · ${fmtHora(it.d)}</div>
          ${resumo.length ? `<p class="rq__resumo">${esc(resumo.join(" "))}</p>` : `<p class="rq__resumo rq__resumo--aguarde">O resumo em português está sendo preparado pelo robô.</p>`}
          <div class="rq__fontes">
            <a class="rq__orig" href="${esc(g.orig.u)}" target="_blank" rel="noopener"><span>★ Fonte original</span><b>${esc(g.orig.f)}</b>${g.orig.s ? `<small>${esc(g.orig.s)}</small>` : ""}<i>Ler ↗</i></a>
            ${outras ? `<div class="rq__outras"><span class="rq__rot">Também publicaram</span>${outras}${mais}</div>` : ""}
          </div>
          <a class="rq__ler" href="${hrefNoticia(it)}">Ler o resumo completo ▶</a>
        </div>
      </li>`;
    }).join("");
    return `<div class="ranking${completo ? " ranking--completo" : ""}" data-ranking>
      <div class="ranking__topo">
        <h2 class="titulo-secao titulo-secao--tipo"><svg viewBox="0 0 24 24" aria-hidden="true">${ICONES.ranking}</svg>Ranking: as 15 mais citadas <small>quantos sites do mundo publicaram a mesma notícia</small></h2>
        <div class="ranking__abas">${abas}</div>
      </div>
      ${lista.length ? `<ol class="rq-lista">${quadros}</ol>` : `<p class="painel__dica">Ainda não há notícias neste período.</p>`}
    </div>`;
  }
  const rankingNaInicial = () => false;  // o ranking tem a sua própria aba, ao lado de Destaques
  async function renderRankingInicio(id) {
    const el = $("#ranking");
    document.body.classList.toggle("com-ranking", rankingNaInicial());
    if (!rankingNaInicial()) { el.innerHTML = ""; return new Set(); }
    const r = await dadosRanking();
    if (id !== ultimoRender) return new Set();
    el.innerHTML = htmlRanking(r.listas, false);
    return new Set((r.listas[rankAtual] || []).flatMap((g) => g.itens.map((x) => x.id)));
  }

  // ------------------------------------------------------------------ página da notícia
  const TIPO_FONTE = { especializado: "Site especializado", imprensa: "Grande veículo internacional", tecnologia: "Site de tecnologia" };
  function infoFonte(dom, nome) {
    const c = credDe(dom, nome);
    return [TIPO_FONTE[c[2]] || (c[0] >= 3 ? "Grande veículo internacional" : c[0] >= 2 ? "Site de tecnologia" : ""), c[4] || ""].filter(Boolean).join(" · ");
  }
  async function acharNoticia(idN, dia) {
    const meses = dia ? [dia.slice(0, 7)] : Object.keys(INDICE.meses).sort().reverse();
    for (const m of meses) {
      await carregarMes(m);
      const dados = window.CR_DADOS[m] || {};
      const dias = dia && dados[dia] ? [dia, ...Object.keys(dados)] : Object.keys(dados);
      for (const d of dias) for (const it of dados[d] || []) if (it.id === idN) { it.dia = d; return it; }
    }
    return dia ? acharNoticia(idN, "") : null;
  }
  async function renderNoticia(id) {
    const el = $("#especial");
    document.body.classList.add("modo-especial");
    $("#especial").hidden = false;
    for (const s of ["#destaques", "#mais-destaques", "#outras"]) $(s).innerHTML = "";
    $("#aviso").hidden = $("#vazio").hidden = true;
    el.innerHTML = `<div class="vazio"><b>Carregando a notícia…</b></div>`;
    const it = await acharNoticia(estado.n, estado.em);
    if (id !== ultimoRender) return;
    if (!it) {
      el.innerHTML = `<div class="vazio"><b>Notícia não encontrada</b>Ela pode ter saído do arquivo. <a href="#">Voltar às notícias</a></div>`;
      return;
    }
    aprovar(it);
    document.title = it.t + " — Central Robótica";
    const original = it.lg && it.lg !== "pt" && it.to
      ? `<p class="noticia__original"><span>Título original (${esc(IDIOMAS[it.lg] || "idioma original")})</span>${esc(it.to)}</p>` : "";
    const perto = await itensDoPeriodo(somaDias(it.dia, -3), [somaDias(it.dia, 3), hojeBR()].sort()[0]);
    if (id !== ultimoRender) return;
    if (!perto.includes(it)) perto.push(it);
    agruparNoticias(perto);
    const g = it._grupo;
    const orig = g ? g.orig : { f: it.f, u: it.u, s: it.s };
    const outras = g ? g.outras : (it.o || []).filter((o) => o.u && o.u !== it.u);
    const resumo = ((g && g.resumo) || it.rx || it.r || "").split(/\n+/).filter(Boolean);
    const corpoResumo = resumo.length
      ? resumo.map((p) => `<p>${esc(p)}</p>`).join("")
      : `<p class="noticia__aguarde">O robô da Central Robótica ainda está preparando o resumo em português desta notícia. Enquanto isso, você pode ler a matéria completa no site original, logo abaixo.</p>`;
    const nSites = 1 + outras.length;
    const linhaFonte = (o) => {
      const tipo = infoFonte(o.s, o.f);
      return `<li><a href="${esc(o.u)}" target="_blank" rel="noopener">
        <span class="outra-fonte__nome"><b>${esc(o.f)}</b>${o.s ? `<small>${esc(o.s)}</small>` : ""}</span>
        ${tipo ? `<span class="outra-fonte__tipo">${esc(tipo)}</span>` : ""}<span class="outra-fonte__ler">Ler ↗</span></a></li>`;
    };
    // mais notícias do mesmo assunto, dos dias próximos
    const cat = (it.c || []).find((c) => c !== "geral");
    let rel = [];
    if (cat) {
      const vizinhas = await itensDoPeriodo(somaDias(it.dia, -6), it.dia);
      if (id !== ultimoRender) return;
      const meus = new Set(g ? g.itens.map((x) => x.id) : [it.id]);
      rel = agruparNoticias(vizinhas.filter((x) => !meus.has(x.id))).map(representante)
        .filter((x) => (x.c || []).includes(cat)).sort((a, b) => (b.l || 0) - (a.l || 0) || b.p - a.p).slice(0, 6);
    }
    const tipoOrig = infoFonte(orig.s, orig.f);
    el.innerHTML = `<article class="noticia">
      <button class="noticia__voltar" id="voltar-noticia">◀ Voltar às notícias</button>
      ${chips(it, 4)}
      <h1 class="noticia__titulo">${esc(it.t)}</h1>
      <div class="noticia__meta"><span>${fmtDiaLongo(it.dia)} · ${fmtHora(it.d)}</span>
        ${it.lg && it.lg !== "pt" ? `<span class="trad">Traduzido do ${esc(IDIOMAS[it.lg] || "idioma original")}</span>` : ""}
        <span>Publicado primeiro por <b>${esc(orig.f)}</b></span></div>
      <figure class="noticia__foto">${imagem(it)}</figure>
      <section class="noticia__resumo">
        <h2 class="titulo-secao">Resumo da notícia</h2>
        ${corpoResumo}
        ${original}
      </section>
      <section class="noticia__fontes">
        <h2 class="titulo-secao">Quem publicou esta notícia <small>${nSites} site${nSites > 1 ? "s" : ""}</small></h2>
        <a class="fonte-original" href="${esc(orig.u)}" target="_blank" rel="noopener">
          <span class="fonte-original__selo">★ Fonte original</span>
          <span class="fonte-original__nome"><b>${esc(orig.f)}</b>${orig.s ? `<small>${esc(orig.s)}</small>` : ""}</span>
          ${tipoOrig ? `<span class="fonte-original__tipo">${esc(tipoOrig)}</span>` : ""}
          <span class="fonte-original__ler">Ler a matéria completa no site original ↗</span>
        </a>
        ${outras.length ? `<h3 class="noticia__sub">Outros sites que também falam desta notícia</h3><ul class="outras-fontes">${outras.map(linhaFonte).join("")}</ul>` : ""}
      </section>
      ${rel.length ? `<section class="noticia__rel"><h2 class="titulo-secao">Mais notícias de ${esc(NOME_CAT[cat] || cat)}</h2><ul class="mini">${rel.map(miniNoticia).join("")}</ul></section>` : ""}
    </article>`;
    $("#voltar-noticia").addEventListener("click", () => {
      if (veioDoSite) history.back(); else irPara({ n: "", em: "" });
    });
    window.scrollTo({ top: 0, behavior: "instant" });
  }
  let veioDoSite = false;
  window.addEventListener("hashchange", () => { if (/[#&]n=/.test(location.hash)) veioDoSite = true; });

  // ------------------------------------------------------------------ render
  let ultimoRender = 0;
  async function render() {
    const id = ++ultimoRender;
    marcarControles();
    document.body.classList.toggle("modo-noticia", !!estado.n);
    if (estado.n) { await renderNoticia(id); return; }
    const especial = ESPECIAIS.has(estado.c);
    document.body.classList.toggle("modo-especial", especial);
    $("#especial").hidden = !especial;
    if (especial) {
      for (const s of ["#destaques", "#mais-destaques", "#outras"]) $(s).innerHTML = "";
      $("#aviso").hidden = $("#vazio").hidden = true;
      await renderEspecial(id);
      return;
    }
    $("#especial").innerHTML = "";
    let [i, f] = intervalo(estado.p, estado.d);
    let todos = await itensDoPeriodo(i, f);
    if (id !== ultimoRender) return;

    const aviso = $("#aviso");
    aviso.hidden = true;
    // "Hoje" mostra só as notícias do dia (sem trazer as de ontem)

    // busca
    let base = todos;
    if (estado.q) {
      const termos = semAcento(estado.q).split(/\s+/).filter(Boolean);
      base = todos.filter((it) => { const t = semAcento(`${it.t} ${it.r} ${it.f} ${it.to || ""} ${it.s || ""}`); return termos.every((x) => t.includes(x)); });
    }
    // uma notícia por história: matérias de sites diferentes sobre o mesmo assunto viram um quadro só
    base = agruparNoticias(base).map(representante);
    contarAbas(base);
    let itens = base.filter((it) => passaCategoria(it, estado.c));
    // página inicial: o ranking vai no topo e não se repete nas seções de baixo
    const noRanking = await renderRankingInicio(id);
    if (id !== ultimoRender) return;
    if (noRanking.size) itens = itens.filter((it) => !it._ids.some((x) => noRanking.has(x)));
    const multiDia = i !== f;

    renderLateral(base, itens);
    renderTicker(todos);

    const dest = $("#destaques"), mais = $("#mais-destaques"), outras = $("#outras"), vazio = $("#vazio");
    if (!itens.length) {
      dest.innerHTML = mais.innerHTML = outras.innerHTML = "";
      vazio.hidden = false;
      vazio.innerHTML = estado.q
        ? `<b>Nada encontrado</b>Nenhuma notícia com “${esc(estado.q)}” neste período e categoria.`
        : estado.p === "hoje"
          ? `<b>Ainda não há notícias de hoje</b>O robô reúne as notícias do dia a cada hora. <button class="mais" data-ir="dia" data-d="${somaDias(hojeBR(), -1)}">Ver as notícias de ontem</button>`
          : `<b>Sem notícias neste período</b>Tente outro dia, outra categoria ou consulte o arquivo ao lado.`;
      return;
    }
    vazio.hidden = true;

    // seleção dos destaques: relevância + bônus para quem tem imagem
    // lançamentos de robôs SEMPRE vêm primeiro; depois relevância (+ bônus para quem tem imagem)
    const nota = (it) => it.p + (it.i ? 1.2 : 0);
    // ordem: lançamentos > especializados e grandes veículos (nível) > foto própria > relevância
    const ranking = [...itens].sort((a, b) => (b.l || 0) - (a.l || 0) || nivel(b) - nivel(a) || (b.i ? 1 : 0) - (a.i ? 1 : 0) || nota(b) - nota(a) || b.d.localeCompare(a.d));
    const nDest = itens.length >= 8 ? 5 : Math.min(itens.length, 1);
    const topo = ranking.slice(0, nDest);
    const nCards = itens.length >= 14 ? 6 : itens.length >= 11 ? 3 : 0;
    const cards = ranking.slice(nDest, nDest + nCards);
    const usados = new Set([...topo, ...cards].map((x) => x.id));
    const resto = itens.filter((x) => !usados.has(x.id)).sort((a, b) => b.dia.localeCompare(a.dia) || (b.l || 0) - (a.l || 0) || nivel(b) - nivel(a) || b.p - a.p || b.d.localeCompare(a.d));

    const nomeCat = estado.c === "inicio" ? (noRanking.size ? "Outros destaques" : "Destaques") : NOME_CAT[estado.c];
    const titPeriodo = estado.p === "hoje" && i === hojeBR() ? "de hoje" : multiDia ? "do período" : "do dia";

    // resumo do ano: blocos por mês
    let blocoAno = "";
    if (estado.p === "ano") {
      const porMes = {};
      for (const it of itens) porMes[it.dia.slice(0, 7)] = (porMes[it.dia.slice(0, 7)] || 0) + 1;
      blocoAno = `<h2 class="titulo-secao">Mês a mês <small>${itens.length} notícias no ano</small></h2><div class="meses-ano">` +
        Object.keys(porMes).sort().map((m) => `<button class="mes-ano" data-mes="${m}"><b>${MESES[+m.slice(5) - 1]}</b><span>${porMes[m]}</span><small>notícias</small></button>`).join("") + "</div>";
    }

    dest.innerHTML = `${blocoAno}<h2 class="titulo-secao">${esc(nomeCat)} ${titPeriodo} <small>${itens.length} notícia${itens.length > 1 ? "s" : ""}</small></h2>
      <div class="destaques__grade">${htmlPrincipal(topo[0], multiDia)}${topo.length > 1 ? `<div class="secundarios">${topo.slice(1).map((x) => htmlSec(x, multiDia)).join("")}</div>` : ""}</div>`;
    if (topo.length === 1) dest.querySelector(".destaques__grade").style.gridTemplateColumns = "1fr";

    mais.innerHTML = cards.length ? `<h2 class="titulo-secao">Mais destaques</h2><div class="cards">${cards.map((x) => htmlCard(x, multiDia)).join("")}</div>` : "";

    const pagina = resto.slice(0, POR_PAGINA * estado.pagina);
    let h = resto.length ? `<h2 class="titulo-secao">Outras notícias <small>${resto.length}</small></h2>` : "";
    let diaAtual = null, aberto = false;
    for (const it of pagina) {
      if (it.dia !== diaAtual) {
        if (aberto) h += "</ul></div>";
        diaAtual = it.dia;
        const n = resto.filter((x) => x.dia === it.dia).length;
        h += `<div class="dia-grupo"><div class="dia-grupo__titulo">${fmtDiaLongo(it.dia)}<span>${n} notícia${n > 1 ? "s" : ""}</span></div><ul class="lista">`;
        aberto = true;
      }
      h += htmlMenor(it);
    }
    if (aberto) h += "</ul></div>";
    if (resto.length > pagina.length) h += `<button class="mais" id="carregar-mais">Carregar mais notícias (${resto.length - pagina.length})</button>`;
    outras.innerHTML = h;
  }

  function contarAbas(base) {
    for (const c of CATEGORIAS) {
      if (c.especial) continue;
      const el = document.querySelector(`.aba[data-c="${c.id}"] .aba__n`);
      if (el) el.textContent = base.filter((it) => passaCategoria(it, c.id)).length;
    }
  }

  function renderLateral(base) {
    // contagem por categoria
    const lista = CATEGORIAS.filter((c) => c.id !== "inicio" && !c.especial).map((c) => ({ ...c, n: base.filter((it) => passaCategoria(it, c.id)).length })).sort((a, b) => b.n - a.n);
    const max = Math.max(1, ...lista.map((c) => c.n));
    $("#contagem").innerHTML = lista.map((c) => `<li data-cat="${c.id}"><div class="contagem__linha"><span class="contagem__nome">${esc(NOME_CAT[c.id])}</span><b>${c.n}</b></div><div class="contagem__barra"><i style="width:${(c.n / max) * 100}%"></i></div></li>`).join("");

    // mais citadas
    const cit = agruparNoticias(base).filter((g) => g.n > 1).sort((a, b) => b.n - a.n || b.it.p - a.it.p).slice(0, 6);
    $("#citadas").innerHTML = cit.length ? cit.map((g) => `<li>${miniFoto(g.it)}<div>${link(g.it, g.it.t)}<small>${g.n} sites · ${esc(g.it.f)}</small></div></li>`).join("") : `<li style="display:block;color:var(--texto-3)">—</li>`;
  }

  function renderTicker(todos) {
    let lanc = todos.filter((x) => x.l).sort((a, b) => b.p - a.p).slice(0, 14);
    const t = $("#ticker");
    if (lanc.length < 3) { t.hidden = true; return; }
    t.hidden = false;
    const html = lanc.map((x) => link(x, x.t)).join("");
    $("#ticker-faixa").innerHTML = html + html;
  }

  function renderArquivo() {
    const anos = {};
    for (const m of Object.keys(INDICE.meses).sort().reverse()) {
      const a = m.slice(0, 4);
      (anos[a] = anos[a] || []).push(m);
    }
    const hoje = hojeBR();
    let h = "";
    Object.keys(anos).sort().reverse().forEach((a, ia) => {
      const totalAno = anos[a].reduce((s, m) => s + Object.values(INDICE.meses[m]).reduce((x, y) => x + y, 0), 0);
      h += `<details ${ia === 0 ? "open" : ""}><summary><span>${a}</span><small>${totalAno}</small></summary>
        <div class="acoes"><button data-ir="ano" data-d="${a}-01-01">Ver o ano</button></div>`;
      anos[a].forEach((m, im) => {
        const dias = INDICE.meses[m];
        const totalMes = Object.values(dias).reduce((x, y) => x + y, 0);
        h += `<details ${ia === 0 && im === 0 ? "open" : ""}><summary><span>${MESES[+m.slice(5) - 1]}</span><small>${totalMes}</small></summary>
          <div class="acoes"><button data-ir="mes" data-d="${m}-01">Ver o mês</button></div><div class="dias">` +
          Object.keys(dias).sort().reverse().map((d) => `<button data-ir="dia" data-d="${d}" class="${d === hoje ? "" : ""}" title="${fmtDiaLongo(d)}">${d.slice(8)}<small>${dias[d]}</small></button>`).join("") +
          "</div></details>";
      });
      h += "</details>";
    });
    $("#arquivo").innerHTML = h || `<p class="painel__dica">O histórico aparecerá aqui após a primeira coleta.</p>`;
  }

  // botões que levam a um dia fixo no passado (quantos dias antes de hoje)
  const DIAS_ATRAS = { ontem: 1, anteontem: 2 };

  // Botão "Atualizar": força o navegador a baixar de novo a página e os dados
  // (sem usar a cópia guardada) e recarrega mantendo a aba/período abertos.
  async function atualizarSite() {
    const b = $("#atualizar");
    if (b) { b.disabled = true; b.classList.add("girando"); b.querySelector("span").textContent = "Atualizando…"; }
    const arquivos = [location.pathname, "dados/indice.js", "dados/status.js", "dados/imagens.js", "dados/biblioteca/meta.js"];
    if (location.protocol.startsWith("http")) {
      await Promise.all(arquivos.map((u) => fetch(u, { cache: "reload" }).catch(() => null)));
    }
    location.reload();
  }

  function marcarControles() {
    document.querySelectorAll(".aba").forEach((b) => b.classList.toggle("ativa", b.dataset.c === estado.c));
    document.querySelectorAll(".atalho").forEach((a) => a.classList.toggle("ativo", a.getAttribute("href") === "#c=" + estado.c));
    document.querySelectorAll("#periodos button").forEach((b) => b.classList.toggle("ativo",
      DIAS_ATRAS[b.dataset.p] ? estado.p === "dia" && estado.d === somaDias(hojeBR(), -DIAS_ATRAS[b.dataset.p])
        : b.dataset.p === estado.p));
    $("#rotulo-periodo").textContent = rotulo(estado.p, estado.d);
    $("#seletor-data").value = estado.d;
    $("#seletor-data").max = hojeBR();
    const [, f] = intervalo(estado.p, estado.d);
    $("#proximo").disabled = f >= hojeBR();
    const dias = diasDisponiveis();
    const [i] = intervalo(estado.p, estado.d);
    $("#anterior").disabled = !dias.length || i <= dias[0];
    if ($("#busca").value !== estado.q) $("#busca").value = estado.q;
    document.querySelectorAll(".dias button").forEach((b) => b.classList.toggle("atual", (estado.p === "dia" || estado.p === "hoje") && b.dataset.d === estado.d));
    document.title = (estado.c === "inicio" ? "" : NOME_CAT[estado.c] + " — ") + "Central Robótica";
  }

  // ------------------------------------------------------------------ guias especiais
  const CAT = window.CR_CATALOGO || { robos: [], fabricantes: [], sites: [] };
  const REGIAO = (pais) => {
    if (/EUA/.test(pais)) return "EUA";
    if (/China|Hong Kong/.test(pais)) return "China";
    if (/Japão/.test(pais)) return "Japão";
    if (/Coreia/.test(pais)) return "Coreia do Sul";
    if (/Brasil/.test(pais)) return "Brasil";
    if (/Suíça|Alemanha|Dinamarca|Reino Unido|França|Suécia|Polônia|Noruega|Irlanda|Estônia|Itália|Espanha|Holanda/.test(pais)) return "Europa";
    return "Outros";
  };
  const STATUS_CLS = { "À venda": "st-venda", "Pré-venda": "st-pre", "Em operação": "st-oper", "Pilotos e testes": "st-teste", "Protótipo": "st-proto", "Em desenvolvimento": "st-proto", "Aposentado": "st-apos" };
  const ANO_ATUAL = +hojeBR().slice(0, 4);

  let TODAS = null;
  async function todasNoticias() {
    await Promise.all(Object.keys(INDICE.meses).map(carregarMes));
    if (TODAS) return TODAS;
    const out = [];
    for (const m in window.CR_DADOS) for (const dia in window.CR_DADOS[m]) for (const it of window.CR_DADOS[m][dia]) { if (it.nt || !aprovar(it)) continue; it.dia = dia; out.push(it); }
    out.sort((a, b) => b.d.localeCompare(a.d));
    return (TODAS = out);
  }
  function rxTermos(termos) {
    const alts = termos.filter(Boolean).map((s) => s.trim().replace(/[.*+?^${}()[\]\\]/g, "\\$&"));
    return new RegExp("(?<![\\p{L}\\p{N}])(?:" + alts.join("|") + ")(?![\\p{L}\\p{N}])", "u");
  }
  const termosRobo = (r) => (r.busca || r.nome).split("|");
  function termosFab(f) {
    const pular = new Set(["DEEP", "Ghost", "Standard", "Serve", "Clone", "Universal", "Engineered", "Rainbow", "Kepler", "Agility", "Sanctuary", "Booster", "Mobile"]);
    const out = [];
    for (let p of f.nome.split(/[()\/]/)) {
      p = p.trim(); if (!p) continue;
      out.push(p);
      const r = p.replace(/\s+(Robotics|Technologies|Electronics|MedTech|Innovation|Space|Surgical|Dynamics)$/, "").trim();
      if (r !== p && !pular.has(r) && (r.length >= 4 || /^[A-Z0-9]{2,}$/.test(r))) out.push(r);
    }
    return out;
  }
  const casa = (rx, it) => rx.test(it.t) || (it.to && rx.test(it.to));
  let BASE_CAT = null;
  async function baseCatalogo() {
    const todas = await todasNoticias();
    if (BASE_CAT && BASE_CAT.n === todas.length) return BASE_CAT;
    const fab = Object.fromEntries(CAT.fabricantes.map((f) => [f.id, { ...f, robos: [] }]));
    const robos = CAT.robos.map((r) => {
      const rx = rxTermos(termosRobo(r));
      const ns = todas.filter((it) => casa(rx, it));
      const rob = { ...r, fabr: fab[r.fab] || { nome: r.fab, pais: "" }, noticias: ns, img: (ns.find((x) => x.i) || {}).i || "" };
      if (fab[r.fab]) fab[r.fab].robos.push(rob);
      return rob;
    });
    for (const f of Object.values(fab)) {
      const rx = rxTermos(termosFab(f).concat(...f.robos.map(termosRobo)));
      f.noticias = todas.filter((it) => casa(rx, it));
      f.tipos = [...new Set(f.robos.map((r) => r.tipo))];
    }
    return (BASE_CAT = { n: todas.length, robos, fab, todas });
  }
  const passaBusca = (txt) => {
    if (!estado.q) return true;
    const t = semAcento(txt);
    return semAcento(estado.q).split(/\s+/).filter(Boolean).every((x) => t.includes(x));
  };
  const linkNoticias = (q, n) => `<a class="btn-noticias" href="#p=ano&d=${hojeBR()}&q=${encodeURIComponent(q)}">${n} notícia${n === 1 ? "" : "s"} →</a>`;
  function miniNoticia(it) {
    return `<li class="mini__item">${miniFoto(it)}<div><a href="${hrefNoticia(it)}">${it.l ? '<b class="mini-lanc">Lançamento</b> ' : ""}${esc(it.t)}</a><small>${fmtDiaCurto(it.dia)} · ${esc(it.f)}${it.s ? " (" + esc(it.s) + ")" : ""}</small></div></li>`;
  }
  // imagem com reserva: tenta a foto principal; se falhar, usa a ilustrativa dos assuntos
  function imgComReserva(src, chaves, semente, cat) {
    const f = escolherFoto(chaves, semente);
    if (!src) return f ? htmlFoto(f) : placeholder(cat);
    const alt = f ? encodeURIComponent(JSON.stringify(f)) : "";
    return `<img src="${esc(src)}" alt="" loading="lazy" referrerpolicy="no-referrer" data-cat="${esc(cat)}" data-alt="${alt}" onerror="CR_falhaImagem(this)">`;
  }
  function filtros(opcoes, atual, chave = "f") {
    return `<div class="filtros">${opcoes.map(([v, nome, n]) => `<button class="filtro ${v === atual ? "ativo" : ""}" data-${chave}="${esc(v)}">${esc(nome)}${n != null ? ` <span>${n}</span>` : ""}</button>`).join("")}</div>`;
  }
  function cabecalhoEspecial(titulo, sub) {
    return `<div class="esp-cab"><h1>${esc(titulo)}</h1><p>${sub}</p>${estado.q ? `<p class="esp-busca">Filtrando por “${esc(estado.q)}” <button data-limpar-busca>limpar</button></p>` : ""}</div>`;
  }

  async function renderEspecial(id) {
    const el = $("#especial");
    if (!el.innerHTML) el.innerHTML = `<div class="vazio"><b>Carregando…</b></div>`;
    const base = await baseCatalogo();
    if (id !== ultimoRender) return;
    if (estado.c === "ranking") {
      const r = await dadosRanking();
      if (id !== ultimoRender) return;
      el.innerHTML = cabecalhoEspecial("Ranking das mais citadas", "As notícias de robótica publicadas pelo maior número de sites do mundo — nas últimas 24 horas, na última semana, no último mês e no último ano. A contagem junta a mesma história publicada por sites de países e idiomas diferentes e se atualiza sozinha a cada coleta.") + htmlRanking(r.listas, true);
    }
    else if (estado.c === "catalogo") el.innerHTML = htmlCatalogo(base);
    else if (estado.c === "fabricantes") el.innerHTML = htmlFabricantes(base);
    else if (estado.c === "curiosidades") { await carregarBiblioteca(); if (id !== ultimoRender) return; el.innerHTML = htmlCuriosidades(base); }
    else if (estado.c === "universidades") {
      await carregarBiblioteca();
      const meses = Object.keys(bib().meta.arxiv || {}).sort().reverse();
      const mesArx = /^\d{4}-\d{2}$/.test(estado.g) ? estado.g : meses[0];
      if (mesArx) await carregarScript(`dados/biblioteca/arxiv/${mesArx}.js`, () => (window.CR_ARXIV || {})[mesArx]);
      if (id !== ultimoRender) return;
      el.innerHTML = htmlUniversidades(base, mesArx, meses);
    }
    else if (estado.c === "historia") el.innerHTML = htmlHistoria(base);
    else el.innerHTML = htmlSites(base);
    // faixa de lançamentos e contadores das abas também nas guias especiais
    renderTicker(base.todas.filter((x) => x.dia >= somaDias(hojeBR(), -3)));
    const dias = diasDisponiveis();
    const ultimo = dias[dias.length - 1];
    contarAbas(base.todas.filter((x) => x.dia === ultimo));
  }

  function htmlCatalogo(base) {
    const tipo = TIPOS.includes(estado.f) ? estado.f : "";
    const visiveis = base.robos.filter((r) => passaBusca(`${r.nome} ${r.fabr.nome} ${r.desc} ${r.fabr.pais} ${r.status}`));
    const contTipo = (t) => visiveis.filter((r) => r.tipo === t).length;
    let h = cabecalhoEspecial("Catálogo de robôs", `${CAT.robos.length} robôs de ${CAT.fabricantes.length} fabricantes, separados por tipo. Cada robô mostra as notícias reunidas pela Central Robótica.`);
    h += filtros([["", "Todos", visiveis.length], ...TIPOS.filter((t) => contTipo(t) > 0).map((t) => [t, NOME_CAT[t], contTipo(t)])], tipo);

    // lançamentos recentes no noticiário (prioridade)
    const limite = somaDias(hojeBR(), -14);
    const lanc = base.todas.filter((x) => x.l && x.dia >= limite && (!tipo || (x.c || []).includes(tipo))).sort((a, b) => (b.i ? 1 : 0) - (a.i ? 1 : 0) || b.p - a.p).slice(0, 6);
    if (lanc.length) {
      h += `<h2 class="titulo-secao">Lançamentos recentes no noticiário <small>últimos 14 dias</small></h2><div class="cards cards--lanc">${lanc.map((x) => htmlCard(x, true)).join("")}</div>`;
    }

    for (const t of TIPOS) {
      if (tipo && t !== tipo) continue;
      let lista = visiveis.filter((r) => r.tipo === t);
      if (!lista.length) continue;
      lista.sort((a, b) => (b.status === "Aposentado" ? -1 : 0) - (a.status === "Aposentado" ? -1 : 0) || b.ano - a.ano || b.noticias.length - a.noticias.length);
      h += `<h2 class="titulo-secao titulo-secao--tipo"><svg viewBox="0 0 24 24">${ICONES[t]}</svg>${esc(NOME_CAT[t])} <small>${lista.length} robô${lista.length > 1 ? "s" : ""}</small></h2><div class="robos">`;
      for (const r of lista) {
        const novo = r.ano >= ANO_ATUAL - 1 && r.status !== "Aposentado";
        const lancN = r.noticias.find((x) => x.l && x.dia >= somaDias(hojeBR(), -30));
        h += `<article class="robo">
          <div class="robo__capa">${imgComReserva(r.img, ["robo:" + r.nome, "fabq:" + r.fab, "cat:" + t], r.nome, t)}
            <div class="robo__selos">${lancN ? '<span class="chip chip--lanc">Lançamento recente</span>' : ""}${novo ? '<span class="chip">Novo</span>' : ""}</div></div>
          <div class="robo__corpo">
            <div class="robo__topo"><span class="status ${STATUS_CLS[r.status] || ""}">${esc(r.status)}</span><span class="robo__ano">${r.ano}</span></div>
            <h3>${esc(r.nome)}</h3>
            <a class="robo__fab" href="#c=fabricantes&q=${encodeURIComponent(r.fabr.nome)}">${esc(r.fabr.nome)} · ${esc(r.fabr.pais)}</a>
            <p>${esc(r.desc)}</p>
            ${r.noticias[0] ? `<div class="robo__ult"><span class="fonte__rot">Última notícia</span> <a href="${esc(r.noticias[0].u)}" target="_blank" rel="noopener">${esc(r.noticias[0].t)}</a> <small>${fmtDiaCurto(r.noticias[0].dia)} · ${esc(r.noticias[0].f)}</small></div>` : ""}
            <div class="robo__rodape">${r.noticias.length ? linkNoticias(termosRobo(r)[0], r.noticias.length) : '<span class="sem-noticias">Sem notícias no arquivo ainda</span>'}</div>
          </div></article>`;
      }
      h += "</div>";
    }
    if (!visiveis.length) h += `<div class="vazio"><b>Nenhum robô encontrado</b>Tente outro termo de busca.</div>`;
    return h;
  }

  function htmlFabricantes(base) {
    const regioes = ["EUA", "China", "Japão", "Coreia do Sul", "Europa", "Outros"];
    const reg = regioes.includes(estado.f) ? estado.f : "";
    const todos = Object.values(base.fab).filter((f) => passaBusca(`${f.nome} ${f.pais} ${f.sede} ${f.desc} ${f.robos.map((r) => r.nome).join(" ")}`));
    const lista = todos.filter((f) => !reg || REGIAO(f.pais) === reg).sort((a, b) => b.noticias.length - a.noticias.length || b.robos.length - a.robos.length || a.nome.localeCompare(b.nome));
    let h = cabecalhoEspecial("Fabricantes de robôs", `As principais fabricantes de robôs do mundo e seus robôs — ordenadas pelo volume de notícias no arquivo da Central Robótica.`);
    h += filtros([["", "Todas", todos.length], ...regioes.map((r) => [r, r, todos.filter((f) => REGIAO(f.pais) === r).length])], reg);
    h += `<div class="fabs">`;
    for (const f of lista) {
      const lanc = f.noticias.filter((x) => x.l).slice(0, 1);
      const ult = [...lanc, ...f.noticias.filter((x) => !lanc.includes(x))].slice(0, 3);
      h += `<article class="fab">
        <div class="fab__capa capa">${foto(["fab:" + f.id, "fabq:" + f.id, ...f.tipos.map((t) => "cat:" + t), "cat:geral"], f.id, f.tipos[0])}</div>
        <div class="fab__cab"><div><h3>${esc(f.nome)}</h3><span class="fab__pais">${esc(f.pais)} · ${esc(f.sede)} · desde ${f.fund}</span></div>
          <a class="fab__site" href="https://${esc(f.site)}" target="_blank" rel="noopener">${esc(f.site)} ↗</a></div>
        <p>${esc(f.desc)}</p>
        <div class="fab__tipos">${f.tipos.map((t) => `<span class="chip" data-f-tipo="${t}"><svg viewBox="0 0 24 24">${ICONES[t]}</svg>${esc(NOME_CAT[t])}</span>`).join("")}</div>
        <div class="fab__robos"><span class="fonte__rot">Robôs (${f.robos.length})</span>${f.robos.sort((a, b) => b.ano - a.ano).map((r) => `<a href="#c=catalogo&q=${encodeURIComponent(r.nome)}" class="robo-chip ${r.status === "Aposentado" ? "apos" : ""}" title="${esc(r.status)} · ${r.ano}">${esc(r.nome)} <small>${r.ano}</small></a>`).join("")}</div>
        <div class="fab__noticias"><span class="fonte__rot">Últimas notícias</span>${ult.length ? `<ul class="mini">${ult.map(miniNoticia).join("")}</ul>` : '<p class="sem-noticias">Sem notícias no arquivo ainda.</p>'}</div>
        <div class="robo__rodape">${f.noticias.length ? linkNoticias(termosFab(f).slice(-1)[0], f.noticias.length) : ""}</div>
      </article>`;
    }
    h += "</div>";
    if (!lista.length) h += `<div class="vazio"><b>Nenhum fabricante encontrado</b></div>`;
    return h;
  }

  function htmlSites(base) {
    // fontes: a tabela única do robô (todas as regiões); descrições extras vêm do catálogo
    const doDominio = (dom, d) => !!d && (d === dom || d.endsWith("." + dom));
    const extra = Object.fromEntries((CAT.sites || []).map((s) => [s.dom, s]));
    const GRUPOS = { especializado: "Especializados em robótica, drones e ciência", tecnologia: "Grandes sites de tecnologia", imprensa: "Grandes veículos de reconhecimento mundial" };
    const DESC = { especializado: "Site especializado em robótica, automação, drones ou ciência.", tecnologia: "Um dos grandes sites de tecnologia da região.", imprensa: "Veículo de imprensa de grande reconhecimento e credibilidade." };
    const vistos = new Set();
    const sites = Object.entries(MAIORES).filter(([dom, v]) => v.length >= 5 && !dom.endsWith(".br")).map(([dom, v]) => {
      const [nivelS, nome, grupo, regiao, pais] = v;
      const ex = extra[dom] || {};
      const ns = base.todas.filter((it) => doDominio(dom, (it.s || "").toLowerCase()) || (it.o || []).some((o) => doDominio(dom, (o.s || "").toLowerCase())));
      return { dom, nome, grupo, regiao, pais, nivel: nivelS, desc: ex.desc || DESC[grupo], url: ex.url || "https://" + dom, foco: ex.foco || GRUPOS[grupo].split(" ")[0], noticias: ns };
    }).filter((s) => { if (vistos.has(s.nome)) return false; vistos.add(s.nome); return true; })
      .filter((s) => passaBusca(`${s.nome} ${s.pais} ${s.regiao} ${s.desc} ${s.dom}`));
    const REGIOES = ["Mundo", "Américas", "Europa", "Ásia e Oriente Médio", "Oceania", "África"];
    const reg = REGIOES.includes(estado.f) ? estado.f : "";
    let h = cabecalhoEspecial("Sites do mundo", `A Central Robótica publica somente notícias de ${sites.length} fontes aprovadas: sites especializados em robótica, grandes sites de tecnologia e grandes veículos de reconhecimento mundial de todas as regiões. Sites genéricos, de pouco reconhecimento e brasileiros não entram.`);
    h += filtros([["", "Todas as regiões", sites.length], ...REGIOES.map((r) => [r, r === "Mundo" ? "Agências globais" : r, sites.filter((s) => s.regiao === r).length])], reg);
    for (const r of REGIOES) {
      if (reg && r !== reg) continue;
      const daRegiao = sites.filter((s) => s.regiao === r);
      if (!daRegiao.length) continue;
      h += `<h2 class="linha__era sites__regiao">${r === "Mundo" ? "Agências e veículos globais" : r} <small>${daRegiao.length} fontes</small></h2>`;
      for (const g of ["especializado", "tecnologia", "imprensa"]) {
        const lista = daRegiao.filter((s) => s.grupo === g).sort((a, b) => b.noticias.length - a.noticias.length || a.nome.localeCompare(b.nome));
        if (!lista.length) continue;
        h += `<h3 class="titulo-secao">${GRUPOS[g]} <small>${lista.length}</small></h3><div class="sites">`;
        for (const s of lista) {
          h += `<article class="site">
            <div class="fab__capa capa">${foto(["site:" + s.nome, "cat:geral"], s.dom)}</div>
            <div class="fab__cab"><div><h3>${esc(s.nome)}</h3><span class="fab__pais">${esc(s.pais)} · ${esc(s.dom)}</span></div><span class="chip">${esc(g === "imprensa" ? "Imprensa" : g === "tecnologia" ? "Tecnologia" : "Especializado")}</span></div>
            <p>${esc(s.desc)}</p>
            <div class="fab__noticias"><span class="fonte__rot">Últimas notícias reunidas</span>${s.noticias.length ? `<ul class="mini">${s.noticias.slice(0, 2).map(miniNoticia).join("")}</ul>` : '<p class="sem-noticias">Aguardando as próximas coletas.</p>'}</div>
            <div class="robo__rodape"><a class="fab__site" href="${esc(s.url)}" target="_blank" rel="noopener">Visitar o site ↗</a><span class="sem-noticias">${s.noticias.length} notícias no arquivo</span></div>
          </article>`;
        }
        h += "</div>";
      }
    }
    return h;
  }

  // ------------------------------------------------------------------ Curiosidades
  const CONT = window.CR_CONTEUDO || { fatos: [], documentarios: [], historia: [] };
  let sorteada = null;
  function diaDoAno() { const d = paraData(hojeBR()); return Math.floor((d - Date.UTC(d.getUTCFullYear(), 0, 0)) / 864e5); }

  function htmlCuriosidades(base) {
    const fatos = CONT.fatos.filter((f) => passaBusca(f.titulo + " " + f.texto));
    const n = diaDoAno();
    let vocesabia = "";
    const total = bib().meta.total + base.todas.filter((x) => x.cur).length;
    let h = cabecalhoEspecial("+1000 Curiosidades", `${total.toLocaleString("pt-BR")} matérias e curiosidades sobre robôs e robótica, reunidas de revistas, sites e universidades do mundo todo e traduzidas para o português. Novas matérias chegam sozinhas a cada coleta.`);
    if (fatos.length) {
      const dodia = fatos[n % fatos.length];
      h += `<div class="cur-dia"><div class="cur-dia__foto capa">${foto(["fato:" + dodia.titulo, "cat:geral"], dodia.titulo)}</div><div><span class="cur-dia__rot">Curiosidade do dia</span><h2>${esc(dodia.titulo)}</h2><p>${esc(dodia.texto)}</p></div></div>`;
      const outros = fatos.filter((f) => f !== dodia);
      const ini = n % Math.max(1, outros.length);
      const giro = outros.slice(ini).concat(outros.slice(0, ini));
      vocesabia = `<h2 class="titulo-secao">Você sabia? <small>curiosidades rápidas · mudam de ordem todo dia</small></h2><div class="fatos">${giro.map((f, i) => `<article class="fato"><div class="fab__capa capa">${foto(["fato:" + f.titulo, "cat:geral"], f.titulo)}</div><span class="fato__n">${String(i + 1).padStart(2, "0")}</span><h3>${esc(f.titulo)}</h3><p>${esc(f.texto)}</p></article>`).join("")}</div>`;
    }
    if (sorteada) h += `<div class="sorteio"><span class="cur-dia__rot">🎲 Curiosidade sorteada para você</span><div class="cards">${htmlMateria(sorteada)}</div></div>`;

    // biblioteca: matérias de revistas, sites e universidades + curiosidades do noticiário
    const lib = bibOk().map(paraMateria);
    const doNoticiario = base.todas.filter((x) => x.cur && !x.doc).map((x) => ({ ...x, origem: "noticiario", dia: x.dia }));
    const ids = new Set(lib.map((x) => x.u));
    let materias = lib.concat(doNoticiario.filter((x) => !ids.has(x.u)));
    const origens = [["", "Todas"], ["revista", "Revistas"], ["site", "Sites"], ["universidade", "Universidades e pesquisa"], ["noticiario", "Do noticiário"]];
    const origem = origens.some(([v]) => v === estado.f) ? estado.f : "";
    const tema = TIPOS.concat(["ia", "negocios", "competicoes"]).includes(estado.g) ? estado.g : "";
    materias = materias.filter((x) => passaBusca(`${x.t} ${x.r} ${x.f} ${x.pais || ""} ${x.inst || ""}`));
    const contOrig = (v) => materias.filter((x) => !v || x.origem === v).length;
    const porOrigem = materias.filter((x) => !origem || x.origem === origem);
    const contTema = (t) => porOrigem.filter((x) => (x.c || []).includes(t)).length;
    const lista = porOrigem.filter((x) => !tema || (x.c || []).includes(tema)).sort((a, b) => b.d.localeCompare(a.d));
    const paises = new Set(materias.map((x) => x.pais).filter(Boolean));
    h += `<h2 class="titulo-secao" id="biblioteca">Biblioteca de curiosidades <small>${materias.length.toLocaleString("pt-BR")} matérias · ${paises.size} países · atualizado automaticamente</small></h2>`;
    h += filtros(origens.map(([v, n]) => [v, n, contOrig(v)]), origem);
    h += `<div class="filtros filtros--tema">${[["", "Todos os temas"], ...TIPOS.concat(["ia", "negocios", "competicoes"]).filter((t) => contTema(t) > 0).map((t) => [t, NOME_CAT[t]])].map(([v, n]) => `<button class="filtro ${v === tema ? "ativo" : ""}" data-g="${v}">${esc(n)} ${v ? `<span>${contTema(v)}</span>` : ""}</button>`).join("")}
      <button class="filtro filtro--sorte" data-sorte>🎲 Surpreenda-me</button></div>`;
    if (lista.length) {
      const pag = lista.slice(0, 24 * estado.pagina);
      h += `<div class="cards cards--bib">${pag.map(htmlMateria).join("")}</div>`;
      if (lista.length > pag.length) h += `<button class="mais" id="carregar-mais">Carregar mais curiosidades (${(lista.length - pag.length).toLocaleString("pt-BR")})</button>`;
    } else h += `<p class="sem-noticias">Nenhuma matéria com esses filtros.</p>`;

    // documentários
    const docsNot = base.todas.filter((x) => x.doc).slice(0, 6);
    const docs = CONT.documentarios.filter((d) => passaBusca(`${d.titulo} ${d.desc} ${d.tema} ${d.direcao}`));
    h += `<h2 class="titulo-secao">Documentários <small>para assistir</small></h2>`;
    if (docsNot.length) h += `<p class="painel__dica">Documentários no noticiário (atualizado automaticamente):</p><div class="cards">${docsNot.map((x) => htmlCard(x, true)).join("")}</div><p class="painel__dica" style="margin-top:22px">Clássicos e destaques sobre robôs e inteligência artificial:</p>`;
    h += `<div class="docs">${docs.sort((a, b) => b.ano - a.ano).map((d) => {
      const q = encodeURIComponent(`${d.titulo} ${d.ano}`);
      return `<article class="doc"><div class="fab__capa capa">${foto(["doc:" + d.titulo, "cat:geral"], d.titulo)}</div><div class="doc__topo"><span class="doc__ano">${d.ano}</span><span class="chip">${esc(d.tema)}</span></div>
        <h3>${esc(d.titulo)}</h3><span class="fab__pais">${esc(d.origem)} · ${esc(d.direcao)}</span><p>${esc(d.desc)}</p>
        <div class="robo__rodape"><a class="btn-noticias" href="https://www.youtube.com/results?search_query=${q}+trailer" target="_blank" rel="noopener">▶ Trailer</a><a class="fab__site" href="https://www.justwatch.com/br/busca?q=${encodeURIComponent(d.titulo)}" target="_blank" rel="noopener">Onde assistir ↗</a></div></article>`;
    }).join("")}</div>`;
    return h + vocesabia;
  }

  // ------------------------------------------------------------------ Biblioteca (curiosidades e universidades)
  const carregados = {};
  function carregarScript(src, pronto) {
    if (pronto()) return Promise.resolve();
    if (!carregados[src]) {
      carregados[src] = new Promise((ok) => {
        const s = document.createElement("script");
        s.src = `${src}?v=${encodeURIComponent(INDICE.atualizado || "")}`;
        s.onload = s.onerror = () => ok();
        document.head.appendChild(s);
      });
    }
    return carregados[src];
  }
  const carregarBiblioteca = () => carregarScript("dados/biblioteca/biblioteca.js", () => window.CR_BIBLIOTECA);
  const bib = () => window.CR_BIBLIOTECA || { meta: { total: 0, arxiv: {} }, itens: [] };
  // biblioteca: nada do Brasil e nada de sites genéricos
  const BIB_FORA = new Set(["Big Think", "Jornal da USP", "Revista Pesquisa FAPESP", "Mundo Conectado"]);
  const bibOk = () => bib().itens.filter((x) => x.pais !== "Brasil" && !BIB_FORA.has(x.f));
  const NOME_TIPO = { revista: "Revista", site: "Site", universidade: "Universidade", pesquisa: "Pesquisa", periodico: "Periódico científico", noticiario: "Noticiário" };
  function paraMateria(x) {
    const origem = x.tipo === "pesquisa" || x.tipo === "periodico" ? "universidade" : x.tipo;
    let s = ""; try { s = new URL(x.u).hostname.replace(/^www\./, ""); } catch (e) { /* */ }
    return { ...x, origem, dia: x.d.slice(0, 10), s };
  }
  function htmlMateria(x) {
    const rotulo = x.origem === "noticiario" ? "Noticiário" : `${NOME_TIPO[x.tipo] || ""}${x.inst ? " · " + x.inst : ""}`;
    return `<article class="card card--mat"><div class="capa">${imagem(x)}<div class="chips"><span class="chip chip--origem">${esc(rotulo)}</span>${x.pais ? `<span class="chip">${esc(x.pais)}</span>` : ""}</div></div>
      <div class="card__corpo"><h3>${link(x, x.t)}</h3>${x.r ? `<p>${esc(x.r)}</p>` : ""}
      <div class="meta"><span>${fmtDiaCurto(x.dia)}</span>${x.lg && x.lg !== "pt" ? `<span class="trad" title="${esc(x.to || "")}">Traduzido do ${esc(IDIOMAS[x.lg] || "idioma original")}</span>` : ""}</div>
      ${fonte(x, true)}</div></article>`;
  }

  function htmlUniversidades(base, mesArx, mesesArx) {
    const todos = bibOk().map(paraMateria).filter((x) => ["universidade", "pesquisa", "periodico"].includes(x.tipo))
      .filter((x) => passaBusca(`${x.t} ${x.r} ${x.f} ${x.inst || ""} ${x.pais}`));
    const insts = {};
    for (const x of todos) { const k = x.inst || x.f; insts[k] = insts[k] || { n: 0, pais: x.pais }; insts[k].n++; }
    const inst = insts[estado.f] ? estado.f : "";
    const lista = todos.filter((x) => !inst || (x.inst || x.f) === inst).sort((a, b) => b.d.localeCompare(a.d));
    const paises = new Set(todos.map((x) => x.pais));
    let h = cabecalhoEspecial("Universidades", `Pesquisas em robótica publicadas por universidades e centros de pesquisa do mundo todo (${Object.keys(insts).length} instituições em ${paises.size} países) e os artigos científicos novos de robótica do arXiv — tudo traduzido para o português e atualizado automaticamente.`);
    h += filtros([["", "Todas", todos.length], ...Object.entries(insts).sort((a, b) => b[1].n - a[1].n).map(([k, v]) => [k, `${k} · ${v.pais}`, v.n])], inst);
    h += `<h2 class="titulo-secao">Pesquisa nas universidades <small>${lista.length} matérias</small></h2>`;
    if (lista.length) {
      const pag = lista.slice(0, 18 * estado.pagina);
      h += `<div class="cards cards--bib">${pag.map(htmlMateria).join("")}</div>`;
      if (lista.length > pag.length) h += `<button class="mais" id="carregar-mais">Carregar mais (${lista.length - pag.length})</button>`;
    } else h += `<p class="sem-noticias">As matérias das universidades aparecem aqui após a próxima coleta.</p>`;

    // arXiv
    const arts = ((window.CR_ARXIV || {})[mesArx] || []).filter((a) => passaBusca(`${a.t} ${a.r} ${a.au}`));
    h += `<h2 class="titulo-secao" id="artigos">Artigos científicos — arXiv (robótica) <small>${arts.length} artigos em ${mesArx ? MESES[+mesArx.slice(5) - 1] + " de " + mesArx.slice(0, 4) : "—"}</small></h2>
      <p class="painel__dica">Artigos de pesquisadores de universidades do mundo todo, publicados na categoria cs.RO do arXiv. Título e resumo traduzidos automaticamente.</p>`;
    if (mesesArx.length > 1) h += `<div class="filtros">${mesesArx.map((m) => `<button class="filtro ${m === mesArx ? "ativo" : ""}" data-g="${m}">${MESES[+m.slice(5) - 1]} ${m.slice(0, 4)}</button>`).join("")}</div>`;
    const lim = estado.f === "arxiv-todos" ? arts.length : 30;
    h += `<ul class="artigos">${arts.slice(0, lim).map((a) => `<li class="artigo"><div class="artigo__foto capa">${imagem(a)}</div><div class="artigo__corpo">
        <div class="artigo__topo"><span class="chip chip--origem">arXiv · cs.RO</span><span class="meta">${fmtDiaCurto(a.d.slice(0, 10))}</span>${(a.c || []).filter((c) => c !== "geral").slice(0, 2).map((c) => `<span class="chip">${esc(NOME_CAT[c] || c)}</span>`).join("")}</div>
        <h3><a href="${esc(a.u)}" target="_blank" rel="noopener" title="${esc(a.to)}">${esc(a.t)}</a></h3>
        <p class="artigo__autores">${esc(a.au || "")}</p><p>${esc(a.r)}</p>
        <div class="fonte"><div class="fonte__linha"><span class="fonte__rot">Fonte</span><a class="fonte__site" href="${esc(a.u)}" target="_blank" rel="noopener">arXiv.org</a><span class="fonte__dom">${esc(a.to)}</span>
        <a class="fonte__ler" href="${esc(a.u.replace("/abs/", "/pdf/"))}" target="_blank" rel="noopener">Ler o artigo (PDF) ↗</a></div></div></div></li>`).join("")}</ul>`;
    if (arts.length > lim) h += `<button class="mais" data-f="arxiv-todos">Ver todos os ${arts.length} artigos do mês</button>`;
    return h;
  }

  // ------------------------------------------------------------------ História
  function htmlHistoria(base) {
    const itens = CONT.historia.filter((e) => passaBusca(`${e.ano} ${e.titulo} ${e.texto} ${e.era}`));
    let h = cabecalhoEspecial("História da robótica", `Dos autômatos da Grécia Antiga aos humanoides com inteligência artificial. Os marcos recentes no fim da linha do tempo são gerados automaticamente a partir das notícias — a história continua sendo escrita todos os dias. <a href="#marcos-recentes" class="link-vermelho">Ir para os marcos recentes ↓</a>`);
    const eras = [...new Set(itens.map((e) => e.era))];
    h += `<div class="linha">`;
    for (const era of eras) {
      h += `<h2 class="linha__era">${esc(era)}</h2>`;
      for (const e of itens.filter((x) => x.era === era)) {
        h += `<article class="marco"><span class="marco__ano">${esc(e.ano)}</span><div class="marco__corpo marco__corpo--foto"><div class="marco__foto capa">${foto(["hist:" + e.titulo, "cat:geral"], e.titulo)}</div><div><h3>${esc(e.titulo)}</h3><p>${esc(e.texto)}</p></div></div></article>`;
      }
    }
    // marcos automáticos: os lançamentos mais importantes de cada mês do arquivo
    const porMes = {};
    for (const x of base.todas) if (x.l) (porMes[x.dia.slice(0, 7)] = porMes[x.dia.slice(0, 7)] || []).push(x);
    const meses = Object.keys(porMes).sort();
    h += `<h2 class="linha__era" id="marcos-recentes">Marcos recentes <small>atualizado automaticamente</small></h2>`;
    for (const m of meses) {
      const top = porMes[m].sort((a, b) => (b.o || []).length - (a.o || []).length || b.p - a.p).slice(0, 3);
      if (!passaBusca(top.map((x) => x.t).join(" "))) continue;
      h += `<article class="marco marco--auto"><span class="marco__ano">${MESES[+m.slice(5) - 1].slice(0, 3)} ${m.slice(0, 4)}</span><div class="marco__corpo"><div class="marco__destaque capa">${imagem(top.find((x) => x.i) || top[0])}</div><h3>Principais lançamentos do mês</h3><ul class="mini">${top.map(miniNoticia).join("")}</ul>
        <a class="btn-noticias" href="#c=lancamentos&p=mes&d=${m}-01">Todos os lançamentos de ${MESES[+m.slice(5) - 1]} →</a></div></article>`;
    }
    if (!meses.length) h += `<p class="sem-noticias">Os marcos recentes aparecem aqui conforme as notícias são coletadas.</p>`;
    h += `</div>`;
    return h;
  }

  // ------------------------------------------------------------------ status e auto-atualização
  function renderStatus() {
    const st = window.CR_STATUS;
    const el = $("#status");
    if (!el) return;
    if (!st) { el.innerHTML = `<li>Aguardando a primeira execução do robô.</li>`; return; }
    const fim = st.fim || st.inicio;
    const prox = new Date(new Date(fim).getTime() + 60 * 60 * 1000);
    const hm = (d) => new Intl.DateTimeFormat("pt-BR", { timeZone: "America/Sao_Paulo", hour: "2-digit", minute: "2-digit" }).format(d);
    const pct = st.imagens && st.imagens[1] ? Math.round((st.imagens[0] / st.imagens[1]) * 100) : null;
    el.innerHTML = [
      ["Última coleta", `${fmtDiaCurto(fim.slice(0, 10))} às ${fim.slice(11, 16)}`],
      ["Próxima coleta", `por volta das ${hm(prox)}`],
      ["Fontes lidas", `${st.fontes_ok} de ${st.fontes_total}`],
      ["Notícias novas", `${st.novas} na última coleta`],
      pct != null ? ["Com imagem", `${pct}% (cresce a cada coleta)`] : null,
    ].filter(Boolean).map(([a, b]) => `<li><span>${a}</span><b>${b}</b></li>`).join("");
  }
  function vigiarAtualizacoes() {
    let diaAtual = hojeBR();
    // virou o dia: atualiza a página "Hoje" sozinha
    setInterval(() => {
      if (hojeBR() !== diaAtual) {
        diaAtual = hojeBR();
        $("#data-hoje").textContent = fmtDiaLongo(diaAtual);
        if (estado.p === "hoje") { estado.d = diaAtual; render(); }
      }
    }, 60 * 1000);
    // chegaram notícias novas? (confere o índice a cada 5 minutos)
    setInterval(() => {
      const antes = (window.CR_INDICE || {}).atualizado;
      const s = document.createElement("script");
      s.src = `dados/indice.js?t=${Date.now()}`;
      s.onload = () => {
        s.remove();
        const depois = (window.CR_INDICE || {}).atualizado;
        if (depois && depois !== INDICE.atualizado) {
          $("#novidades").hidden = false;
          // se a página estiver parada (sem interação) há 10 min, recarrega sozinha
          if (Date.now() - ultimaInteracao > 10 * 60 * 1000) location.reload();
        }
      };
      s.onerror = () => s.remove();
      document.head.appendChild(s);
    }, 5 * 60 * 1000);
  }
  let ultimaInteracao = Date.now();
  ["click", "keydown", "scroll", "mousemove", "touchstart"].forEach((ev) => window.addEventListener(ev, () => (ultimaInteracao = Date.now()), { passive: true }));

  // ------------------------------------------------------------------ eventos
  function montar() {
    const BM = window.CR_BIB_META || {};
    const contEsp = {
      ranking: 15, catalogo: CAT.robos.length, fabricantes: CAT.fabricantes.length, sites: (CAT.sites || []).length, historia: CONT.historia.length,
      curiosidades: (BM.total || 0).toLocaleString("pt-BR"), universidades: ((BM.universidades || 0) + (BM.arxiv || 0)).toLocaleString("pt-BR"),
    };
    $("#abas").innerHTML = CATEGORIAS.map((c, i) => `${c.especial && c.id !== "ranking" && !CATEGORIAS[i - 1].especial ? '<span class="abas__sep"></span>' : ""}<button class="aba ${c.id === "ranking" ? "aba--ranking" : c.especial ? "aba--esp" : ""}" data-c="${c.id}"><svg viewBox="0 0 24 24" aria-hidden="true">${ICONES[c.id]}</svg>${esc(c.nome)}<span class="aba__n">${c.especial ? contEsp[c.id] : 0}</span></button>`).join("");
    $("#abas").addEventListener("click", (e) => { const b = e.target.closest(".aba"); if (b) irPara({ c: b.dataset.c, f: "", pagina: 1 }); });
    $("#recarregar").addEventListener("click", atualizarSite);
    $("#atualizar").addEventListener("click", atualizarSite);

    $("#periodos").addEventListener("click", (e) => {
      const b = e.target.closest("button"); if (!b) return;
      const p = b.dataset.p;
      if (DIAS_ATRAS[p]) { irPara({ p: "dia", d: somaDias(hojeBR(), -DIAS_ATRAS[p]), pagina: 1 }); return; }
      irPara({ p, d: p === "hoje" ? hojeBR() : estado.d, pagina: 1 });
    });
    const passo = (n) => {
      const p = estado.p === "hoje" ? "dia" : estado.p;
      let d = estado.d;
      if (p === "dia") d = somaDias(d, n);
      else if (p === "semana") d = somaDias(d, 7 * n);
      else if (p === "mes") d = somaMeses(d, n);
      else d = somaMeses(d, 12 * n);
      if (d > hojeBR()) d = hojeBR();
      irPara({ p: p === "dia" && d === hojeBR() ? "hoje" : p, d, pagina: 1 });
    };
    $("#anterior").addEventListener("click", () => passo(-1));
    $("#proximo").addEventListener("click", () => passo(1));
    $("#seletor-data").addEventListener("change", (e) => {
      const d = e.target.value; if (!d) return;
      irPara({ p: estado.p === "hoje" ? (d === hojeBR() ? "hoje" : "dia") : estado.p, d, pagina: 1 });
    });

    let t;
    $("#busca").addEventListener("input", (e) => { clearTimeout(t); t = setTimeout(() => irPara({ q: e.target.value.trim(), pagina: 1 }), 250); });

    document.body.addEventListener("click", async (e) => {
      const rk = e.target.closest("[data-rank]");
      if (rk) {
        rankAtual = rk.dataset.rank;
        if (rankingNaInicial() && !ESPECIAIS.has(estado.c) && !estado.n) { render(); return; }
        const r = await dadosRanking();
        document.querySelectorAll("[data-ranking]").forEach((el) => { el.outerHTML = htmlRanking(r.listas, el.classList.contains("ranking--completo")); });
        return;
      }
      const filtro = e.target.closest("[data-f]");
      if (filtro) { irPara({ f: filtro.dataset.f, pagina: 1 }); return; }
      const filtroG = e.target.closest("[data-g]");
      if (filtroG) { irPara({ g: filtroG.dataset.g, pagina: 1 }); return; }
      if (e.target.closest("[data-sorte]")) {
        const itens = bibOk();
        if (itens.length) { sorteada = paraMateria(itens[Math.floor(Math.random() * itens.length)]); render(); setTimeout(() => document.querySelector(".sorteio")?.scrollIntoView({ behavior: "smooth", block: "center" }), 80); }
        return;
      }
      const ftipo = e.target.closest("[data-f-tipo]");
      if (ftipo) { irPara({ c: "catalogo", f: ftipo.dataset.fTipo, q: "" }); window.scrollTo({ top: 0, behavior: "smooth" }); return; }
      if (e.target.closest("[data-limpar-busca]")) { irPara({ q: "" }); return; }
      const chip = e.target.closest(".chip[data-cat], .contagem li[data-cat]");
      if (chip) { e.preventDefault(); irPara({ c: chip.dataset.cat, pagina: 1 }); window.scrollTo({ top: 0, behavior: "smooth" }); return; }
      const ir = e.target.closest("[data-ir]");
      if (ir) { irPara({ p: ir.dataset.d === hojeBR() && ir.dataset.ir === "dia" ? "hoje" : ir.dataset.ir, d: ir.dataset.d, pagina: 1 }); window.scrollTo({ top: 0, behavior: "smooth" }); return; }
      const mes = e.target.closest("[data-mes]");
      if (mes) { irPara({ p: "mes", d: mes.dataset.mes + "-01", pagina: 1 }); window.scrollTo({ top: 0, behavior: "smooth" }); return; }
      if (e.target.id === "carregar-mais") { estado.pagina++; render(); }
    });
    $(".logo").addEventListener("click", (e) => { e.preventDefault(); irPara({ c: "inicio", p: "hoje", d: hojeBR(), q: "", pagina: 1 }); });
    window.addEventListener("popstate", () => { lerHash(); render(); });
    window.addEventListener("hashchange", () => { lerHash(); render(); });

    // cabeçalho
    $("#data-hoje").textContent = fmtDiaLongo(hojeBR());
    if (INDICE.atualizado) {
      const a = INDICE.atualizado;
      $("#atualizado").textContent = `Atualizado em ${fmtDiaCurto(a.slice(0, 10))} às ${a.slice(11, 16)}`;
    } else $("#atualizado").textContent = "Aguardando a primeira coleta";
    $("#total-historico").textContent = INDICE.total ? `${INDICE.total.toLocaleString("pt-BR")} notícias no arquivo` : "";

    // fontes no rodapé
    // só os sites aprovados (especializados e grandes veículos do mundo — nada do Brasil)
    const vistos = new Set();
    const fontes = Object.entries(MAIORES).filter(([dom, v]) => !dom.endsWith(".br") && v[1] && !vistos.has(v[1]) && vistos.add(v[1]))
      .map(([dom, v]) => [v[1], dom]).sort((a, b) => a[0].localeCompare(b[0], "pt"));
    $("#fontes").innerHTML = fontes.map(([nome, dom]) => `<a href="https://${esc(dom)}" target="_blank" rel="noopener" title="${esc(dom)}">${esc(nome)}</a>`).join("") || "—";

    renderArquivo();
    renderStatus();
    vigiarAtualizacoes();
  }

  montar();
  lerHash();
  render();
})();
