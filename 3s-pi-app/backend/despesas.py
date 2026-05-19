import os, datetime, time

def clearTerminal(temp):
  time.sleep(temp)
  os.system('cls' if os.name == 'nt' else 'clear')

"""
Backend FastAPI — SOF Dashboard 2026
Prefeitura de São Paulo / Secretaria da Fazenda
"""

from fastapi import FastAPI, Query, HTTPException

"""
Backend FastAPI — SOF Dashboard 2026
Prefeitura de São Paulo / Secretaria da Fazenda
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Any
import logging
from pathlib import Path

# ==============================
# CONFIGURAÇÕES
# ==============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SOF Dashboard 2026",
    description="Dashboard orçamentário — Prefeitura de São Paulo",
    version="3.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

SOF_BASE    = "https://gateway.apilib.prefeitura.sp.gov.br/sf/sof/v4"
SOF_TOKEN   = "74afe7f1-c239-3545-af30-b383914b0c76"
SOF_HEADERS = {
    "Authorization": f"Bearer {SOF_TOKEN}",
    "accept": "application/json",
}

ANO_FIXO         = 2026
CONCURRENCY      = 8
CONCURRENCY_ORGS = 6
CACHE_TTL        = 3600
TOP_N_CREDORES   = 10
TOP_N_PROGRAMAS  = 10
MIN_ROWS_CACHE   = 4   # mínimo de linhas por tabela para considerar cache válido

# ==============================
# CONFIGURAÇÃO DO SQLITE
# ==============================

DB_DIR  = Path(__file__).parent
DB_PATH = DB_DIR / "dashboard.db"


def get_db_connection() -> sqlite3.Connection:
    """Retorna uma conexão com o banco SQLite."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Cria as tabelas do banco caso não existam."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS tabela_resumo (
                ano       INTEGER NOT NULL,
                mes       INTEGER NOT NULL,
                orcado    REAL    DEFAULT 0,
                liquidado REAL    DEFAULT 0,
                pago      REAL    DEFAULT 0,
                PRIMARY KEY (ano, mes)
            );

            CREATE TABLE IF NOT EXISTS tabela_orgaos (
                ano   INTEGER NOT NULL,
                mes   INTEGER NOT NULL,
                orgao TEXT    NOT NULL,
                valor REAL    DEFAULT 0,
                PRIMARY KEY (ano, mes, orgao)
            );

            CREATE TABLE IF NOT EXISTS tabela_credores (
                ano    INTEGER NOT NULL,
                mes    INTEGER NOT NULL,
                credor TEXT    NOT NULL,
                valor  REAL    DEFAULT 0,
                PRIMARY KEY (ano, mes, credor)
            );

            CREATE TABLE IF NOT EXISTS tabela_programas (
                ano      INTEGER NOT NULL,
                mes      INTEGER NOT NULL,
                programa TEXT    NOT NULL,
                valor    REAL    DEFAULT 0,
                PRIMARY KEY (ano, mes, programa)
            );
        """)
        conn.commit()
        logger.info(f"[SQLite] Banco inicializado em: {DB_PATH}")
    except sqlite3.Error as e:
        logger.error(f"[SQLite] Erro ao inicializar banco: {e}")
        raise
    finally:
        conn.close()


# ==============================
# FUNÇÕES DE LEITURA DO SQLITE
# ==============================

def sqlite_has_data(ano: int, mes: int) -> bool:
    """
    Validação de qualidade: verifica se TODAS as 4 tabelas possuem
    linhas suficientes para o ano/mês informado.
    - tabela_resumo:    mínimo 1 linha  (é um registro agregado)
    - tabela_orgaos:    mínimo MIN_ROWS_CACHE linhas
    - tabela_credores:  mínimo MIN_ROWS_CACHE linhas
    - tabela_programas: mínimo MIN_ROWS_CACHE linhas
    Se qualquer tabela estiver vazia ou insuficiente, retorna False
    e força nova busca na API da SOF.
    """
    verificacoes = [
        ("tabela_resumo",    1),
        ("tabela_orgaos",    MIN_ROWS_CACHE),
        ("tabela_credores",  MIN_ROWS_CACHE),
        ("tabela_programas", MIN_ROWS_CACHE),
    ]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for tabela, minimo in verificacoes:
            cursor.execute(
                f"SELECT COUNT(*) FROM {tabela} WHERE ano = ? AND mes = ?",
                (ano, mes)
            )
            count = cursor.fetchone()[0]
            if count < minimo:
                conn.close()
                logger.warning(
                    f"[SQLite] Qualidade insuficiente — '{tabela}': "
                    f"{count} linha(s) (mínimo: {minimo}) para {ano}/{mes:02d}. "
                    f"Forçando busca na API da SOF."
                )
                return False
        conn.close()
        logger.info(f"[SQLite] Cache válido para {ano}/{mes:02d} — todas as tabelas OK.")
        return True
    except sqlite3.Error as e:
        logger.warning(f"[SQLite] Erro ao validar qualidade do cache: {e}")
        return False


def sqlite_load_resumo(ano: int, mes: int) -> dict | None:
    """Lê o resumo financeiro do SQLite."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ano, mes, orcado, liquidado, pago FROM tabela_resumo WHERE ano = ? AND mes = ?",
            (ano, mes)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None
    except sqlite3.Error as e:
        logger.error(f"[SQLite] Erro ao ler tabela_resumo: {e}")
        return None


