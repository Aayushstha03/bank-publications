import os
import json
import csv
import requests
import time
import re

API_URL = "https://laterical.com/api/call/"
BANKS_PATH = os.path.join(os.path.dirname(__file__), "data", "websites.csv")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OBJECTS_DIR = os.path.join(OUTPUT_DIR, "search_results")
os.makedirs(OBJECTS_DIR, exist_ok=True)


def generate_queries(bank_url, info):
    if info == "spanish_only":
        return [
            {
                "topic": "publicaciones",
                "query": f"site:{bank_url} (inurl:publicaciones OR inurl:informes) OR (intitle:publicaciones OR intitle:informes)",
            },
            {
                "topic": "estadísticas",
                "query": f"site:{bank_url} (inurl:estadísticas OR inurl:boletín OR inurl:datos) OR (intitle:estadísticas OR intitle:datos OR intitle:boletín)",
            },
            {
                "topic": "política_monetaria",
                "query": f"site:{bank_url} (inurl:política OR inurl:regulaciones OR inurl:directrices) OR (intitle:política OR intitle:regulaciones)",
            },
            {
                "topic": "noticias",
                "query": f"site:{bank_url} (inurl:noticias OR inurl:discursos OR inurl:prensa) OR (intitle:noticias OR intitle:discursos OR intitle:prensa)",
            },
            {
                "topic": "investigación",
                "query": f"site:{bank_url} (inurl:investigación OR inurl:documentos-de-trabajo OR inurl:artículos) OR (intitle:investigación OR intitle:'documentos de trabajo')",
            },
            {
                "topic": "anuncios",
                "query": f"site:{bank_url} (inurl:anuncios OR inurl:actualizaciones) OR (intitle:anuncios OR intitle:actualizaciones)",
            },
            {
                "topic": "avisos",
                "query": f"site:{bank_url} (inurl:avisos OR inurl:alertas) OR (intitle:avisos OR intitle:alertas)",
            },
            {
                "topic": "comunicación",
                "query": f"site:{bank_url} (inurl:comunicación OR inurl:mensajes) OR (intitle:comunicación OR intitle:mensajes)",
            },
        ]

    elif info == "french_only":
        return [
            {
                "topic": "publications",
                "query": f"site:{bank_url} (inurl:publications OR inurl:rapports) OR (intitle:publications OR intitle:rapports)",
            },
            {
                "topic": "statistiques",
                "query": f"site:{bank_url} (inurl:statistiques OR inurl:bulletin OR inurl:données) OR (intitle:statistiques OR intitle:données OR intitle:bulletin)",
            },
            {
                "topic": "politique_monétaire",
                "query": f"site:{bank_url} (inurl:politique OR inurl:régulations OR inurl:directives) OR (intitle:politique OR intitle:régulations)",
            },
            {
                "topic": "nouvelles",
                "query": f"site:{bank_url} (inurl:nouvelles OR inurl:discours OR inurl:communiqués) OR (intitle:nouvelles OR intitle:discours OR intitle:communiqués)",
            },
            {
                "topic": "recherche",
                "query": f"site:{bank_url} (inurl:recherche OR inurl:documents-de-travail OR inurl:articles) OR (intitle:recherche OR intitle:'documents de travail')",
            },
            {
                "topic": "annonces",
                "query": f"site:{bank_url} (inurl:annonces OR inurl:mises-à-jour) OR (intitle:annonces OR intitle:mises-à-jour)",
            },
            {
                "topic": "avis",
                "query": f"site:{bank_url} (inurl:avis OR inurl:alertes) OR (intitle:avis OR intitle:alertes)",
            },
            {
                "topic": "communication",
                "query": f"site:{bank_url} (inurl:communication OR inurl:messages) OR (intitle:communication OR intitle:messages)",
            },
        ]
    else:
        return [
            {
                "topic": "publications",
                "query": f"site:{bank_url} (inurl:publications OR inurl:reports) OR (intitle:publications OR intitle:reports)",
            },
            {
                "topic": "statistics",
                "query": f"site:{bank_url} (inurl:statistics OR inurl:bulletin OR inurl:data) OR (intitle:statistics OR intitle:data OR intitle:bulletin)",
            },
            {
                "topic": "monetary_policy",
                "query": f"site:{bank_url} (inurl:policy OR inurl:regulations OR inurl:guidelines) OR (intitle:policy OR intitle:regulations)",
            },
            {
                "topic": "news",
                "query": f"site:{bank_url} (inurl:news OR inurl:speeches OR inurl:press) OR (intitle:news OR intitle:speeches OR intitle:press)",
            },
            {
                "topic": "research",
                "query": f"site:{bank_url} (inurl:research OR inurl:working-papers OR inurl:papers) OR (intitle:research OR intitle:'working papers')",
            },
            {
                "topic": "announcements",
                "query": f"site:{bank_url} (inurl:announcements OR inurl:updates) OR (intitle:announcements OR intitle:updates)",
            },
            {
                "topic": "notices",
                "query": f"site:{bank_url} (inurl:notices OR inurl:alerts) OR (intitle:notices OR intitle:alerts)",
            },
            {
                "topic": "communication",
                "query": f"site:{bank_url} (inurl:communication OR inurl:messages) OR (intitle:communication OR intitle:messages)",
            },
        ]


