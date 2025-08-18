from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.shortcuts import render, redirect
from .models import Radcheck, EldRegistroViewVideos, Unidades, EldUploadVideo, EldGerenciarPortal, EldPortalSemVideo
from django.db.models.functions import TruncDay
from django.db.models import Count, Max
from django.utils.html import format_html
from django import forms
import csv
import io

# Formulário personalizado para a tela de adição do Radcheck
class RadcheckAddForm(forms.ModelForm):
    class Meta:
        model = Radcheck
        fields = ['username']

# Formulário para importação de CSV
class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label="Selecione o arquivo CSV")

# Modelo fictício para criar o menu Starlink Admin
from .models import StarlinkAdminProxy

class StarlinkAdminModelAdmin(admin.ModelAdmin):
    """
    Admin personalizado para o Starlink Admin
    """
    
    def get_urls(self):
        """
        Sobrescreve as URLs para redirecionar para nossa view personalizada
        """
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.starlink_admin_view), name='painel_starlinkapproxy_changelist'),
        ]
        return custom_urls + urls
    
    def starlink_admin_view(self, request):
        """
        View personalizada que redireciona para nossa página principal
        """
        from django.shortcuts import redirect
        return redirect('/starlink/starlink/')  # Redireciona para a página principal do Starlink
    
    def has_module_permission(self, request):
        return True
    
    def has_view_permission(self, request, obj=None):
        return True
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

# Registrar o modelo fictício
admin.site.register(StarlinkAdminProxy, StarlinkAdminModelAdmin)

# Configuração do Django Admin Site
admin.site.site_header = 'POPPFIRE ADMIN'
admin.site.site_title = 'POPPFIRE ADMIN'
admin.site.index_title = 'Painel de Administração'

# Traduções personalizadas para o admin

