#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests


def fetch_starlink_prefixes(api_url: str, token: str) -> list[str]:
    resp = requests.get(
        api_url.rstrip('/') + '/prefixes/?format=json',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return list(dict.fromkeys(data.get('prefixes') or []))


def adguard_access_list(base_url: str, username: str, password: str) -> dict:
    resp = requests.get(
        base_url.rstrip('/') + '/control/access/list',
        auth=(username, password),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def adguard_access_set(base_url: str, username: str, password: str, allowed_clients: list[str]) -> None:
    payload = {
        'allowed_clients': allowed_clients,
        'disallowed_clients': [],
        'blocked_hosts': [],
    }
    resp = requests.post(
        base_url.rstrip('/') + '/control/access/set',
        auth=(username, password),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()


def load_state(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        return set(json.loads(path.read_text(encoding='utf-8')))
    except Exception:
        return set()


def save_state(path: Path, cidrs: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cidrs, indent=2, ensure_ascii=False), encoding='utf-8')


def main() -> int:
    ap = argparse.ArgumentParser(description='Sincroniza allowlist do AdGuard Home mantendo entradas manuais.')
    ap.add_argument('--api-url', required=True, help='URL base do Django: ex https://app.exemplo.com/api/starlink')
    ap.add_argument('--api-token', required=True, help='Bearer token (ApplianceToken)')
    ap.add_argument('--adguard-url', required=True, help='URL base do AdGuard: ex http://127.0.0.1:3000')
    ap.add_argument('--adguard-user', required=True)
    ap.add_argument('--adguard-pass', required=True)
    ap.add_argument('--state-file', default='/var/lib/poppfire/starlink_adguard_state.json')
    ap.add_argument('--dry-run', action='store_true')

    args = ap.parse_args()

    state_file = Path(args.state_file)
    last_applied = load_state(state_file)

    starlink = fetch_starlink_prefixes(args.api_url, args.api_token)
    starlink_set = set(starlink)

    current = adguard_access_list(args.adguard_url, args.adguard_user, args.adguard_pass)
    current_allowed = list(dict.fromkeys(current.get('allowed_clients') or []))

    # Remove apenas o que nós mesmos aplicamos antes (não mexe em itens manuais)
    manual = [c for c in current_allowed if c not in last_applied]

    new_allowed = manual + [c for c in starlink if c not in manual]

    if args.dry_run:
        print('dry-run:')
        print(f'  current_allowed={len(current_allowed)} manual={len(manual)} starlink={len(starlink)}')
        print(f'  new_allowed={len(new_allowed)}')
        return 0

    adguard_access_set(args.adguard_url, args.adguard_user, args.adguard_pass, new_allowed)
    save_state(state_file, starlink)
    print(f'OK: allowed_clients={len(new_allowed)} starlink={len(starlink)} manual={len(manual)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
