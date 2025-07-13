from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.shortcuts import render, redirect
from .models import Radcheck, EldRegistroViewVideos, Unidades
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
        return redirect('/admin/starlink/')
    
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

@admin.register(EldRegistroViewVideos)
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
            path('grouped/', self.admin_site.admin_view(self.grouped_view), name='eldregistroviewvideos_grouped'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        # Redireciona para a view agrupada por padrão
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(reverse('admin:eldregistroviewvideos_grouped'))

    def grouped_view(self, request):
        # Lógica para agrupar os dados
        queryset = EldRegistroViewVideos.objects.all()
        
        # Agrupamento
        grouped_data = (
            queryset.annotate(day=TruncDay('date_view'))
            .values('username', 'video', 'day')
            .annotate(
                view_count=Count('id'),
                last_view=Max('date_view')
            )
            .order_by('-day', 'username')
        )

        context = dict(
           self.admin_site.each_context(request),
           title="Logs de Vídeos Agrupados por Dia",
           grouped_data=grouped_data,
           opts=self.model._meta,
           original_changelist_url=reverse('admin:painel_eldregistroviewvideos_changelist')
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