@admin.register(Radcheck)
class RadcheckAdmin(admin.ModelAdmin):
    list_display = ('username', 'attribute')
    search_fields = ('username', 'attribute', 'value')
    list_per_page = 50
    ordering = ('username', 'attribute')
    show_full_result_count = False  # Otimização para tabelas grandes
    
    # Campos editáveis na lista - removido 'value' pois foi substituído por 'value_preview'
    list_editable = ()
    
    # Seleção múltipla melhorada
    actions_on_top = True
    actions_on_bottom = False  # Removido para evitar duplicação
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Usa um formulário simplificado para adicionar novos usuários (apenas username)
        e o formulário completo para edição.
        """
        if obj is None:
            return RadcheckAddForm
        else:
            return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Define valores padrão para os campos ocultos ao criar um novo usuário
        através do formulário simplificado.
        """
        if not change:  # 'change' é False quando estamos adicionando um novo objeto
            obj.attribute = 'Cleartext-Password'
            obj.op = ':='
            obj.value = '123'  # Senha padrão
        super().save_model(request, obj, form, change)

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('username', 'attribute'),
            'description': 'Dados básicos do usuário e tipo de atributo RADIUS'
        }),
        ('Configuração', {
            'fields': ('op', 'value'),
            'description': 'Configure o operador e valor para o atributo RADIUS'
        }),
    )
      # Filtros laterais personalizados - removido 'username' para evitar lentidão
    list_filter = (
        ('attribute', admin.AllValuesFieldListFilter),
        ('op', admin.ChoicesFieldListFilter),
    )
    
    # Campos de busca avançada
    search_help_text = 'Busque por usuário, atributo ou valor'
      # Ações personalizadas
    actions = ['duplicate_selected', 'export_csv', 'enable_users', 'disable_users']
    
    def value_preview(self, obj):
        """Mostrar preview do valor com limitação de caracteres"""
        if len(obj.value) > 30:
            return f"{obj.value[:30]}..."
        return obj.value
    value_preview.short_description = 'Valor'
    
    def duplicate_selected(self, request, queryset):
        for obj in queryset:
            obj.pk = None  # Remove a chave primária para criar um novo objeto
            obj.save()
        self.message_user(request, f'{queryset.count()} registros duplicados com sucesso.')
    duplicate_selected.short_description = 'Duplicar registros selecionados'
    
    def export_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="radcheck_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Usuario', 'Atributo', 'Operador', 'Valor'])
        
        for obj in queryset:
            writer.writerow([obj.username, obj.attribute, obj.op, obj.value])
            
        return response
    export_csv.short_description = 'Exportar selecionados para CSV'
    
    def enable_users(self, request, queryset):
        """Habilitar usuários selecionados (set value para não vazio)"""
        count = 0
        for obj in queryset:
            if obj.attribute.lower() in ['cleartext-password', 'md5-password', 'nt-password']:
                if not obj.value or obj.value.strip() == '':
                    obj.value = 'senha123'  # Senha padrão
                    obj.save()
                    count += 1
        self.message_user(request, f'{count} usuários habilitados com senha padrão.')
    enable_users.short_description = 'Habilitar usuários selecionados'
    
    def disable_users(self, request, queryset):
        """Desabilitar usuários selecionados (set value vazio)"""
        count = 0
        for obj in queryset:
            if obj.attribute.lower() in ['cleartext-password', 'md5-password', 'nt-password']:
                obj.value = ''
                obj.save()
                count += 1
        self.message_user(request, f'{count} usuários desabilitados.')
    disable_users.short_description = 'Desabilitar usuários selecionados'
    
    def created_display(self, obj):
        return "Ativo"
    created_display.short_description = 'Status'
      # Customizar formulário
    def get_form(self, request, obj=None, **kwargs):
        """
        Usa um formulário personalizado para a tela de adição.
        """
        if obj is None:
            # Tela de "Adicionar"
            return RadcheckAddForm
        else:
            # Tela de "Alterar"
            return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Define os valores padrão ao criar um novo usuário.
        """
        if not change:  # Apenas na criação (add view)
            obj.attribute = 'Cleartext-Password'
            obj.op = ':='
            obj.value = '123'
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Excluir usuários com base na política de segurança
        if request.user.username != 'admin':
            qs = qs.exclude(username='admin')
        return qs
    
    # View personalizada para estatísticas
    def changelist_view(self, request, extra_context=None):
        # Adicionar estatísticas ao contexto
        extra_context = extra_context or {}
        
        # Contar registros por atributo
        attributes_stats = Radcheck.objects.values('attribute').annotate(
            count=Count('attribute')
        ).order_by('-count')
        
        # Contar registros por operador
        operators_stats = Radcheck.objects.values('op').annotate(
            count=Count('op')
        ).order_by('-count')
        
        # Total de usuários únicos
        unique_users = Radcheck.objects.values('username').distinct().count()
        
        extra_context.update({
            'attributes_stats': attributes_stats,
            'operators_stats': operators_stats,
            'unique_users': unique_users,
            'total_records': Radcheck.objects.count(),
        })
        
        return super().changelist_view(request, extra_context=extra_context)
    
    # View personalizada para relatórios
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('relatorio/', self.admin_site.admin_view(self.relatorio_view), name='painel_radcheck_relatorio'),
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='painel_radcheck_import_csv'),
        ]
        return custom_urls + urls
    
    def import_csv_view(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]
                
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, 'Erro: O arquivo selecionado não é um CSV.')
                    return redirect(request.path)

                try:
                    decoded_file = csv_file.read().decode('utf-8')
                    io_string = io.StringIO(decoded_file)
                    
                    # Pula o cabeçalho
                    next(io_string)
                    
                    reader = csv.reader(io_string)
                    
                    imported_count = 0
                    skipped_count = 0
                    
                    existing_usernames = set(Radcheck.objects.values_list('username', flat=True))

                    for row in reader:
                        if not row: continue
                        username = row[0].strip()
                        
                        if not username:
                            continue

                        if username not in existing_usernames:
                            Radcheck.objects.create(
                                username=username,
                                attribute='Cleartext-Password',
                                op=':=',
                                value='123'
                            )
                            existing_usernames.add(username)
                            imported_count += 1
                        else:
                            skipped_count += 1
                    
                    self.message_user(request, f"Importação concluída: {imported_count} usuários adicionados, {skipped_count} ignorados (já existentes).")
                except Exception as e:
                    self.message_user(request, f"Ocorreu um erro ao processar o arquivo: {e}", level=messages.ERROR)

                return redirect("..")
        
        form = CsvImportForm()
        context = self.admin_site.each_context(request)
        context.update({
            'form': form,
            'title': 'Importar Usuários via CSV',
            'opts': self.model._meta,
        })
        return render(request, 'admin/painel/radcheck/import_csv.html', context)

    def relatorio_view(self, request):
        """View personalizada para relatórios detalhados"""
        from django.template.response import TemplateResponse
        
        # Estatísticas básicas
        total_users = Radcheck.objects.values('username').distinct().count()
        total_records = Radcheck.objects.count()
        
        # Análise por atributos
        attr_stats = Radcheck.objects.values('attribute').annotate(
            count=Count('attribute')
        ).order_by('-count')
        
        # Usuários com múltiplos atributos
        users_with_multiple_attrs = Radcheck.objects.values('username').annotate(
            attr_count=Count('attribute')
        ).filter(attr_count__gt=1).order_by('-attr_count')
        
        # Atributos mais comuns
        common_attributes = [
            'Cleartext-Password', 'MD5-Password', 'NT-Password', 
            'Expiration', 'Session-Timeout', 'Simultaneous-Use'
        ]
        
        attr_usage = {}
        for attr in common_attributes:
            attr_usage[attr] = Radcheck.objects.filter(attribute=attr).count()
        
        context = {
            'title': 'Relatório RADIUS - Análise Detalhada',
            'total_users': total_users,
            'total_records': total_records,
            'attr_stats': attr_stats,
            'users_with_multiple_attrs': users_with_multiple_attrs[:20],
            'attr_usage': attr_usage,
            'opts': self.model._meta,
        }
        
        return TemplateResponse(request, 'admin/painel/radcheck/relatorio.html', context)

    def get_fieldsets(self, request, obj=None):
        if not obj:  # Se 'obj' não existe, estamos na tela de ADICIONAR
            return (
                (None, {'fields': ('username',)}),
            )
        # Caso contrário, estamos na tela de EDITAR, então usamos os fieldsets completos
        return super().get_fieldsets(request, obj)

# Removemos o registro automático do EldRegistroViewVideos para reregistrar dentro do grupo Captive Portal
# @admin.register(EldRegistroViewVideos) - REMOVIDO

# PROXY MODELS MOVIDOS PARA painel/models.py

class EldRegistroViewVideosAdmin(admin.ModelAdmin):
    list_display = ('username', 'video', 'formatted_date_view')
    search_fields = ('username', 'video')
    list_filter = ('date_view',)
    ordering = ('-date_view',)

    def formatted_date_view(self, obj):
        if obj.date_view:
            return obj.date_view.strftime("%d/%m/%Y %H:%M:%S")
        return "N/A"
    formatted_date_view.short_description = 'Data e Hora da Visualização'
    formatted_date_view.admin_order_field = 'date_view'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('grouped/', self.admin_site.admin_view(self.grouped_view), name='captive_portal_logsvideosproxy_grouped'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        # Redireciona para a view agrupada por padrão
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(reverse('admin:captive_portal_logsvideosproxy_grouped'))

    def grouped_view(self, request):
        # Lógica para agrupar os dados
        queryset = EldRegistroViewVideos.objects.all()
        
        # Filtros opcionais por período
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date_view__date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date_view__date__lte=date_to_obj)
            except ValueError:
                pass
        
        # Agrupamento por usuário, vídeo e dia
        grouped_data = (
            queryset.annotate(day=TruncDay('date_view'))
            .values('username', 'video', 'day')
            .annotate(
                view_count=Count('id'),
                last_view=Max('date_view')
            )
            .order_by('-day', 'username', 'video')
        )
        
        # Estatísticas gerais
        total_views = queryset.count()
        unique_users = queryset.values('username').distinct().count()
        unique_videos = queryset.values('video').distinct().count()
        
        # Calcular total de visualizações nos dados agrupados
        total_grouped_views = sum(item['view_count'] for item in grouped_data)
        
        context = dict(
           self.admin_site.each_context(request),
           title="Logs de Vídeos Agrupados por Dia",
           grouped_data=grouped_data,
           total_views=total_views,
           unique_users=unique_users,
           unique_videos=unique_videos,
           total_grouped_views=total_grouped_views,
           date_from=date_from,
           date_to=date_to,
           opts=self.model._meta,
           original_changelist_url=reverse('admin:captive_portal_logsvideosproxy_changelist')
        )
        return TemplateResponse(request, "admin/painel/eldregistroviewvideos/grouped_list.html", context)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Unidades)
class UnidadesAdmin(admin.ModelAdmin):
    list_display = ('designacao', 'sigla', 'nome_empresa', 'cidade_filial', 'estado_filial', 'servicelinenumber')
    search_fields = ('designacao', 'sigla', 'nome_empresa', 'cidade_filial', 'estado_filial', 'servicelinenumber', 'email')
    list_filter = ('estado_filial', 'grupo_empresa', 'negocio_faturamento')
    ordering = ('designacao',)
    list_per_page = 50
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('designacao', 'sigla', 'kit'),
            'description': 'Informações básicas da unidade'
        }),
        ('Empresa', {
            'fields': ('nome_empresa', 'grupo_empresa', 'negocio_faturamento'),
            'description': 'Dados empresariais'
        }),
        ('Localização', {
            'fields': ('estado_filial', 'cidade_filial', 'endereco', 'cep'),
            'description': 'Informações de localização'
        }),
        ('Contato e Serviços', {
            'fields': ('email', 'servicelinenumber', 'data_ativacao'),
            'description': 'Dados de contato e configurações de serviço'
        }),
    )
    
    # Campos de busca avançada
    search_help_text = 'Busque por designação, sigla, empresa, cidade, estado, service line number ou email'
    
    # Ações personalizadas
    actions = ['export_csv']
    
    def export_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="unidades_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Designação', 'Sigla', 'Kit', 'Grupo Empresa', 'Negócio Faturamento',
            'Nome Empresa', 'Estado', 'Cidade', 'Endereço', 'CEP', 
            'Data Ativacao', 'Service Line Number', 'Email'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.designacao, obj.sigla, obj.kit, obj.grupo_empresa,
                obj.negocio_faturamento, obj.nome_empresa, obj.estado_filial,
                obj.cidade_filial, obj.endereco, obj.cep, obj.data_ativacao,
                obj.servicelinenumber, obj.email
            ])
            
        return response
    export_csv.short_description = 'Exportar selecionados para CSV'
    
    # View personalizada para estatísticas
    def changelist_view(self, request, extra_context=None):
        # Adicionar estatísticas ao contexto
        extra_context = extra_context or {}
        
        # Estatísticas por estado
        estados_stats = Unidades.objects.values('estado_filial').annotate(
            count=Count('estado_filial')
        ).order_by('-count').filter(estado_filial__isnull=False)
        
        # Estatísticas por grupo empresa
        grupos_stats = Unidades.objects.values('grupo_empresa').annotate(
            count=Count('grupo_empresa')
        ).order_by('-count').filter(grupo_empresa__isnull=False)
        
        # Total de unidades
        total_unidades = Unidades.objects.count()
        
        extra_context.update({
            'estados_stats': estados_stats[:5],  # Top 5 estados
            'grupos_stats': grupos_stats[:5],    # Top 5 grupos
            'total_unidades': total_unidades,
        })
        
        return super().changelist_view(request, extra_context=extra_context)


# ========================================
# CAPTIVE PORTAL ADMIN SECTION
# ========================================

# PROXY MODELS MOVIDOS PARA painel/models.py




# class EldAdminModelAdmin(admin.ModelAdmin):
#     """
#     Admin personalizado para o ELD Admin
#     """
#     
#     def get_urls(self):
#         """
#         Sobrescreve as URLs para redirecionar para nossa view personalizada
#         """
#         urls = super().get_urls()
#         custom_urls = [
#             path('', self.admin_site.admin_view(self.eld_admin_view), name='painel_eldadminproxy_changelist'),
#         ]
#         return custom_urls + urls
#     
#     def eld_admin_view(self, request):
#         """
#         View personalizada que redireciona para nossa página principal do ELD
#         """
#         from django.shortcuts import redirect
#         return redirect('/admin/eld/')
#     
#     def has_add_permission(self, request):
#         return False
#     
#     def has_change_permission(self, request, obj=None):
#         return False
#     
#     def has_delete_permission(self, request, obj=None):
#         return False

