# análise dos dados coletados

import csv
import json
from database import collection


def analyze_data():
    """Roda as agregações no MongoDB e imprime os resultados."""
    print("\n" + "=" * 40)
    print("ANÁLISE DOS DADOS")
    print("=" * 40)

    _print_top_countries()
    _print_top_author()
    _print_top_domains()
    _print_country_distribution()


def export_reports():
    """Exporta relatórios para CSV e JSON."""
    print("\n💾 Exportando relatórios bônus...")
    _export_top_domains_csv()
    _export_country_distribution_json()


# --- Análises ---

def _print_top_countries():
    print("\n 1. Top 3 Países com maior média de pontos:")
    pipeline = [
        {"$match": {"country": {"$ne": "Unknown"}}},
        {"$group": {"_id": "$country", "avg_points": {"$avg": "$points"}}},
        {"$sort": {"avg_points": -1}},
        {"$limit": 3},
    ]
    for doc in collection.aggregate(pipeline):
        print(f" - {doc['_id']}: {doc['avg_points']:.2f} pontos")


def _print_top_author():
    print("\n 2. Autor com maior engajamento:")
    pipeline = [
        {"$project": {"author": 1, "engagement": {"$add": ["$points", "$comments"]}}},
        {"$group": {"_id": "$author", "total_engagement": {"$sum": "$engagement"}}},
        {"$sort": {"total_engagement": -1}},
        {"$limit": 1},
    ]
    for doc in collection.aggregate(pipeline):
        print(f" - {doc['_id']}: {doc['total_engagement']} de engajamento")


def _print_top_domains():
    print("\n 3. Top 10 domínios com maior engajamento:")
    for idx, doc in enumerate(_top_domains_pipeline(), 1):
        print(f" {idx:2d}. {doc['_id']}: {doc['total_engagement']}")


def _print_country_distribution():
    print("\n 4. Distribuição de posts por país:")
    for doc in _country_distribution_pipeline():
        print(f" - {doc['_id']}: {doc['count']} posts")


# --- Exportações ---

def _export_top_domains_csv():
    with open('top_10_dominios.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Dominio', 'Engajamento Total'])
        for doc in _top_domains_pipeline():
            writer.writerow([doc['_id'], doc['total_engagement']])
    print(" ✅ 'top_10_dominios.csv' criado!")


def _export_country_distribution_json():
    data = list(_country_distribution_pipeline())
    with open('distribuicao_paises.json', mode='w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4, default=str)
    print(" ✅ 'distribuicao_paises.json' criado!")


# --- Pipelines reutilizáveis ---

def _top_domains_pipeline():
    pipeline = [
        {"$project": {"domain": 1, "engagement": {"$add": ["$points", "$comments"]}}},
        {"$group": {"_id": "$domain", "total_engagement": {"$sum": "$engagement"}}},
        {"$sort": {"total_engagement": -1}},
        {"$limit": 10},
    ]
    return collection.aggregate(pipeline)


def _country_distribution_pipeline():
    pipeline = [
        {"$group": {"_id": "$country", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    return collection.aggregate(pipeline)
