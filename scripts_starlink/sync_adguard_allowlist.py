#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests


def fetch_allowlist_prefixes(
    django_api_url: str,
    token: str,
    *,
    ip_version: str = "",
    include_non_americas: bool = False,
    include_custom: bool = False,
) -> list[str]:
    params: dict[str, str] = {"format": "json"}
    if ip_version in {"4", "6"}:
        params["ip_version"] = ip_version
    if include_non_americas:
        params["include_non_americas"] = "1"
    if include_custom:
        params["include_custom"] = "1"

    url = django_api_url.rstrip("/") + "/prefixes/"
    resp = requests.get(
        url,
        params=params,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    prefixes = data.get("prefixes") or []
    out: list[str] = []
    seen: set[str] = set()
    for item in prefixes:
        cidr = str(item).strip()
        if not cidr or cidr in seen:
            continue
        seen.add(cidr)
        out.append(cidr)
    return out


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_list(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for v in values or []:
        s = str(v).strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Sincroniza allowlist de clientes no AdGuard Home (allowed_clients) usando prefixes do POPPFIRE. "
            "Recomendado para rodar via crontab no servidor do AdGuard."
        )
    )
    ap.add_argument(
        "--django-api-url",
        required=True,
        help="URL base do endpoint Starlink Allowlist no Django (ex: https://app.exemplo.com/api/starlink)",
    )
    ap.add_argument("--django-token", required=True, help="Bearer token (ApplianceToken)")
    ap.add_argument(
        "--include-custom",
        action="store_true",
        help="Inclui prefixes cadastrados manualmente no painel (non-Starlink)",
    )
    ap.add_argument(
        "--include-non-americas",
        action="store_true",
        help="Inclui prefixes fora das Américas (por padrão o endpoint filtra)",
    )
    ap.add_argument("--ip-version", choices=["4", "6"], default="", help="Filtrar IPv4 ou IPv6")

    ap.add_argument(
        "--adguard-url",
        required=True,
        help="URL base do AdGuard Home (ex: http://127.0.0.1:3000)",
    )
    ap.add_argument("--adguard-user", required=True)
    ap.add_argument("--adguard-pass", required=True)

    ap.add_argument(
        "--preserve-existing",
        action="store_true",
        help=(
            "Mantém itens já existentes em allowed_clients e apenas adiciona os do painel. "
            "Por segurança, use isso no primeiro deploy para evitar lock-out."
        ),
    )
    ap.add_argument(
        "--backup-file",
        default="./adguard_access_list_backup.json",
        help="Caminho para salvar backup do /control/access/list antes de aplicar mudanças",
    )
    ap.add_argument("--dry-run", action="store_true")

    args = ap.parse_args()

    cidrs = fetch_allowlist_prefixes(
        args.django_api_url,
        args.django_token,
        ip_version=args.ip_version,
        include_non_americas=args.include_non_americas,
        include_custom=args.include_custom,
    )

    access_list_url = args.adguard_url.rstrip("/") + "/control/access/list"
    access_set_url = args.adguard_url.rstrip("/") + "/control/access/set"

    auth = (args.adguard_user, args.adguard_pass)

    resp = requests.get(access_list_url, auth=auth, timeout=20)
    resp.raise_for_status()
    current = resp.json() or {}

    current_allowed = normalize_list(current.get("allowed_clients") or [])
    current_disallowed = normalize_list(current.get("disallowed_clients") or [])
    current_blocked_hosts = normalize_list(current.get("blocked_hosts") or [])

    new_allowed = cidrs
    if args.preserve_existing:
        new_allowed = normalize_list(current_allowed + cidrs)

    # comparar por conjunto (ordem não importa no AdGuard)
    if set(new_allowed) == set(current_allowed):
        print(f"OK: no changes (allowed_clients count={len(current_allowed)})")
        return 0

    backup_path = Path(args.backup_file)
    write_json(
        backup_path,
        {
            "source": access_list_url,
            "allowed_clients": current_allowed,
            "disallowed_clients": current_disallowed,
            "blocked_hosts": current_blocked_hosts,
        },
    )

    payload = {
        "allowed_clients": new_allowed,
        "disallowed_clients": current_disallowed,
        "blocked_hosts": current_blocked_hosts,
    }

    if args.dry_run:
        print(
            "dry-run: "
            + json.dumps(
                {
                    "backup": str(backup_path),
                    "allowed_clients_before": len(current_allowed),
                    "allowed_clients_after": len(new_allowed),
                },
                ensure_ascii=False,
            )
        )
        return 0

    resp2 = requests.post(access_set_url, auth=auth, json=payload, timeout=30)
    resp2.raise_for_status()

    print(
        f"OK: updated AdGuard Home allowed_clients {len(current_allowed)} -> {len(new_allowed)}; backup={backup_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
