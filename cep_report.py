"""Consulta CEPs em lote (API ViaCEP) e gera um relatório CSV."""
import argparse
import csv
import sys
import time
from pathlib import Path

import requests

VIACEP_URL = "https://viacep.com.br/ws/{cep}/json/"
CSV_FIELDS = [
    "cep", "logradouro", "bairro", "localidade", "uf",
    "ibge", "ddd", "status", "erro",
]


def normalizar_cep(cep: str) -> str:
    return "".join(ch for ch in cep if ch.isdigit())


def consultar_cep(cep: str, timeout: float = 10.0) -> dict:
    cep_limpo = normalizar_cep(cep)

    if len(cep_limpo) != 8:
        return {"cep": cep, "status": "invalido", "erro": "CEP deve ter 8 dígitos"}

    try:
        resposta = requests.get(VIACEP_URL.format(cep=cep_limpo), timeout=timeout)
        resposta.raise_for_status()
    except requests.RequestException as exc:
        return {"cep": cep, "status": "erro_rede", "erro": str(exc)}

    dados = resposta.json()

    if dados.get("erro"):
        return {"cep": cep, "status": "nao_encontrado", "erro": "CEP não encontrado"}

    return {
        "cep": dados.get("cep", cep),
        "logradouro": dados.get("logradouro", ""),
        "bairro": dados.get("bairro", ""),
        "localidade": dados.get("localidade", ""),
        "uf": dados.get("uf", ""),
        "ibge": dados.get("ibge", ""),
        "ddd": dados.get("ddd", ""),
        "status": "ok",
        "erro": "",
    }


def ler_ceps_do_arquivo(caminho: Path) -> list[str]:
    with caminho.open(encoding="utf-8") as arquivo:
        return [linha.strip() for linha in arquivo if linha.strip()]


def gerar_relatorio(ceps: list[str], saida: Path, pausa: float = 0.0) -> int:
    linhas_com_erro = 0
    cache: dict[str, dict] = {}
    consultas_evitadas = 0

    with saida.open("w", newline="", encoding="utf-8") as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=CSV_FIELDS)
        escritor.writeheader()

        for i, cep in enumerate(ceps):
            cep_limpo = normalizar_cep(cep)
            veio_do_cache = cep_limpo in cache

            if veio_do_cache:
                resultado = {**cache[cep_limpo], "cep": cep}
                consultas_evitadas += 1
            else:
                resultado = consultar_cep(cep)
                if resultado["status"] in ("ok", "nao_encontrado"):
                    cache[cep_limpo] = resultado

            escritor.writerow(resultado)

            if resultado["status"] != "ok":
                linhas_com_erro += 1

            if pausa and i < len(ceps) - 1 and not veio_do_cache:
                time.sleep(pausa)

    if consultas_evitadas:
        print(f"CEPs repetidos reaproveitados do cache: {consultas_evitadas}")

    return linhas_com_erro


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consulta uma lista de CEPs na API ViaCEP e gera um relatório em CSV."
    )
    parser.add_argument(
        "--arquivo", "-a", type=Path, help="Arquivo .txt com um CEP por linha"
    )
    parser.add_argument(
        "--cep", "-c", action="append", help="CEP individual (pode ser usado várias vezes)"
    )
    parser.add_argument(
        "--saida", "-o", type=Path, default=Path("relatorio.csv"),
        help="Caminho do CSV de saída (padrão: relatorio.csv)"
    )
    parser.add_argument(
        "--pausa", type=float, default=0.0,
        help="Segundos de pausa entre consultas (evita sobrecarregar a API)"
    )
    args = parser.parse_args()

    ceps: list[str] = []
    if args.arquivo:
        ceps.extend(ler_ceps_do_arquivo(args.arquivo))
    if args.cep:
        ceps.extend(args.cep)

    if not ceps:
        parser.error("informe --arquivo e/ou --cep com ao menos um CEP")

    erros = gerar_relatorio(ceps, args.saida, args.pausa)
    total = len(ceps)

    print(f"Relatório gerado em: {args.saida}")
    print(f"Total de CEPs: {total} | Sucesso: {total - erros} | Com erro: {erros}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
