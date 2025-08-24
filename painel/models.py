# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AdminInterfaceTheme(models.Model):
    name = models.CharField(unique=True, max_length=50)
    active = models.BooleanField()
    title = models.CharField(max_length=50)
    title_visible = models.BooleanField()
    logo = models.CharField(max_length=100)
    logo_visible = models.BooleanField()
    css_header_background_color = models.CharField(max_length=10)
    title_color = models.CharField(max_length=10)
    css_header_text_color = models.CharField(max_length=10)
    css_header_link_color = models.CharField(max_length=10)
    css_header_link_hover_color = models.CharField(max_length=10)
    css_module_background_color = models.CharField(max_length=10)
    css_module_text_color = models.CharField(max_length=10)
    css_module_link_color = models.CharField(max_length=10)
    css_module_link_hover_color = models.CharField(max_length=10)
    css_module_rounded_corners = models.BooleanField()
    css_generic_link_color = models.CharField(max_length=10)
    css_generic_link_hover_color = models.CharField(max_length=10)
    css_save_button_background_color = models.CharField(max_length=10)
    css_save_button_background_hover_color = models.CharField(max_length=10)
    css_save_button_text_color = models.CharField(max_length=10)
    css_delete_button_background_color = models.CharField(max_length=10)
    css_delete_button_background_hover_color = models.CharField(max_length=10)
    css_delete_button_text_color = models.CharField(max_length=10)
    list_filter_dropdown = models.BooleanField()
    related_modal_active = models.BooleanField()
    related_modal_background_color = models.CharField(max_length=10)
    related_modal_rounded_corners = models.BooleanField()
    logo_color = models.CharField(max_length=10)
    recent_actions_visible = models.BooleanField()
    favicon = models.CharField(max_length=100)
    related_modal_background_opacity = models.CharField(max_length=5)
    env_name = models.CharField(max_length=50)
    env_visible_in_header = models.BooleanField()
    env_color = models.CharField(max_length=10)
    env_visible_in_favicon = models.BooleanField()
    related_modal_close_button_visible = models.BooleanField()
    language_chooser_active = models.BooleanField()
    language_chooser_display = models.CharField(max_length=10)
    list_filter_sticky = models.BooleanField()
    form_pagination_sticky = models.BooleanField()
    form_submit_sticky = models.BooleanField()
    css_module_background_selected_color = models.CharField(max_length=10)
    css_module_link_selected_color = models.CharField(max_length=10)
    logo_max_height = models.SmallIntegerField()
    logo_max_width = models.SmallIntegerField()
    foldable_apps = models.BooleanField()
    language_chooser_control = models.CharField(max_length=20)
    list_filter_highlight = models.BooleanField()
    list_filter_removal_links = models.BooleanField()
    show_fieldsets_as_tabs = models.BooleanField()
    show_inlines_as_tabs = models.BooleanField()
    css_generic_link_active_color = models.CharField(max_length=10)
    collapsible_stacked_inlines = models.BooleanField()
    collapsible_stacked_inlines_collapsed = models.BooleanField()
    collapsible_tabular_inlines = models.BooleanField()
    collapsible_tabular_inlines_collapsed = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'admin_interface_theme'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class ConsumoFranquiaUnidades(models.Model):
    host = models.CharField(max_length=100)
    data = models.DateField()
    consumo = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'consumo_franquia_unidades'


class ConsumoFranquiaUnidades2(models.Model):
    servicelinenumber = models.CharField(max_length=255, blank=True, null=True)
    data = models.DateField(blank=True, null=True)
    consumo_priority = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    consumo_standard = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consumo_franquia_unidades2'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Nas(models.Model):
    nasname = models.TextField()
    shortname = models.TextField()
    type = models.TextField()
    ports = models.IntegerField(blank=True, null=True)
    secret = models.TextField()
    server = models.TextField(blank=True, null=True)
    community = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nas'


class Nasreload(models.Model):
    nasipaddress = models.GenericIPAddressField(primary_key=True)
    reloadtime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'nasreload'


