"""
Simulation de trafic vers l'API de prédiction, à travers Nginx.

Quatre scénarios sont joués dans l'ordre :
  1. Une requête valide            -> 200 attendu
  2. Une requête invalide          -> 422 attendu (validation Pydantic côté BentoML)
  3. Plusieurs appels successifs   -> 200 x N attendu (usage normal, sous la limite Nginx)
  4. Une rafale qui dépasse la rate limit Nginx -> 429 attendu sur une partie des requêtes

Nginx écoute en HTTPS avec un certificat auto-signé : on désactive donc la
vérification TLS (verify=False) et l'avertissement associé.

Usage:
    python script/simulation.py [--base-url https://localhost] [--burst 300] [--workers 50]
"""

import argparse
import concurrent.futures
import time
from collections import Counter

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Payload valide, repris de src/archive/predict/test_features.json
VALID_PAYLOAD = {
    "place": 10,
    "catu": 3,
    "sexe": 1,
    "secu1": 0.0,
    "year_acc": 2021,
    "victim_age": 60,
    "catv": 2,
    "obsm": 1,
    "motor": 1,
    "catr": 3,
    "circ": 2,
    "surf": 1,
    "situ": 1,
    "vma": 50,
    "jour": 7,
    "mois": 12,
    "lum": 5,
    "dep": 77,
    "com": 77317,
    "agg_": 2,
    "int": 1,
    "atm": 0,
    "col": 6,
    "lat": 48.60,
    "long": 2.89,
    "hour": 17,
    "nb_victim": 2,
    "nb_vehicules": 1,
}

# Payload invalide : champs requis manquants et type incorrect sur "place"
INVALID_PAYLOAD = {
    "place": "beaucoup",
    "catu": 3,
    "sexe": 1,
}


def print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_response(label, response=None, error=None):
    if error is not None:
        print(f"[{label}] Erreur réseau : {error}")
        return
    print(f"[{label}] status={response.status_code}")
    try:
        print(f"          body={response.json()}")
    except ValueError:
        print(f"          body={response.text[:200]}")


def scenario_valid_request(url):
    print_header("1. Requête valide")
    try:
        response = requests.post(url, json={"input_data": VALID_PAYLOAD}, verify=False, timeout=15)
        print_response("valide", response=response)
    except requests.RequestException as exc:
        print_response("valide", error=exc)


def scenario_invalid_request(url):
    print_header("2. Requête invalide (payload incomplet / mal typé)")
    try:
        response = requests.post(url, json={"input_data": INVALID_PAYLOAD}, verify=False, timeout=15)
        print_response("invalide", response=response)
    except requests.RequestException as exc:
        print_response("invalide", error=exc)


def scenario_multiple_requests(url, n=10, delay=0.1):
    print_header(f"3. {n} appels successifs à l'API (usage normal)")
    statuses = Counter()
    for i in range(n):
        try:
            response = requests.post(url, json={"input_data": VALID_PAYLOAD}, verify=False, timeout=15)
            statuses[response.status_code] += 1
            print(f"  requête {i + 1}/{n} -> {response.status_code}")
        except requests.RequestException as exc:
            statuses["error"] += 1
            print(f"  requête {i + 1}/{n} -> erreur ({exc})")
        time.sleep(delay)
    print(f"Résumé : {dict(statuses)}")


def scenario_rate_limit_burst(url, n=300, workers=50):
    print_header(f"4. Rafale de {n} requêtes ({workers} en parallèle) pour dépasser la rate limit Nginx")

    def fire_one():
        try:
            response = requests.post(url, json={"input_data": VALID_PAYLOAD}, verify=False, timeout=15)
            return response.status_code
        except requests.RequestException:
            return "error"

    statuses = Counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for status in executor.map(fire_one, range(n)):
            statuses[status] += 1

    print(f"Résumé : {dict(statuses)}")
    if statuses.get(429):
        print(f" {statuses[429]} requêtes rejetées en 429 Too Many Requests : la rate limit Nginx a bien été atteinte.")
    else:
        print(" Aucune requête en 429 : augmentez --burst ou --workers pour dépasser la limite (50r/s, burst=200).")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-url", default="https://localhost", help="URL de base de Nginx (défaut: https://localhost)")
    parser.add_argument("--burst", type=int, default=300, help="Nombre de requêtes envoyées lors du scénario 4 (défaut: 300)")
    parser.add_argument("--workers", type=int, default=50, help="Requêtes en parallèle lors du scénario 4 (défaut: 50)")
    args = parser.parse_args()

    url = args.base_url.rstrip("/") + "/predict"

    scenario_valid_request(url)
    scenario_invalid_request(url)
    scenario_multiple_requests(url)
    scenario_rate_limit_burst(url, n=args.burst, workers=args.workers)


if __name__ == "__main__":
    main()
