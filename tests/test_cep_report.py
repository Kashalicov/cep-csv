import csv
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from cep_report import normalizar_cep, consultar_cep, gerar_relatorio, ler_ceps_do_arquivo


def test_normalizar_cep_remove_caracteres_nao_numericos():
    assert normalizar_cep("01310-100") == "01310100"


def test_normalizar_cep_ja_limpo():
    assert normalizar_cep("01310100") == "01310100"


def test_consultar_cep_invalido_sem_chamar_api():
    resultado = consultar_cep("123")
    assert resultado["status"] == "invalido"


@patch("cep_report.requests.get")
def test_consultar_cep_sucesso(mock_get):
    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: {
            "cep": "01310-100", "logradouro": "Av. Paulista", "bairro": "Bela Vista",
            "localidade": "São Paulo", "uf": "SP", "ibge": "3550308", "ddd": "11",
        },
    )
    mock_get.return_value.raise_for_status = lambda: None

    resultado = consultar_cep("01310100")

    assert resultado["status"] == "ok"
    assert resultado["localidade"] == "São Paulo"


@patch("cep_report.requests.get")
def test_consultar_cep_nao_encontrado(mock_get):
    mock_get.return_value = Mock(status_code=200, json=lambda: {"erro": True})
    mock_get.return_value.raise_for_status = lambda: None

    resultado = consultar_cep("00000000")

    assert resultado["status"] == "nao_encontrado"


@patch("cep_report.requests.get")
def test_consultar_cep_erro_rede(mock_get):
    import requests
    mock_get.side_effect = requests.ConnectionError("falha de conexão")

    resultado = consultar_cep("01310100")

    assert resultado["status"] == "erro_rede"


@patch("cep_report.consultar_cep")
def test_gerar_relatorio_usa_cache_para_cep_repetido(mock_consultar, tmp_path: Path):
    mock_consultar.return_value = {
        "cep": "01310100", "status": "ok", "erro": "", "logradouro": "Av. Paulista",
        "bairro": "", "localidade": "", "uf": "", "ibge": "", "ddd": "",
    }
    saida = tmp_path / "relatorio.csv"

    erros = gerar_relatorio(["01310-100", "01310100", "01310-100"], saida)

    assert erros == 0
    assert mock_consultar.call_count == 1

    with saida.open(encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    assert len(linhas) == 3
    assert all(linha["logradouro"] == "Av. Paulista" for linha in linhas)


def test_ler_ceps_do_arquivo(tmp_path: Path):
    arquivo = tmp_path / "ceps.txt"
    arquivo.write_text("01310-100\n\n20040-020\n", encoding="utf-8")

    ceps = ler_ceps_do_arquivo(arquivo)

    assert ceps == ["01310-100", "20040-020"]


@patch("cep_report.consultar_cep")
def test_gerar_relatorio_cria_csv_com_cabecalho(mock_consultar, tmp_path: Path):
    mock_consultar.side_effect = [
        {"cep": "01310100", "status": "ok", "erro": "", "logradouro": "", "bairro": "", "localidade": "", "uf": "", "ibge": "", "ddd": ""},
        {"cep": "000", "status": "invalido", "erro": "CEP deve ter 8 dígitos", "logradouro": "", "bairro": "", "localidade": "", "uf": "", "ibge": "", "ddd": ""},
    ]
    saida = tmp_path / "relatorio.csv"

    erros = gerar_relatorio(["01310100", "000"], saida)

    assert erros == 1
    with saida.open(encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    assert len(linhas) == 2
    assert linhas[0]["status"] == "ok"