def search_query(query):
    payload = {"path": "search", "entity": [query]}
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        if "data" in data and data["data"]:
            first = data["data"][0]
            if isinstance(first, dict) and "error" in first:
                # print(
                #     f"Search failed for query '{query}' (API error: {first['error'].get('code', '')})"
                # )
                return data
            return data
        else:
            raise ValueError("No data in response")
    except Exception as e:
        # print(f"Search failed for query '{query}': {e}")
        return {"error": str(e)}


def main():
    # Read banks and info from banks_with_few_results.csv
    with open(BANKS_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        banks = [
            (row["Bank Name"], row["Bank URL"], row.get("info", "")) for row in reader
        ]

    # (Failed search results logic removed)

    total_banks = len(banks)
    for idx, (bank_name, bank_url, info) in enumerate(banks, 1):
        print(f"[{idx}/{total_banks}] Processing: {bank_name}")
        queries = generate_queries(bank_url, info.strip())
        bank_results = []
        for query_obj in queries:
            query_str = query_obj["query"]
            topic = query_obj["topic"]
            # print(f"  Running query: {query_str}")
            result = search_query(query_str)
            is_api_error = (
                isinstance(result, dict)
                and "data" in result
                and result["data"]
                and isinstance(result["data"][0], dict)
                and "error" in result["data"][0]
            )
            is_request_error = isinstance(result, dict) and "error" in result
            if is_api_error or is_request_error:
                time.sleep(1)
                continue
            search_result = None
            if (
                isinstance(result, dict)
                and "data" in result
                and isinstance(result["data"], list)
            ):
                search_result = result["data"]
            else:
                search_result = result
            if isinstance(search_result, list):
                for item in search_result:
                    if (
                        isinstance(item, dict)
                        and "results" in item
                        and isinstance(item["results"], dict)
                        and "web" in item["results"]
                        and isinstance(item["results"]["web"], list)
                    ):
                        item["results"]["web"] = item["results"]["web"][:5]
            bank_results.append({"topic": topic, "search_result": search_result})
            time.sleep(1)
        bank_name_clean = re.sub(r"[^\w\- ]", "", bank_name).strip().replace(" ", "_")
        out_path = os.path.join(OBJECTS_DIR, f"{bank_name_clean}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {"Bank Name": bank_name, "search_results": bank_results},
                f,
                ensure_ascii=False,
                indent=2,
            )
        # print(f"Results for {bank_name} written to {out_path}")
    print(f"All results written to {OBJECTS_DIR}")


if __name__ == "__main__":
    main()