def sqlite_load_orgaos(ano: int, mes: int) -> list[dict]:
    """Lê os dados por órgão do SQLite."""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(
            "SELECT orgao, valor FROM tabela_orgaos WHERE ano = ? AND mes = ? ORDER BY valor DESC",
            conn, params=(ano, mes)
        )
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"[SQLite] Erro ao ler tabela_orgaos: {e}")
        return []


def sqlite_load_credores(ano: int, mes: int) -> list[dict]:
    """Lê os top credores do SQLite."""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(
            "SELECT credor, valor FROM tabela_credores WHERE ano = ? AND mes = ? ORDER BY valor DESC",
            conn, params=(ano, mes)
        )
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"[SQLite] Erro ao ler tabela_credores: {e}")
        return []


def sqlite_load_programas(ano: int, mes: int) -> list[dict]:
    """Lê os dados por programa do SQLite."""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(
            "SELECT programa, valor FROM tabela_programas WHERE ano = ? AND mes = ? ORDER BY valor DESC",
            conn, params=(ano, mes)
        )
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"[SQLite] Erro ao ler tabela_programas: {e}")
        return []


# ==============================
# FUNÇÕES DE GRAVAÇÃO NO SQLITE
# ==============================

def sqlite_save_resumo(ano: int, mes: int, resumo: dict) -> None:
    """Salva o resumo financeiro no SQLite usando transação atômica."""
    try:
        df = pd.DataFrame([{
            "ano":       ano,
            "mes":       mes,
            "orcado":    float(resumo.get("orcado")    or 0),
            "liquidado": float(resumo.get("liquidado") or 0),
            "pago":      float(resumo.get("pago")      or 0),
        }])
        conn = get_db_connection()
        with conn:   # transação atômica: DELETE + INSERT
            conn.execute(
                "DELETE FROM tabela_resumo WHERE ano = ? AND mes = ?",
                (ano, mes)
            )
            df.to_sql("tabela_resumo", conn, if_exists="append", index=False)
        conn.close()
        logger.info(f"[SQLite] Resumo salvo para {ano}/{mes:02d}.")
    except Exception as e:
        logger.error(f"[SQLite] Erro ao salvar tabela_resumo: {e}")


def sqlite_save_orgaos(ano: int, mes: int, orgaos: list[dict]) -> None:
    """
    Salva os dados por órgão no SQLite.
    - Filtra entradas com nome vazio/None ou valor zero (evita violação de PK).
    - Usa transação única: DELETE + INSERT atomicamente.
    - Deduplica por nome de órgão antes de inserir.
    """
    if not orgaos:
        logger.warning(f"[SQLite] Nenhum órgão para salvar em {ano}/{mes:02d}.")
        return
    try:
        # Sanitiza e deduplica
        rows = {}
        for o in orgaos:
            nome  = str(o.get("orgao") or "").strip()
            valor = float(o.get("valor") or 0)
            if not nome or valor <= 0:
                continue
            # mantém o maior valor em caso de nome duplicado
            if nome not in rows or valor > rows[nome]:
                rows[nome] = valor

        if not rows:
            logger.warning(f"[SQLite] Todos os órgãos foram filtrados (nomes vazios/valor=0) para {ano}/{mes:02d}.")
            return

        df = pd.DataFrame([
            {"ano": ano, "mes": mes, "orgao": nome, "valor": valor}
            for nome, valor in rows.items()
        ])

        conn = get_db_connection()
        with conn:   # transação: commit automático ou rollback em erro
            conn.execute(
                "DELETE FROM tabela_orgaos WHERE ano = ? AND mes = ?",
                (ano, mes)
            )
            df.to_sql("tabela_orgaos", conn, if_exists="append", index=False)
        conn.close()
        logger.info(f"[SQLite] {len(rows)} órgãos salvos para {ano}/{mes:02d}.")
    except Exception as e:
        logger.error(f"[SQLite] Erro ao salvar tabela_orgaos: {e}")


