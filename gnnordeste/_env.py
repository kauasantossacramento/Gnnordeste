"""Carrega variáveis de um arquivo .env simples (CHAVE=valor), sem dependências."""
import os
from pathlib import Path


def carregar(caminho):
    p = Path(caminho)
    if not p.exists():
        return
    for linha in p.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        k, v = linha.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
