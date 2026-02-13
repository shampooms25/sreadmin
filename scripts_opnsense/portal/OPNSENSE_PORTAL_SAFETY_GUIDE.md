# Guia de Segurança: Customização do Portal Captive OPNsense

Este documento detalha áreas críticas do sistema de arquivos do OPNsense que **NÃO** devem ser alteradas ao instalar ou persistir um portal captive customizado.

## 🚨 ÁREA DE PERIGO (NÃO TOCAR)

### Interface Administrativa (GUI)
O diretório abaixo contém os arquivos da interface de **gerenciamento** do Captive Portal (onde o administrador configura zonas, vouchers, etc). Alterar arquivos aqui quebrará o acesso à configuração via web.

*   **Caminho:** `/usr/local/opnsense/mvc/app/views/OPNsense/CaptivePortal/`
*   **Arquivo Crítico:** `index.volt` (Este é o template da GUI administrativa, **NÃO** do portal de visitantes).
*   **Sintoma de Erro:** Ao acessar "Services > Captive Portal > Administration", a tela exibe o portal de login do usuário ou fica em branco/quebrada.

**Regra de Ouro:** Nunca copie arquivos HTML/Assets para dentro de diretórios `mvc/app/views`.

---

## ✅ ÁREAS SEGURAS (Persistência)

Para garantir que o portal customizado persista após reinicializações ou atualizações de firmware, utilize apenas os caminhos destinados aos **templates de geração** do portal de visitantes.

### 1. Templates de Script (Legacy/Standard)
Estes diretórios são usados pelos scripts de inicialização do OPNsense para popular `/var/captiveportal/zoneX/htdocs` quando uma nova zona é criada ou o sistema reinicia.

*   `/usr/local/opnsense/scripts/OPNsense/CaptivePortal/htdocs_default`
*   `/usr/local/datastore/captiveportal/htdocs_default`

### 2. Arquivos ZIP de Template
O OPNsense pode restaurar o portal padrão a partir de arquivos ZIP. Substituir estes arquivos é uma estratégia válida de persistência, desde que **não** sejam arquivos de sistema do core.

*   **Alvo Seguro:** `htdocs_default.zip` (geralmente em `/usr/local/opnsense/scripts/...` ou `/usr/local/datastore/...`)
*   **Evitar:** Qualquer ZIP que pareça ser parte de um pacote de sistema (ex: `os-captiveportal.zip` ou similar na raiz do sistema).

---

## ⚠️ Resumo da Estrutura

| Caminho | Função | Pode Alterar? |
| :--- | :--- | :--- |
| `/var/captiveportal/zoneX/htdocs` | Portal rodando em memória (Runtime) | **SIM** (Mas perde no reboot) |
| `/usr/local/opnsense/mvc/app/views/...` | **Interface Administrativa (WebGUI)** | **NÃO (PERIGO)** |
| `/usr/local/opnsense/scripts/.../htdocs_default` | Template base para novas zonas | **SIM** (Persistência Segura) |
| `/usr/local/datastore/.../htdocs_default` | Template base (algumas versões) | **SIM** (Persistência Segura) |

## Recuperação de Desastre

Caso a interface administrativa tenha sido sobrescrita acidentalmente:

1.  **Restaurar Backup:** Se o script criou `.bak`, reverta:
    ```bash
    cd /usr/local/opnsense/mvc/app/views/OPNsense/CaptivePortal/
    mv index.volt.bak index.volt
    ```
2.  **Reinstalar Core:** Se não houver backup, force a reinstalação dos arquivos do sistema (não apaga configurações):
    ```bash
    opnsense-revert -r opnsense
    service configd restart
    configctl webgui restart
    ```