def sqlite_save_credores(ano: int, mes: int, credores: list[dict]) -> None:
    """
    Salva os top credores no SQLite.
    - Filtra entradas com nome vazio/None ou valor zero (evita violação de PK).
    - Usa transação única: DELETE + INSERT atomicamente.
    - Deduplica por nome de credor antes de inserir.
    """
    if not credores:
        logger.warning(f"[SQLite] Nenhum credor para salvar em {ano}/{mes:02d}.")
        return
    try:
        # Sanitiza e deduplica
        rows = {}
        for c in credores:
            nome  = str(c.get("credor") or "").strip()
            valor = float(c.get("valor") or 0)
            if not nome or valor <= 0:
                continue
            if nome not in rows or valor > rows[nome]:
                rows[nome] = valor

        if not rows:
            logger.warning(f"[SQLite] Todos os credores foram filtrados (nomes vazios/valor=0) para {ano}/{mes:02d}.")
            return

        df = pd.DataFrame([
            {"ano": ano, "mes": mes, "credor": nome, "valor": valor}
            for nome, valor in rows.items()
        ])

        conn = get_db_connection()
        with conn:   # transação atômica
            conn.execute(
                "DELETE FROM tabela_credores WHERE ano = ? AND mes = ?",
                (ano, mes)
            )
            df.to_sql("tabela_credores", conn, if_exists="append", index=False)
        conn.close()
        logger.info(f"[SQLite] {len(rows)} credores salvos para {ano}/{mes:02d}.")
    except Exception as e:
        logger.error(f"[SQLite] Erro ao salvar tabela_credores: {e}")


def sqlite_save_programas(ano: int, mes: int, programas: list[dict]) -> None:
    """
    Salva os dados por programa no SQLite.
    - Filtra entradas com nome vazio/None ou valor zero.
    - Usa transação atômica: DELETE + INSERT.
    - Deduplica por nome de programa antes de inserir.
    """
    if not programas:
        logger.warning(f"[SQLite] Nenhum programa para salvar em {ano}/{mes:02d}.")
        return
    try:
        rows = {}
        for p in programas:
            nome  = str(p.get("programa") or "").strip()
            valor = float(p.get("valor") or 0)
            if not nome or valor <= 0:
                continue
            if nome not in rows or valor > rows[nome]:
                rows[nome] = valor

        if not rows:
            logger.warning(f"[SQLite] Todos os programas foram filtrados para {ano}/{mes:02d}.")
            return

        df = pd.DataFrame([
            {"ano": ano, "mes": mes, "programa": nome, "valor": valor}
            for nome, valor in rows.items()
        ])

        conn = get_db_connection()
        with conn:
            conn.execute(
                "DELETE FROM tabela_programas WHERE ano = ? AND mes = ?",
                (ano, mes)
            )
            df.to_sql("tabela_programas", conn, if_exists="append", index=False)
        conn.close()
        logger.info(f"[SQLite] {len(rows)} programas salvos para {ano}/{mes:02d}.")
    except Exception as e:
        logger.error(f"[SQLite] Erro ao salvar tabela_programas: {e}")


# ==============================
# CACHE ASSÍNCRONO COM TTL
# ==============================

class AsyncTTLCache:
    def __init__(self, ttl: int = CACHE_TTL, maxsize: int = 256):
        self._store:  dict[str, tuple[Any, float]] = {}
        self._ttl     = ttl
        self._maxsize = maxsize
        self._lock    = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            value, exp = entry
            if datetime.now().timestamp() > exp:
                del self._store[key]
                return None
            return value

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            if len(self._store) >= self._maxsize:
                oldest = min(self._store, key=lambda k: self._store[k][1])
                del self._store[oldest]
            self._store[key] = (value, datetime.now().timestamp() + self._ttl)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    async def stats(self) -> dict:
        async with self._lock:
            now   = datetime.now().timestamp()
            valid = sum(1 for _, exp in self._store.values() if exp > now)
            return {"total": len(self._store), "validas": valid}


