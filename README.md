# 🗞️ Hacker News Scraper

Projeto de web scraping do [Hacker News](https://news.ycombinator.com/) que coleta todos os posts disponíveis, enriquece cada um com o país de origem do domínio via IANA, armazena no MongoDB e gera relatórios de análise e gráficos.

---

## 📁 Estrutura do projeto

```
.
├── main.py              # Script principal — orquestra tudo
├── scraper.py           # Loop de páginas, parse do HTML e salvamento
├── country.py           # Resolução de país via IANA (com cache)
├── analysis.py          # Agregações MongoDB, impressão e exportação
├── database.py          # Conexão com MongoDB e criação dos índices
├── charts.py            # Geração de gráficos com matplotlib
├── Dockerfile           # Imagem Python para rodar o scraper
├── docker-compose.yml   # Sobe o MongoDB + scraper juntos
├── requirements.txt     # Dependências Python
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline de CI (pytest + Docker build)
├── tests/
│   ├── test_country.py          # Testes de resolução de país
│   └── test_scraper.py          # Testes de parse do HTML
├── charts/                      # Gerado após a execução
├── top_10_dominios.csv          # Gerado após a execução
└── distribuicao_paises.json     # Gerado após a execução
```

---

## 🚀 Como rodar

### Pré-requisitos

- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/) instalados

### 1. Clone o repositório

```bash
git clone https://github.com/paulorolinski/scraping-hacker-news
cd hacker-news-scraper
```

### 2. Suba os containers

```bash
docker compose up --build
```

Isso irá:
1. Subir um container com **MongoDB** na porta `27017`
2. Construir e rodar o container do **scraper**
3. Percorrer todas as páginas do Hacker News, salvando os posts no banco
4. Rodar as análises e gerar os arquivos de exportação
5. Gerar os gráficos na pasta `charts/`
6. Desligar o container do scraper automaticamente ao terminar

> ⏳ **O scraping completo leva alguns minutos** — o script percorre todas as páginas do Hacker News e consulta a IANA para cada domínio único. Acompanhe o progresso em tempo real com o passo abaixo.

### 3. Acompanhe o progresso em tempo real

Em outro terminal, rode:

```bash
docker compose logs -f scraper
```

Você verá cada post sendo salvo conforme o scraping avança. Quando o container encerrar, o processo terminou com sucesso.

---

## 📊 Resultados

### Terminal

Ao final da execução, o scraper imprime automaticamente:

```
========================================
ANÁLISE DOS DADOS
========================================

 1. Top 3 Países com maior média de pontos
 2. Autor com maior engajamento total
 3. Top 10 domínios com maior engajamento
 4. Distribuição de posts por país
```

### Gráficos

Quatro gráficos são gerados automaticamente na pasta `charts/`:

| Arquivo | Conteúdo |
|---|---|
| `top_countries_avg_points.png` | Top 10 países por média de pontos por post |
| `top_domains_engagement.png` | Top 10 domínios por engajamento total (pontos + comentários) |
| `country_distribution.png` | Distribuição de posts por país (Top 15) |
| `top_authors_engagement.png` | Top 15 autores por engajamento total |

---

### Arquivos exportados

Dois arquivos são gerados na raiz do projeto assim que o scraper termina:

| Arquivo | Conteúdo |
|---|---|
| `top_10_dominios.csv` | Top 10 domínios por engajamento (pontos + comentários) |
| `distribuicao_paises.json` | Contagem de posts agrupada por país |

### MongoDB

Os dados ficam persistidos no MongoDB e podem ser consultados diretamente:

```bash
# Abre o shell do MongoDB
docker exec -it hacker_news_db mongosh

# Dentro do shell:
use hacker_news_db
db.posts.find().pretty()          # Todos os posts
db.posts.countDocuments()         # Total de posts coletados
db.posts.find({ country: "US" })  # Filtrar por país
```

---

## 🛑 Parar e limpar

```bash
# Para os containers sem apagar os dados do banco
docker compose down

# Para os containers E apaga os dados do MongoDB
docker compose down -v
```

---

## ✨ Além do requisitado

**Exportação de relatórios**
As análises não são apenas exibidas no terminal — são exportadas automaticamente para `top_10_dominios.csv` e `distribuicao_paises.json`.

**Gráficos automáticos**
Quatro gráficos de barras são gerados ao fim de cada execução via `matplotlib`, salvos em `charts/` como `.png`.

**Ambiente dockerizado**
Docker + Docker Compose sobem o MongoDB e o scraper juntos com um único comando, sem necessidade de instalar nada além do Docker.

**Cache de consultas à IANA**
Cada TLD único é consultado na IANA apenas uma vez por execução. Resultados são reutilizados em memória, evitando requisições redundantes.

**Código modularizado**
Dividido em módulos com responsabilidades claras (`database.py`, `country.py`, `scraper.py`, `analysis.py`, `charts.py`), facilitando manutenção e leitura.

---

## ✅ Boas práticas aplicadas

**Separação de responsabilidades**
Cada módulo tem um único propósito — conexão com banco, resolução de país, scraping, análise, exportação e visualização vivem em arquivos independentes.

**Sem dados duplicados**
O upsert (`update_one` com `upsert=True`) garante que rodar o scraper mais de uma vez nunca duplica posts.

**Índices no MongoDB**
Índices criados em `title` (único), `country`, `domain` e `author` — cobrindo todos os campos usados nas consultas e agregações.

**Infraestrutura reproduzível**
Docker + Docker Compose garantem que qualquer pessoa consiga rodar o projeto do zero com um único comando.

**Fallbacks resilientes**
A resolução de país tem múltiplas camadas: nome completo via pycountry, nome oficial, busca fuzzy e, como último recurso, o próprio ccTLD de 2 letras (ex: `.br` → `BR`).

---

## ⚙️ CI — Integração Contínua

O projeto conta com um pipeline de CI via **GitHub Actions** que roda automaticamente a cada push ou pull request nas branches `main` e `dev`.

**`test` — Testes automatizados com pytest**
Valida a lógica de parse e resolução de país sem depender de rede ou banco.

**`docker` — Build da imagem**
Garante que o `Dockerfile` continua funcional a cada alteração.

### Rodar os testes localmente

```bash
pip install pytest
pytest tests/ -v
```

---

## 📦 Dependências

| Pacote | Uso |
|---|---|
| `requests` | Requisições HTTP ao HN e à IANA |
| `beautifulsoup4` | Parse do HTML |
| `pymongo` | Conexão e operações no MongoDB |
| `tldextract` | Extração do domínio e TLD dos links |
| `pycountry` | Conversão de nome de país para código ISO |
| `matplotlib` | Geração dos gráficos |
| `pytest` | Testes automatizados |