# =====================================================================
# PROXY MODELS IMPORTADOS DO MODELS.PY
# =====================================================================
from .models import (
    GerenciarPortalProxy, ZipManagerProxy, NotificationsProxy, 
    PortalSemVideoProxy, UploadVideosProxy
)


# Admin para o modelo real EldUploadVideo (agora via proxy)
# @admin.register(EldUploadVideo) - REMOVIDO para usar proxy
class EldUploadVideoAdmin(admin.ModelAdmin):
    """
    Admin para visualizar e gerenciar uploads de vídeo ELD
    """
    list_display = ['id', 'get_video_name', 'data', 'tamanho_mb', 'get_video_link']
    list_filter = ['data']
    search_fields = ['video']
    readonly_fields = ['data', 'tamanho']
    ordering = ['-data', '-id']
    
    def get_video_name(self, obj):
        if obj.video:
            return obj.video.name.split('/')[-1]  # Apenas o nome do arquivo
        return "N/A"
    get_video_name.short_description = "Nome do Arquivo"
    
    def tamanho_mb(self, obj):
        return f"{obj.tamanho} MB"
    tamanho_mb.short_description = "Tamanho"
    
    def get_video_link(self, obj):
        if obj.video:
            return format_html('<a href="{}" target="_blank">▶️ Visualizar</a>', obj.video.url)
        return "N/A"
    get_video_link.short_description = "Visualizar"
    
    def changelist_view(self, request, extra_context=None):
        """
        Customiza a view da listagem para adicionar botão de upload
        """
        extra_context = extra_context or {}
        extra_context['upload_video_url'] = reverse('painel:eld_video_upload')
        return super().changelist_view(request, extra_context)
    
    def has_add_permission(self, request):
        # Usar a interface customizada para upload
        return False