cache = AsyncTTLCache()


# ==============================
# LÓGICA DE DATAS
# ==============================

def get_mes_disponivel() -> int:
    hoje = datetime.today()
    if hoje.year < ANO_FIXO:
        return 1
    if hoje.year > ANO_FIXO:
        return 12
    return max(1, hoje.month - 1)


def get_meses_disponiveis() -> list[dict]:
    nomes = [
        "Janeiro","Fevereiro","Março","Abril",
        "Maio","Junho","Julho","Agosto",
        "Setembro","Outubro","Novembro","Dezembro",
    ]
    return [{"valor": m, "nome": nomes[m-1]} for m in range(1, get_mes_disponivel() + 1)]


def validar_mes(mes: int) -> int:
    max_mes = get_mes_disponivel()
    if mes < 1 or mes > max_mes:
        raise HTTPException(
            status_code=400,
            detail=f"Mês {mes} indisponível. Máximo com dados em 2026: {max_mes}."
        )
    return mes


# ==============================
# CLIENTE HTTP
# ==============================

_http_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            headers=SOF_HEADERS,
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        )
    return _http_client


@app.on_event("startup")
async def startup():
    get_client()
    init_db()
    logger.info("HTTP client iniciado.")
    logger.info(f"[SQLite] Banco de dados em: {DB_PATH}")


@app.on_event("shutdown")
async def shutdown():
    if _http_client and not _http_client.is_closed:
        await _http_client.aclose()
    logger.info("HTTP client encerrado.")


# ==============================
# PAGINAÇÃO PARALELA
# ==============================

async def _fetch_page(
    endpoint: str,
    params:   dict,
    page:     int,
    list_key: str,
    sem:      asyncio.Semaphore,
) -> list:
    async with sem:
        try:
            resp = await get_client().get(
                f"{SOF_BASE}/{endpoint}",
                params={**params, "numPagina": page},
            )
            resp.raise_for_status()
            return resp.json().get(list_key, [])
        except Exception as exc:
            logger.warning(f"[SOF] {endpoint} pág {page} falhou: {exc}")
            return []


async def fetch_all_pages(
    endpoint:  str,
    params:    dict,
    list_key:  str,
    max_pages: int = 20,
) -> list:
    try:
        resp = await get_client().get(
            f"{SOF_BASE}/{endpoint}",
            params={**params, "numPagina": 1},
        )
        resp.raise_for_status()
        body = resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"SOF API erro {exc.response.status_code} em /{endpoint}"
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=504, detail=f"Timeout SOF API: {exc}")

    meta        = body.get("metadados", {})
    total_pages = min(meta.get("qtdPaginas", 1), max_pages)
    records     = body.get(list_key, [])

    if meta.get("txtStatus") == "SEM_REGISTROS" or total_pages <= 1:
        return records

    sem   = asyncio.Semaphore(CONCURRENCY)
    pages = await asyncio.gather(*[
        _fetch_page(endpoint, params, p, list_key, sem)
        for p in range(2, total_pages + 1)
    ])
    for pg in pages:
        records.extend(pg)

    logger.info(f"[SOF] /{endpoint} → {len(records)} registros ({total_pages} págs)")
    return records


# ==============================
# CACHE + FETCH
# ==============================

async def get_cached(
    endpoint:  str,
    params:    dict,
    list_key:  str,
    max_pages: int = 20,
) -> list:
    key = f"{endpoint}:{sorted(params.items())}"
    hit = await cache.get(key)
    if hit is not None:
        logger.info(f"[HIT]  {key}")
        return hit
    logger.info(f"[MISS] {key}")
    result = await fetch_all_pages(endpoint, params, list_key, max_pages)
    await cache.set(key, result)
    return result


# ==============================
# HELPERS PANDAS
# ==============================

def to_df(raw: list) -> pd.DataFrame:
    return pd.DataFrame(raw).fillna(0) if raw else pd.DataFrame()


