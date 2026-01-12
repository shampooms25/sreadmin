# Automação de allowlist Starlink (FreeRADIUS + AdGuard Home)

## Visão geral

- O Django mantém uma lista de ASNs Starlink (ex.: `AS14593`) e os *prefixes* aprendidos via BGP.
- O comando tenta buscar prefixes via **BGPView** e, se falhar (DNS/bloqueio), faz fallback para **RIPEstat**.
- A cada atualização, o sistema pode classificar cada prefix como **Américas** usando RDAP (`rdap.org`) e a heurística:
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
    - `include_custom=1` (inclui prefixes cadastrados manualmente no painel)

**Autenticação:** `Authorization: Bearer <token>` (reusa o padrão do app `captive_portal`).

**Observação (Apache/mod_wsgi):** se a API retornar 401 mesmo com token correto, habilite o repasse do header:

```apache
WSGIPassAuthorization On
```

e recarregue o Apache.

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

### Modo recomendado para produção (2 fases)

1) Atualiza a lista rapidamente (sem RDAP):

```bash
python manage.py update_starlink_prefixes --no-rdap
```

2) Em horário de baixa, completa metadados (somente os que estão faltando):

```bash
python manage.py update_starlink_prefixes --backfill-missing
```

### Crontab (recomendado) sem vazar segredos

Para evitar expor tokens/senhas no `crontab -l`, use um arquivo `env` root-only e scripts wrapper.

No repo existem exemplos em:
- `scripts_starlink/poppfire_starlink_sync.env.example`
- `scripts_starlink/run_update_starlink_prefixes.sh`
- `scripts_starlink/run_sync_freeradius_starlink.sh`

Fluxo sugerido no servidor:

1) Criar o arquivo de ambiente (ajuste os valores):

```bash
sudo mkdir -p /etc/poppfire
sudo cp /var/www/sreadmin/scripts_starlink/poppfire_starlink_sync.env.example /etc/poppfire/starlink_sync.env
sudo chmod 600 /etc/poppfire/starlink_sync.env
sudo nano /etc/poppfire/starlink_sync.env
```

2) Tornar wrappers executáveis:

```bash
sudo chmod +x /var/www/sreadmin/scripts_starlink/run_update_starlink_prefixes.sh
sudo chmod +x /var/www/sreadmin/scripts_starlink/run_sync_freeradius_starlink.sh
```

3) Agendar (exemplo: atualiza 03:00, sincroniza 03:10):

```cron
0 3 * * * /var/www/sreadmin/scripts_starlink/run_update_starlink_prefixes.sh
10 3 * * * /var/www/sreadmin/scripts_starlink/run_sync_freeradius_starlink.sh
```

Dry-run:

```bash
python manage.py update_starlink_prefixes --dry-run
```

Sugestão cron (1/1h):

```cron
# Sugestão: atualização “rápida” diária (ajuste o horário)
0 3 * * * /usr/bin/python3 /caminho/do/app/manage.py update_starlink_prefixes --no-rdap >> /var/log/starlink_prefixes.log 2>&1

# Sugestão: backfill RDAP semanal (pode demorar)
0 4 * * 0 /usr/bin/python3 /caminho/do/app/manage.py update_starlink_prefixes --backfill-missing >> /var/log/starlink_prefixes_backfill.log 2>&1
```

## Script: AdGuard Home

### Opção A (recomendada): allowlist com backup

Arquivo: `scripts_starlink/sync_adguard_allowlist.py`

- Faz backup do `/control/access/list` antes de aplicar.
- Pode preservar entradas existentes (modo seguro para o primeiro deploy).

Exemplo (primeira execução, mais segura):

```bash
python3 sync_adguard_allowlist.py \
  --django-api-url "https://SEU-DJANGO/api/starlink" \
  --django-token "SEU_TOKEN" \
  --include-custom \
  --adguard-url "http://127.0.0.1:3000" \
  --adguard-user "admin" \
  --adguard-pass "SENHA" \
  --preserve-existing \
  --backup-file "/var/lib/poppfire/adguard_access_list_backup.json"
```

Depois que estiver validado, você pode remover `--preserve-existing` para deixar o `allowed_clients` apenas com o que vem do painel (mais “limpo”).

### Opção B (legado): estado + preserva manual automaticamente

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
  --output-file "/etc/freeradius/clients_starlink.conf" \
  --validate-cmd "freeradius -XC" \
  --reload-cmd "systemctl reload freeradius"
```

No seu `clients.conf`, você inclui uma vez:

```conf
$INCLUDE /etc/freeradius/clients_starlink.conf
```

### BlastRADIUS / Message-Authenticator

Em versões recentes, o FreeRADIUS pode logar avisos do tipo:

- `BlastRADIUS check: Received packet without Message-Authenticator.`

Isso significa que o NAS/cliente que está enviando RADIUS para o servidor não está incluindo o atributo `Message-Authenticator`.

- Correção ideal: **atualizar o NAS/firmware/software** para enviar `Message-Authenticator`.
- Mitigação (compatibilidade): definir `require_message_authenticator = false` nos clients afetados.

Como o include é gerado automaticamente (muitos clients), o wrapper suporta configurar essas diretivas via `/etc/poppfire/starlink_sync.env`:

```bash
# unset | true | false
REQUIRE_MESSAGE_AUTHENTICATOR=false
LIMIT_PROXY_STATE=true
```

Depois rode o wrapper e recarregue/reinicie o serviço.

## Admin UI

Tudo fica no Django Admin:
- Starlink ASNs
- Starlink Prefixes
- Starlink Update Runs

