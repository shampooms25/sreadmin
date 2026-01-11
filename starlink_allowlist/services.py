from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass(frozen=True)
class RdapInfo:
    country: str
    rir: str


_RIR_BY_PORT43 = {
    'whois.arin.net': 'arin',
    'whois.lacnic.net': 'lacnic',
    'whois.ripe.net': 'ripe',
    'whois.apnic.net': 'apnic',
    'whois.afrinic.net': 'afrinic',
    'whois.registro.br': 'nicbr',
}


def _guess_rir_from_port43(port43: str) -> str:
    port43 = (port43 or '').strip().lower()
    return _RIR_BY_PORT43.get(port43, '')


def _guess_rir_from_links(links: list[dict]) -> str:
    for link in links or []:
        href = (link.get('href') or '').lower()
        if 'rdap.arin.net' in href:
            return 'arin'
        if 'rdap.lacnic.net' in href:
            return 'lacnic'
        if 'rdap.ripe.net' in href:
            return 'ripe'
        if 'rdap.apnic.net' in href:
            return 'apnic'
        if 'rdap.afrinic.net' in href:
            return 'afrinic'
        if 'rdap.registro.br' in href:
            return 'nicbr'
    return ''


def rdap_lookup_any(ip: str, timeout_seconds: float = 8.0) -> Optional[RdapInfo]:
    """Resolve RDAP via rdap.org (bootstrap) e retorna (country, rir).

    Retorna None se falhar.
    """
    try:
        # Validação básica
        ipaddress.ip_address(ip)
    except ValueError:
        return None

    try:
        resp = requests.get(
            f'https://rdap.org/ip/{ip}',
            headers={'Accept': 'application/rdap+json'},
            timeout=timeout_seconds,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None

    country = (data.get('country') or '').strip().upper()
    rir = _guess_rir_from_port43(data.get('port43') or '')
    if not rir:
        rir = _guess_rir_from_links(data.get('links') or [])

    return RdapInfo(country=country, rir=rir)


def classify_is_americas(rir: str, country: str) -> bool:
    """Heurística simples: ARIN/LACNIC (e nicbr) = Américas.

    Isso atende ao seu requisito prático ("usar apenas ASNs Starlink da América").
    """
    rir = (rir or '').strip().lower()
    if rir in {'arin', 'lacnic', 'nicbr'}:
        return True

    # fallback se não conseguimos rir
    country = (country or '').strip().upper()
    if country in {
        'US', 'CA', 'MX',
        'BR', 'AR', 'CL', 'PE', 'CO', 'UY', 'PY', 'BO', 'EC', 'VE',
        'GY', 'SR', 'GF',
        'PA', 'CR', 'NI', 'HN', 'SV', 'GT', 'BZ',
        'CU', 'DO', 'HT', 'JM', 'TT', 'BS', 'BB',
    }:
        return True

    return False


def classify_region(rir: str, country: str) -> str:
    """Classifica região em alto nível (coarse) para fins de auditoria.

    Como o objetivo é dar visibilidade e controle operacional, usamos o RIR
    quando disponível (mais estável do que uma tabela completa de países).

    Retornos: 'americas' | 'europe' | 'apac' | 'africa' | 'unknown'
    """
    rir = (rir or '').strip().lower()
    if rir in {'arin', 'lacnic', 'nicbr'}:
        return 'americas'
    if rir == 'ripe':
        return 'europe'
    if rir == 'apnic':
        return 'apac'
    if rir == 'afrinic':
        return 'africa'

    # fallback leve: se conseguimos identificar Américas por país
    if classify_is_americas(rir='', country=country):
        return 'americas'
    return 'unknown'