def safe_sum(df: pd.DataFrame, col: str) -> float:
    if col not in df.columns:
        return 0.0
    return float(pd.to_numeric(df[col], errors="coerce").fillna(0).sum())


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


# ==============================
# POR ÓRGÃO
# ==============================

async def get_despesas_por_orgao(ano: int, mes: int) -> list[dict]:
    """
    1. Busca catálogo de órgãos (/orgaos)
    2. Para cada órgão faz /despesas?codOrgao=X e soma valEmpenhado
    3. Retorna lista ordenada por valor
    """
    orgaos = await get_cached("orgaos", {"anoExercicio": ano}, "lstOrgaos", max_pages=5)
    if not orgaos:
        logger.warning("[ORGAOS] Lista vazia.")
        return []

    logger.info(f"[ORGAOS] Consultando {len(orgaos)} órgãos para {ano}/{mes}")

    sem = asyncio.Semaphore(CONCURRENCY_ORGS)

    async def fetch_orgao(orgao: dict) -> dict | None:
        cod  = orgao.get("codOrgao")
        nome = orgao.get("txtDescricaoOrgao", str(cod))
        if not cod:
            return None
        async with sem:
            try:
                resp = await get_client().get(
                    f"{SOF_BASE}/despesas",
                    params={
                        "anoDotacao": ano,
                        "mesDotacao": mes,
                        "codOrgao":   cod,
                        "numPagina":  1,
                    },
                )
                resp.raise_for_status()
                records = resp.json().get("lstDespesas", [])
                if not records:
                    return None
                df  = pd.DataFrame(records)
                val = safe_sum(df, "valTotalEmpenhado")
                if val <= 0:
                    return None
                return {
                    "orgao":    nome,
                    "codOrgao": cod,
                    "valor":    round(val, 2),
                }
            except Exception as exc:
                logger.warning(f"[ORGAO {cod}] {exc}")
                return None

    results = await asyncio.gather(*[fetch_orgao(o) for o in orgaos])
    valid   = [r for r in results if r is not None]
    valid.sort(key=lambda x: x["valor"], reverse=True)

    logger.info(f"[ORGAOS] {len(valid)} órgãos com valor > 0")
    return valid


# ==============================
# POR PROGRAMA
# ==============================

async def get_despesas_por_programa(ano: int, mes: int) -> list[dict]:
    """
    1. Busca catálogo de programas (/programas)
    2. Para cada programa faz /despesas?codPrograma=X e soma valEmpenhado
    3. Retorna top N ordenados por valor
    """
    programas = await get_cached(
        "programas", {"anoExercicio": ano}, "lstProgramas", max_pages=3
    )
    if not programas:
        logger.warning("[PROGRAMAS] Lista vazia.")
        return []

    logger.info(f"[PROGRAMAS] Consultando {len(programas)} programas para {ano}/{mes}")

    sem = asyncio.Semaphore(CONCURRENCY_ORGS)

    async def fetch_programa(prog: dict) -> dict | None:
        cod  = prog.get("codPrograma")
        nome = prog.get("txtDescricaoPrograma", str(cod))
        if not cod:
            return None
        async with sem:
            try:
                resp = await get_client().get(
                    f"{SOF_BASE}/despesas",
                    params={
                        "anoDotacao":  ano,
                        "mesDotacao":  mes,
                        "codPrograma": cod,
                        "numPagina":   1,
                    },
                )
                resp.raise_for_status()
                records = resp.json().get("lstDespesas", [])
                if not records:
                    return None
                df  = pd.DataFrame(records)
                val = safe_sum(df, "valTotalEmpenhado")
                if val <= 0:
                    return None
                return {
                    "programa":    nome,
                    "codPrograma": cod,
                    "valor":       round(val, 2),
                }
            except Exception as exc:
                logger.warning(f"[PROGRAMA {cod}] {exc}")
                return None

    results = await asyncio.gather(*[fetch_programa(p) for p in programas])
    valid   = [r for r in results if r is not None]
    valid.sort(key=lambda x: x["valor"], reverse=True)

    logger.info(f"[PROGRAMAS] {len(valid)} programas com valor > 0")
    return valid[:TOP_N_PROGRAMAS]


# ==============================
# TOP CREDORES
# ==============================