# ========================================
# ADMIN PARA GERENCIAR PORTAL CAPTIVE
# ========================================

# Formulário customizado para Portal com Vídeo
class GerenciarPortalForm(forms.ModelForm):
    """
    Formulário customizado para esconder campos desnecessários no Portal com Vídeo
    """
    class Meta:
        model = EldGerenciarPortal
        fields = ['ativo', 'nome_video', 'captive_portal_zip']
        widgets = {
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EldGerenciarPortalAdmin(admin.ModelAdmin):
    """
    Admin personalizado para gerenciar as configurações do portal captive
    """
    form = GerenciarPortalForm
    
    list_display = [
        'status_display', 
        'video_selecionado', 
        'portal_zip_status',
        'data_atualizacao',
        'ativo'
    ]
    
    list_filter = [
        'ativo', 
        'data_criacao'
    ]
    
    search_fields = [
        'nome_video__nome',
        'nome_video__descricao'
    ]
    
    fields = [
        'ativo',
        'nome_video', 
        'captive_portal_zip',
        'status_info'
    ]
    
    readonly_fields = ['status_info']
    
    # Customizar o formulário
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Customizar o campo de seleção de vídeo
        """
        if db_field.name == "nome_video":
            # Mostrar apenas vídeos que estão disponíveis, ordenados por data
            try:
                kwargs["queryset"] = EldUploadVideo.objects.all().order_by('-data')
                kwargs["empty_label"] = "--- Selecione um vídeo ---"
            except Exception:
                # Fallback sem ordenação se houver erro
                kwargs["queryset"] = EldUploadVideo.objects.all()
                kwargs["empty_label"] = "--- Selecione um vídeo ---"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def status_display(self, obj):
        """
        Exibe o status do portal com vídeo
        """
        if not obj.ativo:
            return format_html(
                '<span style="color: #999;">⭕ Inativo</span>'
            )
        
        if obj.nome_video:
            return format_html(
                '<span style="color: #28a745;">✅ Ativo - Vídeo customizado</span>'
            )
        else:
            return format_html(
                '<span style="color: #17a2b8;">ℹ️ Ativo - Vídeo padrão (ZIP)</span>'
            )
    
    status_display.short_description = "Status"
    status_display.admin_order_field = 'ativo'
    
    def video_selecionado(self, obj):
        """
        Exibe o vídeo selecionado
        """
        if obj.nome_video:
            video_name = obj.nome_video.video.name if obj.nome_video.video else f"Vídeo {obj.nome_video.id}"
            return format_html(
                '<a href="{}" target="_blank">📹 {}</a>',
                obj.nome_video.video.url if obj.nome_video.video else '#',
                video_name
            )
        return format_html('<span style="color: #17a2b8;">🎥 Vídeo padrão (do ZIP)</span>')
    
    video_selecionado.short_description = "Vídeo"
    
    def portal_zip_status(self, obj):
        """
        Exibe o status do arquivo ZIP
        """
        if obj.captive_portal_zip:
            return format_html(
                '<a href="{}" target="_blank">📦 ZIP Disponível</a>',
                obj.captive_portal_zip.url
            )
        return format_html('<span style="color: #dc3545;">❌ Nenhum ZIP</span>')
    
    portal_zip_status.short_description = "Portal ZIP"
    
    def status_info(self, obj):
        """
        Informações detalhadas sobre o status da configuração
        """
        if not obj.pk:
            return "Configure os campos abaixo e salve para ver as informações de status."
        
        info_html = []
        
        # Status geral
        info_html.append(f"<h4>Status da Configuração:</h4>")
        info_html.append(f"<p><strong>Status:</strong> {obj.status_configuracao}</p>")
        
        # Informações do vídeo
        if obj.nome_video:
            info_html.append(f"<h4>Vídeo Customizado:</h4>")
            video_name = obj.nome_video.video.name if obj.nome_video.video else f"Vídeo {obj.nome_video.id}"
            info_html.append(f"<p><strong>Nome:</strong> {video_name}</p>")
            info_html.append(f"<p><strong>Tamanho:</strong> {obj.nome_video.tamanho}MB</p>")
            if obj.nome_video.video:
                info_html.append(f"<p><strong>URL do Vídeo:</strong> <a href='{obj.nome_video.video.url}' target='_blank'>{obj.nome_video.video.url}</a></p>")
        else:
            info_html.append(f"<h4>Vídeo Padrão:</h4>")
            info_html.append(f"<p style='color: #17a2b8;'><strong>ℹ️ Info:</strong> Usando vídeo padrão incluído no arquivo ZIP do portal.</p>")
            info_html.append(f"<p><strong>Nota:</strong> Para usar um vídeo customizado, faça upload de vídeos e selecione um na lista acima.</p>")
        
        # Informações do ZIP
        if obj.captive_portal_zip:
            info_html.append(f"<h4>Portal ZIP:</h4>")
            info_html.append(f"<p><strong>Arquivo:</strong> <a href='{obj.captive_portal_zip.url}' target='_blank'>{obj.captive_portal_zip.name}</a></p>")
        
        # URLs para Appliance POPPFIRE
        info_html.append(f"<h4>URLs para Appliance POPPFIRE:</h4>")
        video_url = obj.get_video_url()
        if video_url:
            info_html.append(f"<p><strong>URL do Vídeo:</strong> <code>{video_url}</code></p>")
        
        zip_url = obj.get_portal_zip_url()
        if zip_url:
            info_html.append(f"<p><strong>URL do ZIP:</strong> <code>{zip_url}</code></p>")
        
        return format_html(''.join(info_html))
    
    status_info.short_description = "Informações da Configuração"
    
    def save_model(self, request, obj, form, change):
        """
        Override para mostrar mensagens personalizadas e sempre ativar vídeo
        """
        try:
            # Verificar se houve mudança de vídeo
            video_changed = False
            old_video = None
            new_video = None
            
            if change and obj.pk:
                try:
                    old_instance = obj.__class__.objects.get(pk=obj.pk)
                    old_video = old_instance.nome_video
                    new_video = obj.nome_video
                    video_changed = old_video != new_video
                except obj.__class__.DoesNotExist:
                    pass
            
            # Como agora é sempre "Portal com Vídeo", sempre ativar o campo vídeo
            obj.ativar_video = True
            # Campo portal_sem_video não é usado no Portal com Vídeo
            obj.portal_sem_video = None
            
            super().save_model(request, obj, form, change)
            
            if obj.ativo:
                if obj.nome_video:
                    video_name = obj.nome_video.video.name if obj.nome_video.video else f"Vídeo {obj.nome_video.id}"
                    if video_changed and obj.captive_portal_zip:
                        messages.success(request, 
                            f'✅ Portal com Vídeo atualizado! Vídeo "{video_name}" foi substituído no arquivo ZIP e está ativo para o Appliance POPPFIRE.')
                    else:
                        messages.success(request, 
                            f'✅ Portal com Vídeo configurado! Vídeo customizado "{video_name}" está ativo e pronto para o Appliance POPPFIRE.')
                else:
                    messages.success(request,
                        '✅ Portal com Vídeo configurado! Usando vídeo padrão do ZIP.')
            else:
                messages.info(request, 'Portal salvo como inativo.')
                
        except Exception as e:
            messages.error(request, f'Erro ao salvar portal: {str(e)}')

    class Meta:
        verbose_name = "Configuração do Portal com Vídeo"
        verbose_name_plural = "Configurações do Portal com Vídeo"



# Formulário customizado para upload do portal sem vídeo
from django import forms
from .models import EldPortalSemVideo

class ImagePreviewWidget(forms.ClearableFileInput):
    """Widget customizado para mostrar preview da imagem"""
    template_name = 'admin/widgets/image_preview_widget.html'
    
    def format_value(self, value):
        if hasattr(value, 'url'):
            return {
                'url': value.url,
                'name': value.name,
            }
        return value

class PortalSemVideoUploadForm(forms.ModelForm):
    class Meta:
        model = EldPortalSemVideo
        fields = ['nome', 'versao', 'descricao', 'arquivo_zip', 'ativo', 'preview']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Portal Corporativo'}),
            'versao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1.0'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'arquivo_zip': forms.FileInput(attrs={'accept': '.zip', 'class': 'form-control'}),
            'preview': ImagePreviewWidget(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EldPortalSemVideoAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar portais sem vídeo
    """
    form = PortalSemVideoUploadForm
    list_display = ['nome', 'versao', 'status_display', 'tamanho_mb', 'data_atualizacao', 'preview_display', 'actions_display']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'versao', 'descricao']
    readonly_fields = ['tamanho_mb', 'data_criacao', 'data_atualizacao']
    ordering = ['-data_atualizacao']

    fields = [
        'ativo',
        'nome',
        'versao',
        'descricao',
        'arquivo_zip',
        'tamanho_mb',
        'preview',
        'data_criacao',
        'data_atualizacao'
    ]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload/', self.admin_site.admin_view(self.upload_portal_view), name='portal_sem_video_upload'),
            path('add/', self.admin_site.admin_view(self.upload_portal_view), name='painel_eldportalsemvideo_add'),
        ]
        return custom_urls + urls

    def upload_portal_view(self, request):
        from django.shortcuts import redirect
        
        # Detectar se está sendo acessado via captive_portal app
        is_captive_portal = 'captive_portal' in request.path
        template_name = 'admin/captive_portal/portalsemvideoproxy/add_form.html' if is_captive_portal else 'admin/painel/portalsemvideoproxy/upload_list.html'
        
        if request.method == 'POST':
            form = PortalSemVideoUploadForm(request.POST, request.FILES)
            print(f"Form data: {request.POST}")
            print(f"Files data: {request.FILES}")
            if form.is_valid():
                print("Form is valid, saving...")
                portal = form.save(commit=False)
                
                # Calcular tamanho do arquivo ZIP se foi fornecido
                if portal.arquivo_zip:
                    try:
                        portal.tamanho_mb = round(portal.arquivo_zip.size / (1024 * 1024), 2)
                        print(f"Calculated file size: {portal.tamanho_mb} MB")
                    except Exception as e:
                        print(f"Error calculating file size: {e}")
                        portal.tamanho_mb = 0.0
                
                portal.save()
                print(f"Portal saved: {portal}")
                messages.success(request, f'Portal sem vídeo cadastrado com sucesso! Tamanho: {portal.tamanho_mb}MB')
                return redirect('..')
            else:
                print(f"Form errors: {form.errors}")
                messages.error(request, f'Erro no formulário: {form.errors}')
        else:
            form = PortalSemVideoUploadForm()
        
        # Listagem dos portais cadastrados
        portais = EldPortalSemVideo.objects.all().order_by('-data_atualizacao')
        context = self.admin_site.each_context(request)
        context.update({
            'form': form,
            'portais': portais,
            'opts': self.model._meta,
            'title': 'Upload de Portal Sem Vídeo',
            'timestamp': int(__import__('time').time()),  # Para evitar cache
        })
        return render(request, template_name, context)

    def preview_display(self, obj):
        if hasattr(obj, 'preview') and obj.preview:
            return format_html('<img src="{}" style="max-width:120px; max-height:80px;" />', obj.preview.url)
        return '—'
    preview_display.short_description = 'Preview'

    def status_display(self, obj):
        if obj.ativo:
            return format_html('<span style="color: green; font-weight: bold;">✅ Ativo</span>')
        return format_html('<span style="color: #999;">⚪ Inativo</span>')
    status_display.short_description = "Status"

    def actions_display(self, obj):
        # 1) Preferir rota compatível sob /admin/captive_portal/ (serve via view, evita problemas de nome/espaco)
        try:
            # Primeiro tenta o padrão de proxy do Django Admin (portalsemvideoproxy)
            download_url = reverse('portal_sem_video_download_admin_compat_proxy', args=[obj.id])
        except Exception:
            # 2) Tentar rota sob o namespace admin/painel
            try:
                download_url = reverse('painel_admin:portal_sem_video_download_admin', args=[obj.id])
            except Exception:
                # 3) Tentar rota compat sob /admin/captive_portal/ (sem proxy)
                try:
                    download_url = reverse('portal_sem_video_download_admin_compat', args=[obj.id])
                except Exception:
                    # 4) Último fallback: URL direta do arquivo (MEDIA)
                if getattr(obj, 'arquivo_zip', None) and getattr(obj.arquivo_zip, 'url', None):
                    download_url = obj.arquivo_zip.url
                else:
                    download_url = '#'
        return format_html('<a href="{}" class="button" target="_blank">📥 Download</a>', download_url)
    actions_display.short_description = "Ações"

    def save_model(self, request, obj, form, change):
        try:
            # Calcular tamanho antes de salvar
            if obj.arquivo_zip:
                try:
                    obj.tamanho_mb = round(obj.arquivo_zip.size / (1024 * 1024), 2)
                except:
                    obj.tamanho_mb = 0.0
            
            super().save_model(request, obj, form, change)
            
            if obj.ativo:
                messages.success(request, f'✅ Portal "{obj.nome}" v{obj.versao} salvo e ativado! ({obj.tamanho_mb}MB)')
            else:
                messages.info(request, f'ℹ️ Portal "{obj.nome}" v{obj.versao} salvo como inativo. ({obj.tamanho_mb}MB)')
        except Exception as e:
            messages.error(request, f'Erro ao salvar portal: {str(e)}')

    def has_add_permission(self, request):
        return True


