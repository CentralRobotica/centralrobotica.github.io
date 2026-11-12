# -*- coding: utf-8 -*-
"""
Central Robótica — gerenciador automático de atualização.

É este script que o Agendador de Tarefas do Windows (ou o GitHub Actions)
executa de hora em hora. Ele:
  1. impede duas coletas ao mesmo tempo (trava);
  2. roda a coleta completa (notícias, traduções, imagens, curiosidades,
     marcos da história, status) e grava um log por dia em logs/;
  3. apaga logs com mais de 30 dias;
  4. se a pasta for um repositório git com "remote" configurado, envia as
     notícias novas para a internet (GitHub Pages) automaticamente.

Uso manual:  python coletor/gerenciador.py
"""
import contextlib
import io
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PASTA_LOGS = os.path.join(RAIZ, "logs")
TRAVA = os.path.join(RAIZ, "dados", ".coletando.lock")
TRAVA_VENCIDA = 55 * 60  # segundos: uma trava mais velha que isso é de uma coleta que travou
BRASILIA = timezone(timedelta(hours=-3))

sys.path.insert(0, AQUI)


def agora():
    return datetime.now(BRASILIA)


def pegar_trava():
    if os.path.exists(TRAVA):
        idade = time.time() - os.path.getmtime(TRAVA)
        if idade < TRAVA_VENCIDA:
            return False
        os.remove(TRAVA)
    os.makedirs(os.path.dirname(TRAVA), exist_ok=True)
    with open(TRAVA, "w", encoding="utf-8") as f:
        f.write(f"{os.getpid()} {agora().isoformat()}")
    return True


def soltar_trava():
    with contextlib.suppress(FileNotFoundError):
        os.remove(TRAVA)


def limpar_logs(dias=30):
    if not os.path.isdir(PASTA_LOGS):
        return
    limite = time.time() - dias * 86400
    for nome in os.listdir(PASTA_LOGS):
        caminho = os.path.join(PASTA_LOGS, nome)
        if nome.endswith(".log") and os.path.getmtime(caminho) < limite:
            os.remove(caminho)


def git(*args):
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace")


def publicar(log):
    """Envia as notícias novas para o GitHub, se a pasta estiver ligada a um repositório."""
    if not os.path.isdir(os.path.join(RAIZ, ".git")):
        return
    if not git("remote").stdout.strip():
        log("git: sem 'remote' configurado — publicação ignorada.")
        return
    git("pull", "--rebase", "--autostash")
    git("add", "dados")
    if git("diff", "--cached", "--quiet").returncode == 0:
        log("git: nada novo para publicar.")
        return
    msg = f"Notícias atualizadas em {agora():%d/%m/%Y %H:%M}"
    r = git("commit", "-m", msg)
    log("git commit: " + (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr) else "git commit")
    r = git("push")
    log("git push: " + ("ok" if r.returncode == 0 else r.stderr.strip()[-300:]))


def main():
    os.makedirs(PASTA_LOGS, exist_ok=True)
    arq_log = os.path.join(PASTA_LOGS, f"coleta_{agora():%Y-%m-%d}.log")

    def log(msg):
        with open(arq_log, "a", encoding="utf-8") as f:
            f.write(f"[{agora():%H:%M:%S}] {msg}\n")

    if not pegar_trava():
        log("Outra coleta ainda está rodando — esta execução foi pulada.")
        return 0
    inicio = time.time()
    log("=== Início da coleta automática ===")
    codigo = 0
    try:
        # 1) notícias  2) biblioteca (curiosidades, universidades e artigos científicos)
        for etapa in ("atualizar", "biblioteca"):
            buffer = io.StringIO()
            try:
                modulo = __import__(etapa)
                with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                    modulo.main()
            except Exception:
                codigo = 1
                buffer.write(f"ERRO na etapa {etapa}:\n" + traceback.format_exc())
            with open(arq_log, "a", encoding="utf-8") as f:
                f.write(f"--- {etapa} ---\n" + buffer.getvalue())
        publicar(log)
    except Exception:
        codigo = 1
        log("ERRO na coleta:\n" + traceback.format_exc())
    finally:
        soltar_trava()
        limpar_logs()
        log(f"=== Fim ({time.time() - inicio:.0f} s) ===\n")
    return codigo


if __name__ == "__main__":
    sys.exit(main())
