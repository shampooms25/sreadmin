import ipaddress
import logging
import os
import socket
from typing import Iterable, Optional, Tuple

import psycopg2
import requests


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BASE_URL = "http://172.25.4.1:8080"
USERNAME = "root"
PASSWORD = "Popp@Eld2025!"

DB_CONFIG = {
    "host": "172.18.25.253",
    "port": 5432,
    "dbname": "radius",
    "user": "radius",
    "password": "radius@srv02",
}

APPLIANCE_NAME = os.getenv("ADGUARD_APPLIANCE_NAME") or socket.gethostname()


def _login_session() -> requests.Session:
    session = requests.Session()
    response = session.post(
        f"{BASE_URL}/control/login",
        json={"name": USERNAME, "password": PASSWORD},
        timeout=10,
    )
    response.raise_for_status()

    try:
        payload = response.json()
        login_ok = payload.get("ok", False)
    except ValueError:
        login_ok = response.text.strip().upper() == "OK"

    if not login_ok:
        raise RuntimeError("Falha ao autenticar no AdGuard Home")

    return session


def _parse_domain_entry(entry) -> Optional[Tuple[str, int]]:
    if isinstance(entry, dict):
        domain = entry.get("domain") or entry.get("name")
        count = entry.get("count") or entry.get("requests")
        if domain is None and len(entry) == 1:
            domain, count = next(iter(entry.items()))
        
        if domain is None:
            return None
        return str(domain).strip(), int(count) if count else 0

    if isinstance(entry, Iterable) and not isinstance(entry, (str, bytes)):
        entry = list(entry)
        if len(entry) >= 2:
            return str(entry[0]).strip(), int(entry[1]) if entry[1] else 0

    if isinstance(entry, str):
        return entry.strip(), 1

    return None


def _normalize_domain(raw_domain: str) -> str:
    domain = raw_domain.strip().lower().rstrip('.')
    try:
        ipaddress.ip_address(domain)
    except ValueError:
        return domain

    try:
        resolved = socket.gethostbyaddr(domain)[0]
        return resolved.lower().rstrip('.')
    except (socket.herror, socket.gaierror):
        return domain


def _upsert_domain(cursor, appliance: str, domain: str, count: int, condition: str) -> None:
    cursor.execute(
        """
        INSERT INTO public.relatorio_dominios (appliance, dominio, qtd_requisicoes, condicao, data_atualizacao)
        VALUES (%s, %s, %s, %s, CURRENT_DATE)
        ON CONFLICT (appliance, dominio, condicao)
        DO UPDATE SET
            qtd_requisicoes = EXCLUDED.qtd_requisicoes,
            data_atualizacao = EXCLUDED.data_atualizacao;
        """,
        (appliance, domain, count, condition),
    )


def main() -> None:
    try:
        session = _login_session()
    except Exception as exc:
        logger.error("Não foi possível autenticar no AdGuard Home: %s", exc)
        raise

    try:
        response = session.get(f"{BASE_URL}/control/stats", timeout=10)
        response.raise_for_status()
        stats = response.json()
    finally:
        session.close()

    top_queried = stats.get("top_queried_domains", [])[:20]
    top_blocked = stats.get("top_blocked_domains", [])[:20]
    logger.info("Itens retornados - consultas: %d, bloqueios: %d", len(top_queried), len(top_blocked))

    try:
        connection = psycopg2.connect(**DB_CONFIG)
        connection.autocommit = False
    except psycopg2.Error as exc:
        logger.error("Falha ao conectar no banco Postgres: %s", exc)
        raise

    try:
        with connection.cursor() as cursor:
            for entry in top_queried:
                parsed = _parse_domain_entry(entry)
                if not parsed:
                    logger.warning("Entrada inválida em consultas: %s", entry)
                    continue
                domain, count = parsed
                friendly = _normalize_domain(domain)
                _upsert_domain(cursor, APPLIANCE_NAME, friendly, count, "A")
                logger.info("[%s] Domínio consultado salvo: %s (%s)", APPLIANCE_NAME, friendly, count)

            for entry in top_blocked:
                parsed = _parse_domain_entry(entry)
                if not parsed:
                    logger.warning("Entrada inválida em bloqueios: %s", entry)
                    continue
                domain, count = parsed
                friendly = _normalize_domain(domain)
                _upsert_domain(cursor, APPLIANCE_NAME, friendly, count, "B")
                logger.info("[%s] Domínio bloqueado salvo: %s (%s)", APPLIANCE_NAME, friendly, count)

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
        logger.info("Processamento concluído")


if __name__ == "__main__":
    main()
