# Graficos gerados a partir dos dados coletados no MongoDB
# Os arquivos sao salvos na pasta /charts como .png

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from database import collection

OUTPUT_DIR = "charts"


def generate_all():
    """Gera e salva todos os graficos."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("\n Gerando graficos...")

    chart_top_countries()
    chart_top_domains()
    chart_country_distribution()
    chart_engagement_over_time()

    print(f" Graficos salvos em '{OUTPUT_DIR}/'")


# --- Grafico 1: Top paises por media de pontos ---

def chart_top_countries():
    pipeline = [
        {"$match": {"country": {"$ne": "Unknown"}}},
        {"$group": {"_id": "$country", "avg_points": {"$avg": "$points"}}},
        {"$sort": {"avg_points": -1}},
        {"$limit": 10},
    ]
    data = list(collection.aggregate(pipeline))
    if not data:
        print("  Sem dados para grafico de paises.")
        return

    labels = [d["_id"] for d in data]
    values = [round(d["avg_points"], 1) for d in data]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(labels[::-1], values[::-1], color="#f97316")
    ax.bar_label(bars, padding=4, fmt="%.1f", fontsize=9)
    ax.set_xlabel("Media de Pontos")
    ax.set_title("Top 10 Paises - Maior Media de Pontos")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.tight_layout()
    _save("top_countries_avg_points.png")


# --- Grafico 2: Top dominios por engajamento ---

def chart_top_domains():
    pipeline = [
        {"$project": {"domain": 1, "engagement": {"$add": ["$points", "$comments"]}}},
        {"$group": {"_id": "$domain", "total_engagement": {"$sum": "$engagement"}}},
        {"$sort": {"total_engagement": -1}},
        {"$limit": 10},
    ]
    data = list(collection.aggregate(pipeline))
    if not data:
        print("  Sem dados para grafico de dominios.")
        return

    labels = [d["_id"] for d in data]
    values = [d["total_engagement"] for d in data]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(labels[::-1], values[::-1], color="#3b82f6")
    ax.bar_label(bars, padding=4, fontsize=9)
    ax.set_xlabel("Engajamento Total (pontos + comentarios)")
    ax.set_title("Top 10 Dominios - Maior Engajamento")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.tight_layout()
    _save("top_domains_engagement.png")


# --- Grafico 3: Distribuicao de posts por pais (barras) ---

def chart_country_distribution():
    pipeline = [
        {"$match": {"country": {"$ne": "Unknown"}}},
        {"$group": {"_id": "$country", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15},
    ]
    data = list(collection.aggregate(pipeline))
    if not data:
        print("  Sem dados para grafico de distribuicao.")
        return

    labels = [d["_id"] for d in data]
    values = [d["count"] for d in data]
    colors = _palette(len(values))

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1])
    ax.bar_label(bars, padding=4, fontsize=9)
    ax.set_xlabel("Numero de Posts")
    ax.set_title("Distribuicao de Posts por Pais (Top 15)")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.tight_layout()
    _save("country_distribution.png")


# --- Grafico 4: Top autores por engajamento ---

def chart_engagement_over_time():
    pipeline = [
        {"$match": {"author": {"$ne": "Desconhecido"}}},
        {"$project": {"author": 1, "engagement": {"$add": ["$points", "$comments"]}}},
        {"$group": {"_id": "$author", "total_engagement": {"$sum": "$engagement"}}},
        {"$sort": {"total_engagement": -1}},
        {"$limit": 15},
    ]
    data = list(collection.aggregate(pipeline))
    if not data:
        print("  Sem dados para grafico de autores.")
        return

    labels = [d["_id"] for d in data]
    values = [d["total_engagement"] for d in data]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(labels[::-1], values[::-1], color="#8b5cf6")
    ax.bar_label(bars, padding=4, fontsize=9)
    ax.set_xlabel("Engajamento Total (pontos + comentarios)")
    ax.set_title("Top 15 Autores - Maior Engajamento")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.tight_layout()
    _save("top_authors_engagement.png")


# --- Helpers ---

def _save(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"   -> {path}")


def _palette(n):
    base = ["#f97316", "#3b82f6", "#8b5cf6", "#10b981",
            "#f59e0b", "#ef4444", "#06b6d4", "#84cc16",
            "#ec4899", "#6366f1", "#14b8a6", "#f43f5e",
            "#a855f7", "#0ea5e9", "#22c55e"]
    return (base * ((n // len(base)) + 1))[:n]