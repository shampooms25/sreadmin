# Diferença de Horário no Registro de Visualizações

## Problema Identificado

**Sintoma:**
- Horário no OPNsense: `11:38:52`
- Horário no servidor Django: `11:11:27`
- Horário registrado no banco: `12:06:57`

## Causa Raiz

O endpoint `/api/captive-portal/success/` aceita um parâmetro opcional `timestamp`. Quando esse parâmetro **NÃO** é enviado, o sistema usa `timezone.now()` que pega a hora do **servidor Django**, não do cliente OPNsense.

**Código relevante em `captive_portal/api_views.py` (linhas 557-562):**
```python
if timestamp_str:
    # ... parseia o timestamp fornecido ...
else:
    date_view = timezone.now()  # ← Usa hora do servidor Django!
```

## Soluções

### ✅ Solução 1: Enviar timestamp do cliente (RECOMENDADA)

Ao fazer a chamada da API do OPNsense, **sempre envie o parâmetro `timestamp`**:

#### Exemplo com cURL (shell script):
```bash
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

curl -X POST "https://paineleld.poppnet.com.br/api/captive-portal/success/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"202020\",\"video\":\"eld01.mp4\",\"timestamp\":\"$TIMESTAMP\"}"
```

#### Exemplo com JavaScript (no portal HTML):
```javascript
const now = new Date();
const timestamp = now.getFullYear() + '-' + 
                  String(now.getMonth() + 1).padStart(2, '0') + '-' +
                  String(now.getDate()).padStart(2, '0') + ' ' +
                  String(now.getHours()).padStart(2, '0') + ':' +
                  String(now.getMinutes()).padStart(2, '0') + ':' +
                  String(now.getSeconds()).padStart(2, '0');

fetch('https://paineleld.poppnet.com.br/api/captive-portal/success/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: '202020',
        video: 'eld01.mp4',
        timestamp: timestamp
    })
});
```

### Solução 2: Ajustar timezone do servidor Django

Se não for possível enviar o timestamp do cliente, ajuste o timezone do Django para corresponder ao do OPNsense.

**Arquivo: `sreadmin/settings.py`**
```python
TIME_ZONE = 'America/Manaus'  # UTC-4 (mesmo do OPNsense)
USE_TZ = True
```

## Arquivos de Apoio Criados

1. **`scripts_opnsense/register_video_view.sh`**
   - Script shell pronto para uso no OPNsense
   - Envia automaticamente o timestamp correto
   - Uso: `./register_video_view.sh "202020" "eld01.mp4"`

2. **`scripts_opnsense/captive_video_tracker.js`**
   - Script JavaScript para incluir no `index.html` do portal
   - Detecta automaticamente quando o vídeo é assistido (80% ou finalizado)
   - Registra a visualização com timestamp do cliente
   - Inclua no HTML: `<script src="captive_video_tracker.js"></script>`

## Verificação

Para confirmar que o timestamp está sendo enviado corretamente:

```bash
# No servidor Django, monitore os logs:
tail -f /var/log/django/debug.log

# Você deve ver linhas como:
# Visualização registrada: 202020 assistiu eld01.mp4 em 2025-11-15 11:38:52
```

## Formatos de Timestamp Aceitos

O endpoint aceita os seguintes formatos:
- `YYYY-MM-DD HH:MM:SS` (ex: `2025-11-15 11:38:52`)
- `YYYY-MM-DDTHH:MM:SS` (ISO 8601, ex: `2025-11-15T11:38:52`)
- `YYYY-MM-DD HH:MM:SS.ffffff` (com microssegundos)
- `YYYY-MM-DDTHH:MM:SS.ffffff`

**Recomendado:** Use `YYYY-MM-DD HH:MM:SS` para máxima compatibilidade.