class Radacct(models.Model):
    radacctid = models.BigAutoField(primary_key=True)
    acctsessionid = models.TextField()
    acctuniqueid = models.TextField(unique=True)
    username = models.TextField(blank=True, null=True)
    realm = models.TextField(blank=True, null=True)
    nasipaddress = models.GenericIPAddressField()
    nasportid = models.TextField(blank=True, null=True)
    nasporttype = models.TextField(blank=True, null=True)
    acctstarttime = models.DateTimeField(blank=True, null=True)
    acctupdatetime = models.DateTimeField(blank=True, null=True)
    acctstoptime = models.DateTimeField(blank=True, null=True)
    acctinterval = models.BigIntegerField(blank=True, null=True)
    acctsessiontime = models.BigIntegerField(blank=True, null=True)
    acctauthentic = models.TextField(blank=True, null=True)
    connectinfo_start = models.TextField(blank=True, null=True)
    connectinfo_stop = models.TextField(blank=True, null=True)
    acctinputoctets = models.BigIntegerField(blank=True, null=True)
    acctoutputoctets = models.BigIntegerField(blank=True, null=True)
    calledstationid = models.TextField(blank=True, null=True)
    callingstationid = models.TextField(blank=True, null=True)
    acctterminatecause = models.TextField(blank=True, null=True)
    servicetype = models.TextField(blank=True, null=True)
    framedprotocol = models.TextField(blank=True, null=True)
    framedipaddress = models.GenericIPAddressField(blank=True, null=True)
    framedipv6address = models.GenericIPAddressField(blank=True, null=True)
    framedipv6prefix = models.GenericIPAddressField(blank=True, null=True)
    framedinterfaceid = models.TextField(blank=True, null=True)
    delegatedipv6prefix = models.GenericIPAddressField(blank=True, null=True)
    class_field = models.TextField(db_column='class', blank=True, null=True)  # Field renamed because it was a Python reserved word.

    class Meta:
        managed = False
        db_table = 'radacct'


class Radcheck(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64, verbose_name='Usuário', help_text='Nome do usuário')
    attribute = models.CharField(max_length=64, verbose_name='Atributo', help_text='Tipo de atributo (ex: Cleartext-Password)')
    op = models.CharField(max_length=2, verbose_name='Operador', help_text='Operador de comparação', 
                         choices=[
                             ('==', 'Igual (==)'),
                             ('!=', 'Diferente (!=)'),
                             (':=', 'Atribuir (:=)'),
                             ('+=', 'Adicionar (+=)'),
                             ('=~', 'Regex Match (=~)'),
                             ('!~', 'Regex Not Match (!~)'),
                         ], default=':=')
    value = models.CharField(max_length=253, verbose_name='Valor', help_text='Valor do atributo')

    class Meta:
        managed = False
        db_table = 'radcheck'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class Radcheck2(models.Model):
    username = models.TextField()
    attribute = models.TextField()
    op = models.CharField(max_length=2)
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'radcheck2'


class Radgroupcheck(models.Model):
    groupname = models.TextField()
    attribute = models.TextField()
    op = models.CharField(max_length=2)
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'radgroupcheck'


class Radgroupreply(models.Model):
    groupname = models.TextField()
    attribute = models.TextField()
    op = models.CharField(max_length=2)
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'radgroupreply'


