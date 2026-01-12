#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import tempfile
from pathlib import Path

import requests


def fetch_starlink_prefixes(
    api_url: str,
    token: str,
    *,
    include_custom: bool = False,
    include_non_americas: bool = False,
) -> list[str]:
    url = api_url.rstrip('/') + '/prefixes/?format=text'
    if include_non_americas:
        url += '&include_non_americas=1'
    if include_custom:
        url += '&include_custom=1'
    resp = requests.get(
        url,
        headers={'Authorization': f'Bearer {token}'},
        timeout=30,
    )
    resp.raise_for_status()
    cidrs = [line.strip() for line in resp.text.splitlines() if line.strip()]
    # dedupe preserving order
    seen = set()
    out = []
    for c in cidrs:
        if c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out


def client_name_for_cidr(cidr: str) -> str:
    # Use full SHA1 to avoid name collisions with thousands of CIDRs.
    h = hashlib.sha1(cidr.encode('utf-8')).hexdigest()
    return f'starlink_{h}'


def render_clients_conf(cidrs: list[str], secret: str) -> str:
    lines = []
    lines.append('# Managed by POPPFIRE (starlink_allowlist). DO NOT EDIT.')
    for cidr in cidrs:
        name = client_name_for_cidr(cidr)
        lines.append('')
        lines.append(f'client {name} {{')
        lines.append(f'        ipaddr = {cidr}')
        lines.append(f'        secret = {secret}')
        lines.append('}')
    lines.append('')
    return '\n'.join(lines)


def file_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return ''


def backup_file(path: Path, keep_suffix: str = '.bak') -> None:
    if not path.exists():
        return
    bak = path.with_suffix(path.suffix + keep_suffix)
    bak.write_bytes(path.read_bytes())


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', delete=False, dir=str(path.parent), encoding='utf-8') as tmp:
        tmp.write(content)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def run_cmd(cmd: str) -> None:
    subprocess.run(cmd, shell=True, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description='Gera include do FreeRADIUS com clients Starlink (não mexe nos demais).')
    ap.add_argument('--api-url', required=True, help='URL base do Django: ex https://app.exemplo.com/api/starlink')
    ap.add_argument('--api-token', required=True, help='Bearer token (ApplianceToken)')
    ap.add_argument('--secret', required=True, help='Shared secret para os clients Starlink')
    ap.add_argument('--output-file', default='/etc/freeradius/3.0/clients_starlink.conf')
    ap.add_argument('--include-custom', action='store_true', help='Inclui prefixes cadastrados manualmente no painel (include_custom=1)')
    ap.add_argument('--include-non-americas', action='store_true', help='Inclui prefixes fora das Américas (include_non_americas=1)')
    ap.add_argument('--backup', action='store_true', help='Cria backup do arquivo de saída antes de sobrescrever')
    ap.add_argument('--validate-cmd', default='', help='Ex: freeradius -XC')
    ap.add_argument('--reload-cmd', default='', help='Ex: systemctl reload freeradius')
    ap.add_argument('--dry-run', action='store_true')

    args = ap.parse_args()

    cidrs = fetch_starlink_prefixes(
        args.api_url,
        args.api_token,
        include_custom=args.include_custom,
        include_non_americas=args.include_non_americas,
    )
    content = render_clients_conf(cidrs, args.secret)

    out_path = Path(args.output_file)

    if args.dry_run:
        print(f'dry-run: cidrs={len(cidrs)} output={out_path}')
        return 0

    previous = file_text(out_path)
    if previous == content:
        print(f'OK: no changes ({out_path})')
        return 0

    if args.backup:
        backup_file(out_path)

    atomic_write(out_path, content)

    if args.validate_cmd:
        run_cmd(args.validate_cmd)

    if args.reload_cmd:
        run_cmd(args.reload_cmd)

    print(f'OK: wrote {out_path} with {len(cidrs)} clients')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
