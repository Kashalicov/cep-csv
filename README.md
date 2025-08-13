# 📌 Busca de CEP / Relatório CSV

> Consulta uma lista de CEPs na API ViaCEP e gera um relatório em CSV com endereço completo, cidade, UF e status de cada consulta.

![status](https://img.shields.io/badge/status-conclu%C3%ADdo-brightgreen)
![license](https://img.shields.io/badge/license-MIT-blue)

> 🌱 Um dos meus primeiros projetos em Python, feito enquanto eu estudava consumo de APIs e manipulação de arquivos.

## 🧠 Sobre o projeto

Ferramenta de linha de comando para quem precisa validar ou enriquecer uma lista de endereços a partir de CEPs — por exemplo, para conferir uma base de clientes ou preparar uma planilha de entregas. Recebe um arquivo `.txt` com um CEP por linha (e/ou CEPs avulsos via linha de comando), consulta cada um na API pública [ViaCEP](https://viacep.com.br/) e gera um CSV com o resultado, incluindo CEPs inválidos ou não encontrados.

## ✨ Funcionalidades

- Consulta em lote a partir de um arquivo `.txt` com um CEP por linha
- Consulta de CEPs avulsos direto pela linha de comando (`--cep`)
- Geração de relatório `.csv` com logradouro, bairro, cidade, UF, IBGE e DDD
- Tratamento de CEP inválido, CEP não encontrado e falha de rede sem interromper o lote
- Pausa configurável entre requisições para não sobrecarregar a API
- Resumo final no terminal (total, sucesso, erros)

## 🛠️ Tecnologias

- Python 3
- `requests` (consumo da API ViaCEP)
- `argparse` (interface de linha de comando)
- `csv` (geração do relatório)
- `pytest` (testes automatizados)

## 📂 Estrutura do projeto

```
01-cep-csv/
├── cep_report.py
├── exemplo_ceps.txt
├── requirements.txt
├── docs/
├── tests/
│   └── test_cep_report.py
└── README.md
```

## ▶️ Como rodar localmente

```bash
# clonar o repositório
git clone https://github.com/Kashalicov/cep-csv.git
cd cep-csv

# instalar dependências
pip install -r requirements.txt

# rodar com um arquivo de CEPs
python cep_report.py --arquivo exemplo_ceps.txt --saida relatorio.csv

# ou consultar CEPs avulsos
python cep_report.py --cep 01310-100 --cep 20040-020
```

## ✅ Testes

```bash
pytest tests/ -v
```

## 📚 O que eu aprendi

Esse foi o primeiro projeto do meu portfólio, focado em manter o escopo enxuto: uma ferramenta de linha de comando que resolve um problema real (validar/enriquecer endereços a partir de CEP) sem funcionalidades além do necessário. Aprofundei tratamento de erros de rede e de dados inconsistentes (CEP mal formatado, CEP inexistente) sem deixar o programa quebrar no meio de um lote grande, e pratiquei o uso de mocks (`unittest.mock`) para testar código que depende de uma API externa sem fazer chamadas reais nos testes.

## 🚧 Possíveis melhorias futuras

- Suporte a exportação também em `.xlsx`
- Barra de progresso para lotes grandes
- Cache local para evitar reconsultar o mesmo CEP

## 👤 Autor

**Júnior Rodrigues**
Coordenador de T.I. na Fundação Banco de Olhos | Estudante de Ciência da Computação
[LinkedIn](https://www.linkedin.com/feed/) · [GitHub](https://github.com/Kashalicov)