class Radpostauth(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.TextField()
    pass_field = models.TextField(db_column='pass', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    reply = models.TextField(blank=True, null=True)
    calledstationid = models.TextField(blank=True, null=True)
    callingstationid = models.TextField(blank=True, null=True)
    authdate = models.DateTimeField()
    class_field = models.TextField(db_column='class', blank=True, null=True)  # Field renamed because it was a Python reserved word.

    class Meta:
        managed = False
        db_table = 'radpostauth'


class Radreply(models.Model):
    username = models.TextField()
    attribute = models.TextField()
    op = models.CharField(max_length=2)
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'radreply'


class Radusergroup(models.Model):
    username = models.TextField()
    groupname = models.TextField()
    priority = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'radusergroup'


class Unidades(models.Model):
    id = models.AutoField(primary_key=True)
    designacao = models.CharField(max_length=255, verbose_name='Designação', blank=True, null=True)
    kit = models.CharField(max_length=255, verbose_name='Kit', blank=True, null=True)
    sigla = models.CharField(max_length=255, verbose_name='Sigla', blank=True, null=True)
    grupo_empresa = models.CharField(max_length=255, verbose_name='Grupo Empresa', blank=True, null=True)
    negocio_faturamento = models.CharField(max_length=255, verbose_name='Negócio Faturamento', blank=True, null=True)
    nome_empresa = models.CharField(max_length=255, verbose_name='Nome da Empresa', blank=True, null=True)
    estado_filial = models.CharField(max_length=255, verbose_name='Estado da Filial', blank=True, null=True)
    cidade_filial = models.CharField(max_length=255, verbose_name='Cidade da Filial', blank=True, null=True)
    endereco = models.CharField(max_length=255, verbose_name='Endereço', blank=True, null=True)
    cep = models.CharField(max_length=255, verbose_name='CEP', blank=True, null=True)
    data_ativacao = models.CharField(max_length=255, verbose_name='Data de Ativação', blank=True, null=True)
    servicelinenumber = models.CharField(max_length=255, verbose_name='Service Line Number', blank=True, null=True)
    email = models.CharField(max_length=255, verbose_name='Email', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'unidades'
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'
        
    def __str__(self):
        return f"{self.designacao} - {self.sigla}" if self.designacao else f"Unidade {self.id}"


class EldRegistroViewVideos(models.Model):
    username = models.CharField(max_length=255)
    video = models.CharField(max_length=255)
    date_view = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'eld_registro_view_videos'
        verbose_name = 'Log de Vídeo Assistido'
        verbose_name_plural = 'Logs de Vídeos Assistidos'

    def __str__(self):
        return f"{self.username} - {self.video}"


class StarlinkAdminProxy(models.Model):
    """
    Modelo fictício para criar o menu Starlink Admin no Django Admin
    """
    
    class Meta:
        verbose_name = "Starlink Admin"
        verbose_name_plural = "Starlink Admin"
        managed = False  # Não cria tabela no banco
        app_label = 'painel'


class EldUploadVideo(models.Model):
    """
    Model para uploads de vídeos do sistema ELD
    """
    id = models.AutoField(primary_key=True)
    video = models.FileField(
        upload_to='videos/eld/',
        max_length=255,
        help_text='Arquivo de vídeo (máximo 5MB)'
    )
    data = models.DateField(
        auto_now_add=True,
        help_text='Data do upload'
    )
    tamanho = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Tamanho do arquivo em MB'
    )
    
    class Meta:
        db_table = 'eld_upload_videos'
        verbose_name = 'Upload de Vídeo ELD'
        verbose_name_plural = 'Uploads de Vídeos ELD'
        ordering = ['-data', '-id']
    
    def __str__(self):
        return f"Vídeo {self.id} - {self.video.name} ({self.tamanho}MB)"
    
    def save(self, *args, **kwargs):
        # Verificar se é um novo registro
        is_new = self.pk is None
        
        # Calcular tamanho do arquivo em MB
        if self.video:
            self.tamanho = round(self.video.size / (1024 * 1024), 2)
        
        super().save(*args, **kwargs)
        
        # Enviar notificações apenas para novos uploads
        if is_new and self.video:
            # Importar aqui para evitar circular imports
            from .services import NotificationService, ZipManagerService
            from django.contrib.auth.models import User
            import threading
            
            def send_notifications():
                """Enviar notificações em thread separada"""
                try:
                    # Obter usuário do request (se disponível)
                    user = None
                    
                    # Enviar notificações
                    NotificationService.send_email_notification(self.video, user)
                    NotificationService.send_telegram_notification(self.video, user)
                    
                    # Buscar configuração ativa do portal para atualizar ZIP
                    from .models import EldGerenciarPortal
                    try:
                        portal_config = EldGerenciarPortal.objects.filter(ativo=True).first()
                        if portal_config and portal_config.captive_portal_zip:
                            zip_path = portal_config.captive_portal_zip.path
                            ZipManagerService.update_zip_with_video(zip_path, self.video)
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Erro ao atualizar ZIP: {str(e)}")
                        
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Erro ao enviar notificações: {str(e)}")
            
            # Executar notificações em thread separada para não bloquear o save
            thread = threading.Thread(target=send_notifications)
            thread.start()


class EldGerenciarPortal(models.Model):
    """
    Modelo para gerenciar a configuração do portal captive
    Controla qual vídeo será exibido e o arquivo ZIP do portal
    """
    
    # Campo para ativar/desativar a exibição de vídeo
    ativar_video = models.BooleanField(
        default=False,
        verbose_name="Ativar Vídeo",
        help_text="Ativar para permitir que o Appliance POPPFIRE baixe e exiba vídeos no portal captive"
    )
    
    # Campo para selecionar qual vídeo será exibido
    nome_video = models.ForeignKey(
        'EldUploadVideo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Vídeo Selecionado",
        help_text="Selecione o vídeo que será exibido no portal captive",
        related_name='portal_configurations'
    )
    
    # Campo para armazenar o arquivo ZIP do portal captive
    captive_portal_zip = models.FileField(
        upload_to='captive_portal_zips/',
        null=True,
        blank=True,
        verbose_name="Arquivo ZIP do Portal (com vídeo)",
        help_text="Upload do arquivo .zip contendo os arquivos do portal captive (src.zip)"
    )
    
    # Campo para selecionar portal sem vídeo
    portal_sem_video = models.ForeignKey(
        'EldPortalSemVideo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Portal sem Vídeo",
        help_text="Portal usado quando vídeo estiver desativado (scripts_poppnet_sre.zip)",
        related_name='configuracoes_portal'
    )
    
    # Campos de controle
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Configuração Ativa",
        help_text="Apenas uma configuração pode estar ativa por vez"
    )

    class Meta:
        db_table = 'eld_gerenciar_portal'
        verbose_name = "Configuração do Portal Captive"
        verbose_name_plural = "Configurações do Portal Captive"
        ordering = ['-data_atualizacao']

    def __str__(self):
        if self.nome_video:
            video_nome = self.nome_video.video.name if self.nome_video.video else f"Vídeo {self.nome_video.id}"
        else:
            video_nome = "Nenhum vídeo selecionado"
        status = "✅ Ativo" if self.ativo else "❌ Inativo"
        return f"Portal com Vídeo - {status} | {video_nome}"

    def clean(self):
        """
        Validações personalizadas do modelo - Portal com Vídeo
        """
        from django.core.exceptions import ValidationError
        super().clean()
        
        # Para Portal com Vídeo, sempre ativar_video deve ser True
        if not self.ativar_video:
            self.ativar_video = True
        
        # Arquivo ZIP do portal é obrigatório
        if not self.captive_portal_zip:
            raise ValidationError({
                'captive_portal_zip': 'Você deve fazer upload do arquivo ZIP do portal.'
            })
        
        # Garantir que apenas uma configuração esteja ativa
        if self.ativo:
            # Verificar se já existe outra configuração ativa
            existing_active = EldGerenciarPortal.objects.filter(ativo=True)
            if self.pk:
                existing_active = existing_active.exclude(pk=self.pk)
            
            if existing_active.exists():
                raise ValidationError({
                    'ativo': 'Apenas uma configuração pode estar ativa por vez. '
                           'Desative a configuração atual primeiro.'
                })

    def save(self, *args, **kwargs):
        """
        Override do save para aplicar validações, substituir vídeo no ZIP e gerenciar ativação automática
        """
        # Verificar se é uma atualização com mudança de vídeo
        is_video_change = False
        old_video = None
        
        # Verificar se está sendo ativado e precisa desativar portal sem vídeo
        activating_portal = self.ativo and (not self.pk or not EldGerenciarPortal.objects.filter(pk=self.pk, ativo=True).exists())
        
        if self.pk:
            try:
                old_instance = EldGerenciarPortal.objects.get(pk=self.pk)
                old_video = old_instance.nome_video
                is_video_change = old_video != self.nome_video
            except EldGerenciarPortal.DoesNotExist:
                pass
        
        self.clean()
        super().save(*args, **kwargs)
        
        # Se este portal com vídeo foi ativado, desativar automaticamente portal sem vídeo
        if activating_portal:
            try:
                portais_sem_video = EldPortalSemVideo.objects.filter(ativo=True)
                if portais_sem_video.exists():
                    portais_sem_video.update(ativo=False)
                    print(f"[AUTO-SWITCH] Portal com vídeo ativado - Portal sem vídeo desativado automaticamente")
            except Exception as e:
                print(f"[ERRO] Falha ao desativar portal sem vídeo: {e}")
        
        # Se houve mudança de vídeo e temos um ZIP, substituir o vídeo dentro do ZIP
        if is_video_change and self.captive_portal_zip and self.nome_video:
            self._substitute_video_in_zip()
    
    def _substitute_video_in_zip(self):
        """
        Substitui o vídeo dentro do arquivo ZIP na pasta src/assets/videos
        """
        import os
        import zipfile
        import tempfile
        import shutil
        from django.core.files.base import ContentFile
        
        try:
            # Caminho do arquivo ZIP atual
            zip_path = self.captive_portal_zip.path
            
            if not os.path.exists(zip_path):
                print(f"[ERRO] Arquivo ZIP não encontrado: {zip_path}")
                return
            
            # Caminho do novo vídeo
            if not self.nome_video or not self.nome_video.video:
                print("[ERRO] Nenhum vídeo selecionado para substituição")
                return
                
            video_path = self.nome_video.video.path
            if not os.path.exists(video_path):
                print(f"[ERRO] Arquivo de vídeo não encontrado: {video_path}")
                return
            
            print(f"[INFO] Iniciando substituição de vídeo no ZIP...")
            print(f"[INFO] ZIP: {zip_path}")
            print(f"[INFO] Novo vídeo: {video_path}")
            
            # Criar diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_zip_path = os.path.join(temp_dir, "temp_portal.zip")
                
                # Abrir ZIP original e criar novo ZIP temporário
                with zipfile.ZipFile(zip_path, 'r') as original_zip:
                    with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                        
                        # Copiar todos os arquivos exceto vídeos antigos na pasta src/assets/videos
                        for item in original_zip.infolist():
                            # Pular arquivos de vídeo na pasta src/assets/videos
                            if item.filename.startswith('src/assets/videos/') and item.filename.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv')):
                                print(f"[INFO] Removendo vídeo antigo: {item.filename}")
                                continue
                            
                            # Copiar outros arquivos
                            data = original_zip.read(item.filename)
                            new_zip.writestr(item, data)
                        
                        # Adicionar o novo vídeo na pasta src/assets/videos
                        video_filename = os.path.basename(video_path)
                        zip_video_path = f"src/assets/videos/{video_filename}"
                        
                        with open(video_path, 'rb') as video_file:
                            new_zip.writestr(zip_video_path, video_file.read())
                        
                        print(f"[INFO] Novo vídeo adicionado: {zip_video_path}")
                        
                        # Adicionar selected_video.txt para override automático
                        try:
                            selected_video_txt = f"src/assets/videos/selected_video.txt"
                            new_zip.writestr(selected_video_txt, video_filename.encode('utf-8'))
                            print(f"[INFO] selected_video.txt criado com: {video_filename}")
                        except Exception as e:
                            print(f"[AVISO] Falha ao criar selected_video.txt: {e}")
                
                # Agora precisamos extrair temporariamente para corrigir HTMLs e recomprimir
                extract_temp = os.path.join(temp_dir, "extracted")
                with zipfile.ZipFile(temp_zip_path, 'r') as extract_zip:
                    extract_zip.extractall(extract_temp)
                
                # Ajustar HTMLs com nome do vídeo correto
                self._patch_html_video_references(extract_temp, video_filename)
                
                # Recompactar com HTMLs corrigidos
                final_zip_path = os.path.join(temp_dir, "final_portal.zip")
                with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as final_zip:
                    for root, _, files in os.walk(extract_temp):
                        for file in files:
                            file_path = os.path.join(root, file)
                            archive_name = os.path.relpath(file_path, extract_temp)
                            final_zip.write(file_path, archive_name)
                
                # Substituir o arquivo ZIP original
                shutil.move(final_zip_path, zip_path)
                print(f"[SUCESSO] Vídeo substituído e HTMLs atualizados no ZIP!")
                
        except Exception as e:
            print(f"[ERRO] Falha ao substituir vídeo no ZIP: {str(e)}")
            import traceback
            traceback.print_exc()

    def _patch_html_video_references(self, extract_dir, video_filename):
        """
        Atualiza referências de vídeo em arquivos HTML dentro do diretório extraído
        """
        import re
        import os
        
        # HTMLs que precisam ser atualizados
        html_files = ['src/index.html', 'src/login.html', 'src/login2.html']
        
        for html_file in html_files:
            file_path = os.path.join(extract_dir, html_file)
            if not os.path.exists(file_path):
                continue
                
            try:
                # Ler conteúdo atual
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                
                # Atualizar tag <source src="assets/videos/...">
                pattern = r'(<source\b[^>]*\bsrc=["\']assets/videos/)([^"\']+)(["\'][^>]*>)'
                content, n = re.subn(pattern, r'\1' + video_filename + r'\3', content, count=1)
                
                # Fallback: substituir referências diretas de eldNN.mp4
                if n == 0:
                    content = re.sub(r'assets/videos/eld\d+\.mp4', f'assets/videos/{video_filename}', content, count=1)
                    if content != original_content:
                        n = 1
                
                # Atualizar poster se existir (tentativa de mesma base)
                base_no_ext = os.path.splitext(video_filename)[0]
                for ext in ['.jpg', '.png']:
                    poster_file = f'assets/videos/{base_no_ext}{ext}'
                    poster_path = os.path.join(extract_dir, 'src', 'assets', 'videos', f'{base_no_ext}{ext}')
                    
                    # Se o poster existir, atualizar referência
                    if os.path.exists(poster_path):
                        content, n_poster = re.subn(
                            r'(poster=["\']assets/videos/)([^"\']+)(["\'])', 
                            r'\1' + base_no_ext + ext + r'\3', 
                            content, count=1
                        )
                        if n_poster == 0:
                            # Fallback para eldNN.jpg/png
                            content = re.sub(
                                r'poster=["\']assets/videos/eld\d+\.(jpg|png)["\']', 
                                f'poster="assets/videos/{base_no_ext}{ext}"', 
                                content, count=1
                            )
                        break
                
                # Gravar se houve mudanças
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"[INFO] {html_file} atualizado para usar vídeo {video_filename}")
                
            except Exception as e:
                print(f"[AVISO] Falha ao atualizar {html_file}: {e}")

    def get_video_url(self):
        """
        Retorna a URL do vídeo selecionado para o Appliance POPPFIRE
        """
        if self.nome_video:
            return self.nome_video.video.url
        return None

    def get_portal_zip_url(self):
        """
        Retorna a URL do arquivo ZIP do Portal com Vídeo
        """
        if self.captive_portal_zip:
            return self.captive_portal_zip.url
        return None
    
    def get_portal_zip_path(self):
        """
        Retorna o caminho físico do arquivo ZIP do Portal com Vídeo
        """
        if self.captive_portal_zip:
            return self.captive_portal_zip.path
        return None
    
    def get_portal_zip_name(self):
        """
        Retorna o nome do arquivo ZIP para download (sempre src.zip para Portal com Vídeo)
        """
        return "src.zip"

    @property
    def status_configuracao(self):
        """
        Retorna o status da configuração em formato legível - Portal com Vídeo
        """
        if not self.ativo:
            return "Inativo"
        
        if self.nome_video:
            video_name = self.nome_video.video.name if self.nome_video.video else f"Vídeo {self.nome_video.id}"
            return f"Ativo - Vídeo customizado: {video_name}"
        else:
            return "Ativo - Vídeo padrão (do ZIP)"

    @classmethod
    def get_configuracao_ativa(cls):
        """
        Retorna a configuração ativa atual
        """
        try:
            return cls.objects.get(ativo=True)
        except cls.DoesNotExist:
            return None
        except cls.MultipleObjectsReturned:
            # Se houver múltiplas configurações ativas (não deveria acontecer),
            # retorna a mais recente e desativa as outras
            configs = cls.objects.filter(ativo=True).order_by('-data_atualizacao')
            config_ativa = configs.first()
            configs.exclude(pk=config_ativa.pk).update(ativo=False)
            return config_ativa