async def get_top_credores(ano: int, mes: int) -> list[dict]:
    """
    /despesasCredor retorna lstDespesaCredores (atenção: não lstCredores).
    Ordena por valTotalEmpenhado e devolve os top N.
    """
    raw = await get_cached(
        "despesasCredor",
        {"anoExercicio": ano, "mesEmpenho": mes},
        "lstDespesaCredores",
        max_pages=10,
    )
    if not raw:
        return []

    df = to_df(raw)
    logger.info(f"[CREDORES] {len(df)} registros — colunas: {df.columns.tolist()}")

    required = {"txtRazaoSocial", "valTotalEmpenhado", "numCpfCnpj"}
    if not required.issubset(df.columns):
        logger.warning(f"[CREDORES] Colunas ausentes. Disponíveis: {df.columns.tolist()}")
        return []

    df["valTotalEmpenhado"] = safe_numeric(df["valTotalEmpenhado"])

    result = (
        df[["numCpfCnpj", "txtRazaoSocial", "valTotalEmpenhado"]]
        .sort_values("valTotalEmpenhado", ascending=False)
        .head(TOP_N_CREDORES)
        .rename(columns={
            "numCpfCnpj":        "codCredor",
            "txtRazaoSocial":    "credor",
            "valTotalEmpenhado": "valor",
        })
    )
    result["valor"] = result["valor"].round(2)

    logger.info(f"[CREDORES] {len(result)} credores retornados")
    return result.to_dict(orient="records")


# ==============================
# DASHBOARD COM CACHE SQLITE
# ==============================

async def build_dashboard_from_api(ano: int, mes: int) -> dict:
    """
    Consome a API da SOF, processa os dados e persiste no SQLite.
    Retorna o payload completo do dashboard.
    """
    logger.info(f"[FONTE: API SOF] Buscando dados para {ano}/{mes:02d} ...")

    resumo_fut   = get_cached("despesas",
                              {"anoDotacao": ano, "mesDotacao": mes},
                              "lstDespesas", max_pages=5)
    orgao_fut    = get_despesas_por_orgao(ano, mes)
    credores_fut = get_top_credores(ano, mes)
    programa_fut = get_despesas_por_programa(ano, mes)

    resumo_raw, por_orgao, top_credores, por_programa = await asyncio.gather(
        resumo_fut, orgao_fut, credores_fut, programa_fut,
        return_exceptions=True,
    )

    def safe(val, default):
        if isinstance(val, Exception):
            logger.error(f"Erro na tarefa paralela: {val}")
            return default
        return val

    resumo_raw   = safe(resumo_raw,   [])
    por_orgao    = safe(por_orgao,    [])
    top_credores = safe(top_credores, [])
    por_programa = safe(por_programa, [])

    df_dot = to_df(resumo_raw)

    resumo = {
        "ano":       ano,
        "mes":       mes,
        "orcado":    safe_sum(df_dot, "valOrcadoAtualizado"),
        "empenhado": safe_sum(df_dot, "valEmpenhado"),
        "liquidado": safe_sum(df_dot, "valLiquidado"),
        "pago":      safe_sum(df_dot, "valPagoExercicio"),
    }

    # Persiste no SQLite — log de diagnóstico antes de salvar
    logger.info(
        f"[SQLite] Salvando → resumo: 1 reg | órgãos: {len(por_orgao)} | "
        f"credores: {len(top_credores)} | programas: {len(por_programa)}"
    )
    try:
        sqlite_save_resumo(ano, mes, resumo)
        sqlite_save_orgaos(ano, mes, por_orgao)
        sqlite_save_credores(ano, mes, top_credores)
        sqlite_save_programas(ano, mes, por_programa)
        logger.info(f"[SQLite] Dados de {ano}/{mes:02d} persistidos com sucesso.")
    except Exception as e:
        logger.error(f"[SQLite] Falha ao persistir dados: {e}")

    return {
        "meta": {
            "ano":                  ano,
            "mes":                  mes,
            "fonte":                "api",
            "registros_dotacoes":   len(resumo_raw),
            "orgaos_retornados":    len(por_orgao),
            "credores_retornados":  len(top_credores),
            "programas_retornados": len(por_programa),
        },
        "resumo":      resumo,
        "porOrgao":    por_orgao,
        "topCredores": top_credores,
        "topProgramas": por_programa,
    }


