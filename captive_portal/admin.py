from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.utils import timezone
from painel.models import (
    CaptivePortalProxy, LogsVideosProxy, UploadVideosProxy, 
    GerenciarPortalProxy, ZipManagerProxy, NotificationsProxy, PortalSemVideoProxy
)
from painel.admin import (
    EldRegistroViewVideosAdmin, EldUploadVideoAdmin,
    EldGerenciarPortalAdmin, ZipManagerAdmin, NotificationsAdmin, EldPortalSemVideoAdmin
)
from .models import ApplianceToken
import json
import os


@admin.register(ApplianceToken)
class ApplianceTokenAdmin(admin.ModelAdmin):
    """
    Admin interface para gerenciar tokens dos Appliances POPPFIRE
    """
    list_display = [
        'appliance_name', 
        'appliance_id', 
        'status_display_html',
        'token_preview',
        'last_used',
        'ip_address',
        'created_at',
        'actions_display'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
        'last_used'
    ]
    
    search_fields = [
        'appliance_name',
        'appliance_id',
        'description',
        'token'
    ]
    
    readonly_fields = [
        'token',
        'created_at',
        'updated_at',
        'last_used',
        'ip_address'
    ]
    
    fields = [
        'is_active',
        'appliance_id',
        'appliance_name',
        'description',
        'token',
        'created_at',
        'updated_at',
        'last_used',
        'ip_address'
    ]
    
    ordering = ['-created_at']
    
    def status_display_html(self, obj):
        """
        Exibe o status do token com formatação HTML
        """
        if not obj.is_active:
            return format_html('<span style="color: #dc3545;">🔴 Inativo</span>')
        elif obj.last_used:
            return format_html('<span style="color: #28a745;">🟢 Ativo</span>')
        else:
            return format_html('<span style="color: #ffc107;">🟡 Nunca usado</span>')
    
    status_display_html.short_description = "Status"
    status_display_html.admin_order_field = 'is_active'
    
    def token_preview(self, obj):
        """
        Mostra preview do token com botão para copiar
        """
        if obj.token:
            token_short = f"{obj.token[:8]}...{obj.token[-8:]}"
            return format_html(
                '<code>{}</code> <button type="button" onclick="navigator.clipboard.writeText(\'{}\'); alert(\'Token copiado!\');" title="Copiar token completo">📋</button>',
                token_short,
                obj.token
            )
        return "—"
    
    token_preview.short_description = "Token"
    
    def actions_display(self, obj):
        """
        Botões de ação para cada token
        """
        actions = []
        
        if obj.is_active:
            actions.append(
                f'<a href="javascript:void(0)" onclick="toggleToken({obj.id}, false)" class="button" style="color: #dc3545;">🔴 Desativar</a>'
            )
        else:
            actions.append(
                f'<a href="javascript:void(0)" onclick="toggleToken({obj.id}, true)" class="button" style="color: #28a745;">🟢 Ativar</a>'
            )
        
        actions.append(
            f'<a href="javascript:void(0)" onclick="regenerateToken({obj.id})" class="button" style="color: #17a2b8;">🔄 Regenerar</a>'
        )
        
        return format_html(' '.join(actions))
    
    actions_display.short_description = "Ações"
    
    def save_model(self, request, obj, form, change):
        """
        Salva o modelo e sincroniza com o arquivo JSON
        """
        super().save_model(request, obj, form, change)
        
        try:
            self.sync_to_json()
            if change:
                messages.success(request, f'Token do appliance "{obj.appliance_name}" atualizado com sucesso!')
            else:
                messages.success(request, f'Token do appliance "{obj.appliance_name}" criado com sucesso! Token: {obj.token}')
        except Exception as e:
            messages.error(request, f'Erro ao sincronizar com arquivo JSON: {e}')
    
    def delete_model(self, request, obj):
        """
        Remove o modelo e sincroniza com o arquivo JSON
        """
        appliance_name = obj.appliance_name
        super().delete_model(request, obj)
        
        try:
            self.sync_to_json()
            messages.success(request, f'Token do appliance "{appliance_name}" removido com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao sincronizar com arquivo JSON: {e}')
    
    def sync_to_json(self):
        """
        Sincroniza os tokens do banco de dados com o arquivo JSON
        """
        from django.conf import settings
        
        tokens_file = os.path.join(settings.BASE_DIR, 'appliance_tokens.json')
        
        # Buscar todos os tokens ativos
        active_tokens = ApplianceToken.objects.filter(is_active=True)
        
        tokens_data = {
            "generated_at": timezone.now().isoformat(),
            "total_tokens": active_tokens.count(),
            "tokens": {}
        }
        
        for token_obj in active_tokens:
            tokens_data["tokens"][token_obj.token] = {
                "appliance_id": token_obj.appliance_id,
                "appliance_name": token_obj.appliance_name,
                "description": token_obj.description or "",
                "created_at": token_obj.created_at.isoformat(),
                "last_used": token_obj.last_used.isoformat() if token_obj.last_used else None,
                "ip_address": token_obj.ip_address
            }
        
        # Salvar no arquivo JSON
        with open(tokens_file, 'w', encoding='utf-8') as f:
            json.dump(tokens_data, f, indent=4, ensure_ascii=False)
    
    def changelist_view(self, request, extra_context=None):
        """
        Adiciona contexto extra para a listagem
        """
        extra_context = extra_context or {}
        
        # Estatísticas
        total_tokens = ApplianceToken.objects.count()
        active_tokens = ApplianceToken.objects.filter(is_active=True).count()
        used_tokens = ApplianceToken.objects.filter(last_used__isnull=False).count()
        
        extra_context.update({
            'total_tokens': total_tokens,
            'active_tokens': active_tokens,
            'used_tokens': used_tokens,
            'unused_tokens': active_tokens - used_tokens
        })
        
        return super().changelist_view(request, extra_context)
    
    class Media:
        js = ('admin/js/appliance_tokens.js',)


# Registrar os proxy models no app captive_portal
admin.site.register(LogsVideosProxy, EldRegistroViewVideosAdmin)
admin.site.register(UploadVideosProxy, EldUploadVideoAdmin)
admin.site.register(GerenciarPortalProxy, EldGerenciarPortalAdmin)
admin.site.register(ZipManagerProxy, ZipManagerAdmin)
admin.site.register(NotificationsProxy, NotificationsAdmin)
admin.site.register(PortalSemVideoProxy, EldPortalSemVideoAdmin)