class EldPortalSemVideo(models.Model):
    """
    Modelo para gerenciar portais captive sem vídeo institucional
    Armazena o arquivo scripts_poppnet_sre.zip
    """
    
    nome = models.CharField(
        max_length=255,
        verbose_name="Nome do Portal",
        help_text="Nome descritivo para este portal"
    )
    
    arquivo_zip = models.FileField(
        upload_to='portal_sem_video/',
        verbose_name="Arquivo ZIP",
        help_text="Arquivo ZIP do portal sem vídeo (scripts_poppnet_sre.zip)"
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição do portal e suas características"
    )
    
    versao = models.CharField(
        max_length=50,
        verbose_name="Versão",
        help_text="Versão do portal (ex: 1.0, 2.1)"
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )
    
    ativo = models.BooleanField(
        default=False,
        verbose_name="Portal Ativo",
        help_text="Marcar como portal padrão para uso sem vídeo"
    )
    
    tamanho_mb = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Tamanho (MB)",
        help_text="Tamanho do arquivo ZIP em MB"
    )
    
    preview = models.ImageField(
        upload_to='portais_sem_video/previews/',
        blank=True,
        null=True,
        verbose_name='Preview do Portal',
        help_text="Imagem de preview/screenshot do portal"
    )

    def save(self, *args, **kwargs):
        # Calcular tamanho do arquivo ZIP
        if self.arquivo_zip:
            try:
                self.tamanho_mb = round(self.arquivo_zip.size / (1024 * 1024), 2)
            except:
                self.tamanho_mb = 0.0
        
        # Salvar primeiro para ter o arquivo disponível
        super().save(*args, **kwargs)
        
        # Redimensionar a imagem de preview se foi fornecida
        if self.preview:
            self._resize_preview()
    
    def _resize_preview(self):
        """Redimensiona a imagem de preview para um tamanho otimizado"""
        try:
            from PIL import Image
            import os
            from django.conf import settings
            
            # Caminho completo para a imagem
            image_path = os.path.join(settings.MEDIA_ROOT, self.preview.name)
            
            # Abrir e redimensionar
            with Image.open(image_path) as img:
                # Converter para RGB se necessário (para PNG com transparência)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Redimensionar mantendo proporção (máximo 400x300)
                img.thumbnail((400, 300), Image.Resampling.LANCZOS)
                
                # Salvar com qualidade otimizada
                img.save(image_path, 'JPEG', quality=85, optimize=True)
                
        except Exception as e:
            # Log do erro mas não falha o save
            print(f"Erro ao redimensionar preview: {e}")
    
    class Meta:
        db_table = 'eld_portal_sem_video'
        verbose_name = "Portal sem Vídeo"
        verbose_name_plural = "Portais sem Vídeo"
        ordering = ['-data_atualizacao']
    
    def __str__(self):
        status = "✅ Ativo" if self.ativo else "⚪ Inativo"
        return f"{self.nome} v{self.versao} - {status}"
    
    def clean(self):
        """Validações personalizadas"""
        from django.core.exceptions import ValidationError
        super().clean()
        
        # Garantir que apenas um portal esteja ativo
        if self.ativo:
            existing_active = EldPortalSemVideo.objects.filter(ativo=True)
            if self.pk:
                existing_active = existing_active.exclude(pk=self.pk)
            
            if existing_active.exists():
                raise ValidationError({
                    'ativo': 'Apenas um portal sem vídeo pode estar ativo por vez.'
                })
        
        # Validar nome do arquivo
        if self.arquivo_zip:
            filename = self.arquivo_zip.name.lower()
            if not filename.endswith('.zip'):
                raise ValidationError({
                    'arquivo_zip': 'O arquivo deve ter extensão .zip'
                })
    
    def save(self, *args, **kwargs):
        """Override do save para calcular tamanho, sanear nome do arquivo e gerenciar ativação automática."""
        # Verificar se está sendo ativado e precisa desativar portal com vídeo
        activating_portal = self.ativo and (not self.pk or not EldPortalSemVideo.objects.filter(pk=self.pk, ativo=True).exists())
        
        # Calcular tamanho do arquivo em MB
        if self.arquivo_zip:
            try:
                self.tamanho_mb = round(self.arquivo_zip.size / (1024 * 1024), 2)
            except Exception:
                pass

            # Sanear nome do arquivo (remover espaços extras e normalizar)
            try:
                import os, re
                current = getattr(self.arquivo_zip, 'name', '') or ''
                if current:
                    dir_name = os.path.dirname(current) or 'portal_sem_video'
                    base = os.path.basename(current)
                    name, ext = os.path.splitext(base)
                    # trim, colapsar espaços em '_', manter apenas caracteres seguros básicos
                    cleaned_name = re.sub(r'\s+', '_', name.strip())
                    cleaned_name = re.sub(r'[^A-Za-z0-9_\-\.]+', '', cleaned_name) or 'portal_sem_video'
                    cleaned_ext = ext if ext else '.zip'
                    safe_base = f"{cleaned_name}{cleaned_ext}"
                    safe_name = os.path.join(dir_name, safe_base)
                    if safe_name != current:
                        self.arquivo_zip.name = safe_name
            except Exception:
                pass

        self.clean()
        super().save(*args, **kwargs)
        
        # Se este portal sem vídeo foi ativado, desativar automaticamente portal com vídeo
        if activating_portal:
            try:
                # Importar aqui para evitar importação circular
                from . import models as painel_models
                portais_com_video = painel_models.EldGerenciarPortal.objects.filter(ativo=True)
                if portais_com_video.exists():
                    portais_com_video.update(ativo=False)
                    print(f"[AUTO-SWITCH] Portal sem vídeo '{self.nome}' ativado - Portal com vídeo desativado automaticamente")
            except Exception as e:
                print(f"[ERRO] Falha ao desativar portal com vídeo: {e}")
    
    @classmethod
    def get_portal_ativo(cls):
        """Retorna o portal sem vídeo ativo"""
        try:
            return cls.objects.get(ativo=True)
        except cls.DoesNotExist:
            return None
        except cls.MultipleObjectsReturned:
            # Se houver múltiplos ativos, retorna a mais recente
            portais = cls.objects.filter(ativo=True).order_by('-data_atualizacao')
            portal_ativo = portais.first()
            portais.exclude(pk=portal_ativo.pk).update(ativo=False)
            return portal_ativo


