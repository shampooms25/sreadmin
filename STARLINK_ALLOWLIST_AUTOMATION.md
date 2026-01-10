# Automação de allowlist Starlink (FreeRADIUS + AdGuard Home)

## Visão geral

- O Django mantém uma lista de ASNs Starlink (ex.: `AS14593`) e os *prefixes* aprendidos via BGP (fonte: BGPView).
- A cada atualização, o sistema classifica cada prefix como **Américas** usando RDAP (`rdap.org`) e a heurística:
  - `rir` em `arin|lacnic|nicbr` => Américas
  - fallback por `country` (ISO-3166) se `rir` não estiver disponível
- A API publica **apenas os prefixes classificados como Américas** por padrão.
- Nos servidores, scripts Linux consomem a API e aplicam:
  - FreeRADIUS: gera um include `clients_starlink.conf` (não mexe nos seus outros clients)
  - AdGuard: atualiza `allowed_clients` preservando entradas manuais (remove só o que o script aplicou na execução anterior)

## Endpoints

- Health: `/api/starlink/health/`
- Prefixes:
  - JSON: `/api/starlink/prefixes/?format=json`
  - Text: `/api/starlink/prefixes/?format=text`
  - Filtros:
    - `ip_version=4|6`
    - `include_non_americas=1`

**Autenticação:** `Authorization: Bearer <token>` (reusa o padrão do app `captive_portal`).

## Banco de dados

Modelos no app `starlink_allowlist`:
- `StarlinkASN`: ASNs Starlink habilitados
- `StarlinkPrefix`: prefixes ativos/inativos + metadados (rir/country/is_americas)
- `StarlinkUpdateRun`: histórico das execuções

Migração `0002` cria o ASN padrão: `AS14593`.

## Atualização (no servidor Django)

Rodar manual:

```bash
python manage.py update_starlink_prefixes
```

Dry-run:

```bash
python manage.py update_starlink_prefixes --dry-run
```

Sugestão cron (1/1h):

```cron
0 * * * * /usr/bin/python3 /caminho/do/app/manage.py update_starlink_prefixes >> /var/log/starlink_prefixes.log 2>&1
```

## Script: AdGuard Home

Arquivo: `scripts_starlink/sync_adguard_starlink.py`

- Requer Basic Auth do AdGuard.
- Usa um arquivo de estado para lembrar quais entries Starlink foram aplicadas na última execução.

Exemplo:

```bash
python3 sync_adguard_starlink.py \
  --api-url "https://SEU-DJANGO/api/starlink" \
  --api-token "SEU_TOKEN" \
  --adguard-url "http://127.0.0.1:3000" \
  --adguard-user "admin" \
  --adguard-pass "SENHA" \
  --state-file "/var/lib/poppfire/starlink_adguard_state.json"
```

## Script: FreeRADIUS

Arquivo: `scripts_starlink/sync_freeradius_starlink.py`

Esse script **só escreve** um include gerenciado (não toca no seu `clients.conf` principal).

Exemplo:

```bash
python3 sync_freeradius_starlink.py \
  --api-url "https://SEU-DJANGO/api/starlink" \
  --api-token "SEU_TOKEN" \
  --secret "poppnet@vpn@radius" \
  --output-file "/etc/freeradius/3.0/clients_starlink.conf" \
  --validate-cmd "freeradius -XC" \
  --reload-cmd "systemctl reload freeradius"
```

No seu `clients.conf`, você inclui uma vez:

```conf
$INCLUDE /etc/freeradius/3.0/clients_starlink.conf
```

## Admin UI

Tudo fica no Django Admin:
- Starlink ASNs
- Starlink Prefixes
- Starlink Update Runs