def build_dashboard_from_sqlite(ano: int, mes: int) -> dict:
    """
    Monta o payload do dashboard lendo exclusivamente do SQLite.
    """
    logger.info(f"[FONTE: SQLite] Carregando dados para {ano}/{mes:02d} ...")

    resumo_row   = sqlite_load_resumo(ano, mes)
    por_orgao    = sqlite_load_orgaos(ano, mes)
    top_credores = sqlite_load_credores(ano, mes)
    por_programa = sqlite_load_programas(ano, mes)

    resumo = resumo_row if resumo_row else {
        "ano": ano, "mes": mes, "orcado": 0, "liquidado": 0, "pago": 0
    }

    return {
        "meta": {
            "ano":                  ano,
            "mes":                  mes,
            "fonte":                "sqlite",
            "registros_dotacoes":   None,
            "orgaos_retornados":    len(por_orgao),
            "credores_retornados":  len(top_credores),
            "programas_retornados": len(por_programa),
        },
        "resumo":      resumo,
        "porOrgao":    por_orgao,
        "topCredores": top_credores,
        "topProgramas": por_programa,
    }


# ==============================
# ENDPOINTS
# ==============================

@app.get("/", tags=["Status"])
async def home():
    return {
        "status":         "ok",
        "versao":         "3.3.0",
        "ano":            ANO_FIXO,
        "mes_disponivel": get_mes_disponivel(),
    }


@app.get("/meses-disponiveis", tags=["Filtro"])
async def meses_disponiveis():
    return {
        "ano":        ANO_FIXO,
        "mes_padrao": get_mes_disponivel(),
        "meses":      get_meses_disponiveis(),
    }


@app.get("/cache/stats", tags=["Admin"])
async def cache_stats():
    return await cache.stats()


@app.get("/cache/clear", tags=["Admin"])
async def limpar_cache():
    await cache.clear()
    return {"message": "Cache em memória limpo."}


@app.get("/cache/sqlite/clear", tags=["Admin"])
async def limpar_cache_sqlite(
    mes: int = Query(default=None, ge=1, le=12,
                     description="Mês a remover do SQLite (omita para limpar tudo)")
):
    """Remove registros do SQLite para forçar nova consulta à API."""
    try:
        conn = get_db_connection()
        tabelas = ("tabela_resumo", "tabela_orgaos", "tabela_credores", "tabela_programas")
        with conn:
            if mes:
                for tabela in tabelas:
                    conn.execute(f"DELETE FROM {tabela} WHERE ano = ? AND mes = ?", (ANO_FIXO, mes))
                msg = f"Cache SQLite limpo para {ANO_FIXO}/{mes:02d}."
            else:
                for tabela in tabelas:
                    conn.execute(f"DELETE FROM {tabela}")
                msg = "Cache SQLite completamente limpo."
        conn.close()
        logger.info(f"[SQLite] {msg}")
        return {"message": msg}
    except sqlite3.Error as e:
        logger.error(f"[SQLite] Erro ao limpar cache: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao limpar SQLite: {e}")


@app.get("/cache/sqlite/status", tags=["Admin"])
async def status_cache_sqlite():
    """
    Diagnóstico do banco SQLite: exibe quantas linhas existem
    em cada tabela para cada mês disponível.
    Também informa se o cache de cada mês é válido (≥ MIN_ROWS_CACHE linhas).
    """
    tabelas = ("tabela_resumo", "tabela_orgaos", "tabela_credores", "tabela_programas")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        resultado = {}
        for mes in range(1, get_mes_disponivel() + 1):
            info = {"valido": True, "tabelas": {}}
            for tabela in tabelas:
                cursor.execute(
                    f"SELECT COUNT(*) FROM {tabela} WHERE ano = ? AND mes = ?",
                    (ANO_FIXO, mes)
                )
                count = cursor.fetchone()[0]
                minimo = 1 if tabela == "tabela_resumo" else MIN_ROWS_CACHE
                ok = count >= minimo
                info["tabelas"][tabela] = {"linhas": count, "minimo": minimo, "ok": ok}
                if not ok:
                    info["valido"] = False
            resultado[f"{ANO_FIXO}/{mes:02d}"] = info
        conn.close()
        return {
            "banco":      str(DB_PATH),
            "min_linhas": MIN_ROWS_CACHE,
            "meses":      resultado,
        }
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar SQLite: {e}")