# =====================================================================
# PROXY MODELS PARA ORGANIZAR MENU ADMINISTRATIVO
# =====================================================================

class GerenciarPortalProxy(EldGerenciarPortal):
    """
    Proxy model para o menu Gerenciar Portal com Vídeo
    """
    class Meta:
        proxy = True
        verbose_name = "Gerenciar Portal com Vídeo"
        verbose_name_plural = "Gerenciar Portal com Vídeo"
        app_label = 'captive_portal'


class ZipManagerProxy(EldGerenciarPortal):
    """
    Proxy model para gerenciar arquivos ZIP do portal
    """
    class Meta:
        proxy = True
        verbose_name = "Gerenciar ZIP Portal"
        verbose_name_plural = "Gerenciar ZIP Portal"
        app_label = 'captive_portal'


class NotificationsProxy(EldGerenciarPortal):
    """
    Proxy model para sistema de notificações
    """
    class Meta:
        proxy = True
        verbose_name = "Sistema de Notificações"
        verbose_name_plural = "Sistema de Notificações"
        app_label = 'captive_portal'


class PortalSemVideoProxy(EldPortalSemVideo):
    """
    Proxy model para portais sem vídeo
    """
    class Meta:
        proxy = True
        verbose_name = "Portal sem Vídeo"
        verbose_name_plural = "Gerenciar Portal sem Vídeo"
        app_label = 'captive_portal'


class UploadVideosProxy(EldUploadVideo):
    """
    Proxy model para upload de vídeos
    """
    class Meta:
        proxy = True
        verbose_name = "Gerenciar Vídeos"
        verbose_name_plural = "Gerenciar Vídeos"
        app_label = 'captive_portal'


class CaptivePortalProxy(EldGerenciarPortal):
    """
    Proxy model principal para o app Captive Portal
    """
    class Meta:
        proxy = True
        verbose_name = "Captive Portal"
        verbose_name_plural = "Captive Portal"
        app_label = 'captive_portal'


class LogsVideosProxy(EldRegistroViewVideos):
    """
    Proxy model para logs de vídeos
    """
    class Meta:
        proxy = True
        verbose_name = "Logs de Vídeos"
        verbose_name_plural = "Logs de Vídeos"
        app_label = 'captive_portal'
