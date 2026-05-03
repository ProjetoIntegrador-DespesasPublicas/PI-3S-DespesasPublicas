from fastapi import FastAPI
import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

app = FastAPI()

# ==============================
# CONFIGURAÇÕES
# ==============================

BASE_URL = "https://gateway.apilib.prefeitura.sp.gov.br/sf/sof/v4"
TOKEN = "74afe7f1-c239-3545-af30-b383914b0c76" 

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

MAX_WORKERS = 5  # limite de concorrência (evita travamento)


# ==============================
# DATA: ÚLTIMO MÊS FECHADO
# ==============================

def get_last_closed_month():
    today = datetime.today()

    if today.month == 1:
        return today.year - 1, 12

    return today.year, today.month - 1


# ==============================
# REQUISIÇÕES
# ==============================

def fetch_page(endpoint, params, page, list_key):
    local_params = params.copy()
    local_params["numPagina"] = page

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers=HEADERS,
        params=local_params,
        timeout=10
    )
    response.raise_for_status()

    data = response.json()
    return data.get(list_key, [])


def fetch_all_parallel(endpoint, params, list_key):
    # Primeira página (descobre total)
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers=HEADERS,
        params={**params, "numPagina": 1},
        timeout=10
    )
    response.raise_for_status()

    data = response.json()

    all_data = data.get(list_key, [])
    total_pages = data.get("metadados", {}).get("qtdPaginas", 1)

    # Paralelizar páginas restantes
    if total_pages > 1:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(fetch_page, endpoint, params, page, list_key)
                for page in range(2, total_pages + 1)
            ]

            for future in as_completed(futures):
                try:
                    all_data.extend(future.result())
                except Exception as e:
                    print(f"Erro ao buscar página: {e}")

    return all_data


# ==============================
# CACHE SIMPLES
# ==============================

@lru_cache(maxsize=20)
def get_despesas_raw(endpoint: str, ano: int, mes: int):
    if endpoint == "despesas":
        return fetch_all_parallel(
            "despesas",
            {"anoDotacao": ano, "mesDotacao": mes},
            "lstDespesas"
        )

    elif endpoint == "empenhos":
        return fetch_all_parallel(
            "empenhos",
            {"anoEmpenho": ano, "mesEmpenho": mes},
            "lstEmpenhos"
        )

    return []


# ==============================
# ENDPOINTS
# ==============================

@app.get("/")
def home():
    return {"status": "API SOF rodando com sucesso 🚀"}


# 🔹 Resumo geral
@app.get("/despesas/resumo")
def resumo_despesas():

    ano, mes = get_last_closed_month()

    raw = get_despesas_raw("despesas", ano, mes)

    df = pd.DataFrame(raw).fillna(0)

    return {
        "ano": ano,
        "mes": mes,
        "orcado": float(df.get("valOrcadoAtualizado", pd.Series()).sum()),
        "empenhado": float(df.get("valEmpenhado", pd.Series()).sum()),
        "liquidado": float(df.get("valLiquidado", pd.Series()).sum()),
        "pago": float(df.get("valPagoExercicio", pd.Series()).sum())
    }


# 🔹 Por órgão
@app.get("/despesas/por-orgao")
def despesas_por_orgao():

    ano, mes = get_last_closed_month()

    raw = get_despesas_raw("empenhos", ano, mes)

    if not raw:
        return []

    df = pd.DataFrame(raw)

    # 🔍 DEBUG (opcional - ajuda muito)
    print("Colunas disponíveis:", df.columns.tolist())

    # ✔️ valida coluna
    if "txDescricaoOrgao" not in df.columns:
        return {
            "erro": "Coluna txDescricaoOrgao não encontrada",
            "colunas_disponiveis": df.columns.tolist()
        }

    if "valTotalEmpenhado" not in df.columns:
        return {
            "erro": "Coluna valTotalEmpenhado não encontrada"
        }

    # conversão segura
    df["valTotalEmpenhado"] = pd.to_numeric(
        df["valTotalEmpenhado"], errors="coerce"
    )

    grouped = (
        df.groupby("txDescricaoOrgao")["valTotalEmpenhado"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    return grouped.to_dict(orient="records")

# 🔹 Top credores
@app.get("/despesas/top-credores")
def top_credores():

    ano, mes = get_last_closed_month()

    raw = get_despesas_raw("empenhos", ano, mes)

    df = pd.DataFrame(raw)

    if df.empty:
        return []

    df["valTotalEmpenhado"] = pd.to_numeric(
        df.get("valTotalEmpenhado", 0), errors="coerce"
    )

    top = (
        df.groupby("txtRazaoSocial")["valTotalEmpenhado"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    return top.to_dict(orient="records")


# 🔹 Evolução por programa
@app.get("/despesas/por-programa")
def despesas_por_programa():

    ano, mes = get_last_closed_month()

    raw = get_despesas_raw("empenhos", ano, mes)

    df = pd.DataFrame(raw)

    if df.empty:
        return []

    df["valTotalEmpenhado"] = pd.to_numeric(
        df.get("valTotalEmpenhado", 0), errors="coerce"
    )

    grouped = (
        df.groupby("txtDescricaoPrograma")["valTotalEmpenhado"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    return grouped.to_dict(orient="records")