# 🚀 POPPFIRE ADMIN - Guia de Desenvolvimento

## 📋 Visão Geral

Sistema de administração Django 5.2.3 com AdminLTE4, integração com API Starlink e gerenciamento de portal captivo.

## 🔧 Configuração do Ambiente

### Pré-requisitos
- Python 3.11+
- PostgreSQL
- Git
- Windows PowerShell ou Command Prompt

### ⚡ Início Rápido

#### 1. Scripts Automatizados (Recomendado)

**Windows Batch:**
```bash
# Execute no diretório raiz do projeto
start_dev.bat
```

**PowerShell:**
```powershell
# Execute no diretório raiz do projeto
.\start_dev.ps1
```

#### 2. Configuração Manual

```powershell
# 1. Ativar ambiente virtual (PowerShell)
.\venv\Scripts\Activate.ps1

# 1. Alternativo (Command Prompt)
venv\Scripts\activate

# 2. Configurar settings.py (se necessário)
copy sreadmin\settings_local.py.template sreadmin\settings.py

# 3. Executar migrações
python manage.py makemigrations
python manage.py migrate

# 4. Iniciar servidor
python manage.py runserver
```

## 📁 Estrutura do Projeto

```
sreadmin/
├── venv/                    # Ambiente virtual Python
├── sreadmin/               # Configurações Django
│   ├── settings.py         # ⚠️ NÃO COMMITADO (produção)
│   └── settings_local.py.template  # Template para desenvolvimento
├── painel/                 # App principal
├── captive_portal/         # App virtual para menus
├── start_dev.bat          # Script Windows Batch
├── start_dev.ps1          # Script PowerShell
├── .gitignore             # Proteção de arquivos
└── manage.py              # Django management
```

## 🔒 Configuração de Produção

### settings.py
O arquivo `settings.py` é **PROTEGIDO** pelo `.gitignore` para evitar vazamento de credenciais.

#### Para Desenvolvimento:
1. Copie `settings_local.py.template` para `settings.py`
2. Ajuste as configurações locais conforme necessário

#### Para Produção:
1. Configure `settings.py` com credenciais seguras
2. Ajuste `ALLOWED_HOSTS`, `DEBUG=False`, etc.
3. **NUNCA** commite o arquivo `settings.py`

## 🌐 Acesso ao Sistema

- **Aplicação:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/
- **API Starlink:** Integração configurada no painel

## 🛠️ Desenvolvimento

### Comandos Úteis

```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar testes
python manage.py test

# Shell Django
python manage.py shell
```

### Estrutura de Apps

#### painel/
- **models.py:** Modelos de dados (RadCheck, Unidades, etc.)
- **views.py:** Views do sistema
- **admin.py:** Configuração do Django Admin
- **starlink_api.py:** Integração com API Starlink
- **templates/:** Templates HTML
- **management/commands/:** Comandos Django personalizados

#### captive_portal/
- App virtual para organização de menus
- Configuração de proxy models

## 📦 Dependências

```python
# Principais bibliotecas
Django==5.2.3
psycopg2-binary  # PostgreSQL
django-adminlte4  # Tema AdminLTE4
requests  # API calls
python-dateutil  # Manipulação de datas
```

## 🔄 Workflow Git

### Proteções Implementadas
- `.gitignore` protege `settings.py`
- Exclusão automática de `__pycache__/`
- Proteção de arquivos temporários Windows
- Exclusão de ambiente virtual

### Comandos Git Seguros
```bash
# Status seguro (não mostra settings.py)
git status

# Add files (settings.py será ignorado)
git add .

# Commit
git commit -m "Sua mensagem"

# Push
git push
```

## 🚨 Resolução de Problemas

### ⚠️ Ambiente Virtual - IMPORTANTE
**SEMPRE** trabalhe com o ambiente virtual ativado:

```powershell
# Para ativar o ambiente virtual (PowerShell)
.\venv\Scripts\Activate.ps1

# Para ativar o ambiente virtual (Command Prompt)
venv\Scripts\activate

# Verificar se está ativo (deve mostrar (venv) no prompt)
# (venv) PS C:\Projetos\Poppnet\sreadmin>
```

**Dica:** Para comandos únicos com ambiente virtual:
```powershell
# Executar comando único com venv ativo
powershell.exe -Command "& .\venv\Scripts\Activate.ps1; python manage.py migrate"
```

### Erro de Importação
```bash
# Reativar ambiente virtual
venv\Scripts\activate

# Reinstalar dependências
pip install -r requirements.txt
```

### Erro de Database
```bash
# Resetar migrações (cuidado!)
python manage.py migrate --fake painel zero
python manage.py migrate painel
```

### Erro de settings.py
```bash
# Recriar a partir do template
copy sreadmin\settings_local.py.template sreadmin\settings.py
```

## 📊 Recursos do Sistema

### AdminLTE4 Theme
- Interface responsiva moderna
- Menu lateral com organização por módulos
- Dashboards interativos
- Componentes UI avançados

### Integração Starlink
- Monitoramento de service lines
- Relatórios de usage
- Gestão de endereços
- API de billing

### Portal Captivo
- Gestão de usuários RADIUS
- Controle de acesso
- Relatórios de conexão

## 🔧 Customizações

### Adicionando Novos Módulos
1. Criar novo app: `python manage.py startapp novo_app`
2. Adicionar em `INSTALLED_APPS`
3. Configurar URLs
4. Criar models e migrations

### Modificando Interface
1. Templates em `painel/templates/`
2. Arquivos estáticos em `static/`
3. Customização AdminLTE4 em `settings.py`

## 📞 Suporte

Para dúvidas sobre desenvolvimento:
1. Consulte a documentação Django: https://docs.djangoproject.com/
2. AdminLTE4: https://adminlte.io/
3. API Starlink: Consulte documentação interna

---

**⚠️ IMPORTANTE:** Sempre use o ambiente virtual e nunca commite arquivos de configuração de produção!

**🎯 OBJETIVO:** Manter ambiente de desenvolvimento consistente e produção segura.