# ========================================
# ADMIN PARA ZIP MANAGER
# ========================================

class ZipManagerAdmin(admin.ModelAdmin):
    """
    Admin personalizado para o ZIP Manager
    """
    def get_urls(self):
        """
        Sobrescreve as URLs para redirecionar para o ZIP Manager
        """
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.zip_manager_view), name='painel_zipmanagerproxy_changelist'),
        ]
        return custom_urls + urls
    
    def zip_manager_view(self, request):
        """
        View personalizada que chama diretamente o ZIP Manager
        """
        from . import admin_views
        return admin_views.zip_manager_view(request)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ========================================
# ADMIN PARA NOTIFICAÇÕES
# ========================================

class NotificationsAdmin(admin.ModelAdmin):
    """
    Admin personalizado para o Sistema de Notificações
    """
    def get_urls(self):
        """
        Sobrescreve as URLs para redirecionar para as Notificações
        """
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.notifications_view), name='painel_notificationsproxy_changelist'),
        ]
        return custom_urls + urls
    
    def notifications_view(self, request):
        """
        View personalizada que chama diretamente o sistema de notificações
        """
        from . import admin_views
        return admin_views.test_notifications_view(request)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ========================================
# REGISTROS DOS MODELOS PROXY - CAPTIVE PORTAL
# ========================================

# MOVIDOS PARA captive_portal/admin.py PARA CORREÇÃO DE URLS
# Os proxy models com app_label='captive_portal' devem ser registrados lá