# ──────────────────────────────────────────────────
# DASHBOARD UNIFICADO (com cache SQLite)
# ──────────────────────────────────────────────────

@app.get("/despesas/dashboard", tags=["Dashboard"])
async def get_dashboard(
    mes: int = Query(
        default=None, ge=1, le=12,
        description="Mês de 2026 (padrão: último mês fechado)"
    )
):
    if mes is None:
        mes = get_mes_disponivel()
    else:
        mes = validar_mes(mes)

    ano = ANO_FIXO
    logger.info(f"[DASHBOARD] {ano}/{mes:02d}")

    # Verifica se o SQLite já tem dados para este mês
    if sqlite_has_data(ano, mes):
        return build_dashboard_from_sqlite(ano, mes)

    # Primeira requisição: busca na API e persiste no SQLite
    return await build_dashboard_from_api(ano, mes)


# ──────────────────────────────────────────────────
# ENDPOINTS INDIVIDUAIS (com cache SQLite)
# ──────────────────────────────────────────────────

@app.get("/despesas/resumo", tags=["Despesas"])
async def resumo_despesas(mes: int = Query(default=None, ge=1, le=12)):
    if mes is None:
        mes = get_mes_disponivel()
    else:
        mes = validar_mes(mes)

    ano = ANO_FIXO

    # Tenta SQLite primeiro
    if sqlite_has_data(ano, mes):
        logger.info(f"[FONTE: SQLite] Resumo para {ano}/{mes:02d}")
        row = sqlite_load_resumo(ano, mes)
        if row:
            return row

    # Fallback: API
    logger.info(f"[FONTE: API SOF] Resumo para {ano}/{mes:02d}")
    raw = await get_cached("despesas",
                           {"anoDotacao": ano, "mesDotacao": mes},
                           "lstDespesas", max_pages=5)
    df = to_df(raw)
    resumo = {
        "ano":       ano,
        "mes":       mes,
        "orcado":    safe_sum(df, "valOrcadoAtualizado"),
        "empenhado": safe_sum(df, "valEmpenhado"),
        "liquidado": safe_sum(df, "valLiquidado"),
        "pago":      safe_sum(df, "valPagoExercicio"),
    }
    sqlite_save_resumo(ano, mes, resumo)
    return resumo


@app.get("/despesas/por-orgao", tags=["Despesas"])
async def despesas_por_orgao(mes: int = Query(default=None, ge=1, le=12)):
    if mes is None:
        mes = get_mes_disponivel()
    else:
        mes = validar_mes(mes)

    ano = ANO_FIXO

    if sqlite_has_data(ano, mes):
        logger.info(f"[FONTE: SQLite] Órgãos para {ano}/{mes:02d}")
        return sqlite_load_orgaos(ano, mes)

    logger.info(f"[FONTE: API SOF] Órgãos para {ano}/{mes:02d}")
    result = await get_despesas_por_orgao(ano, mes)
    sqlite_save_orgaos(ano, mes, result)
    return result


@app.get("/despesas/top-credores", tags=["Despesas"])
async def top_credores_endpoint(mes: int = Query(default=None, ge=1, le=12)):
    if mes is None:
        mes = get_mes_disponivel()
    else:
        mes = validar_mes(mes)

    ano = ANO_FIXO

    if sqlite_has_data(ano, mes):
        logger.info(f"[FONTE: SQLite] Credores para {ano}/{mes:02d}")
        return sqlite_load_credores(ano, mes)

    logger.info(f"[FONTE: API SOF] Credores para {ano}/{mes:02d}")
    result = await get_top_credores(ano, mes)
    sqlite_save_credores(ano, mes, result)
    return result


@app.get("/despesas/por-programa", tags=["Despesas"])
async def despesas_por_programa(mes: int = Query(default=None, ge=1, le=12)):
    if mes is None:
        mes = get_mes_disponivel()
    else:
        mes = validar_mes(mes)

    ano = ANO_FIXO

    if sqlite_has_data(ano, mes):
        logger.info(f"[FONTE: SQLite] Programas para {ano}/{mes:02d}")
        return sqlite_load_programas(ano, mes)

    logger.info(f"[FONTE: API SOF] Programas para {ano}/{mes:02d}")
    result = await get_despesas_por_programa(ano, mes)
    sqlite_save_programas(ano, mes, result)
    return result