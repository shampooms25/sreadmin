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
        # Calcular tamanho do arquivo em MB
        if self.video:
            self.tamanho = round(self.video.size / (1024 * 1024), 2)
        super().save(*args, **kwargs)


class EldGerenciarPortal(models.Model):
    """
    Modelo para gerenciar a configuração do portal captive
    Controla qual vídeo será exibido e o arquivo ZIP do portal
    """
    
    # Campo para ativar/desativar a exibição de vídeo
    ativar_video = models.BooleanField(
        default=False,
        verbose_name="Ativar Vídeo",
        help_text="Ativar para permitir que o OpenSense baixe e exiba vídeos no portal captive"
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
        verbose_name="Arquivo ZIP do Portal",
        help_text="Upload do arquivo .zip contendo os arquivos do portal captive"
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
        status_video = "✅ Ativo" if self.ativar_video else "❌ Inativo"
        if self.nome_video:
            video_nome = self.nome_video.video.name if self.nome_video.video else f"Vídeo {self.nome_video.id}"
        else:
            video_nome = "Nenhum vídeo selecionado"
        return f"Portal Captive - Vídeo: {status_video} | {video_nome}"

    def clean(self):
        """
        Validações personalizadas do modelo
        """
        from django.core.exceptions import ValidationError
        super().clean()
        
        # Se ativar_video for True, nome_video deve ser obrigatório
        if self.ativar_video and not self.nome_video:
            raise ValidationError({
                'nome_video': 'Quando o vídeo estiver ativado, você deve selecionar um vídeo.'
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
        Override do save para aplicar validações
        """
        self.clean()
        super().save(*args, **kwargs)

    def get_video_url(self):
        """
        Retorna a URL do vídeo selecionado para o OpenSense
        """
        if self.ativar_video and self.nome_video:
            return self.nome_video.video.url
        return None

    def get_portal_zip_url(self):
        """
        Retorna a URL do arquivo ZIP do portal
        """
        if self.captive_portal_zip:
            return self.captive_portal_zip.url
        return None

    @property
    def status_configuracao(self):
        """
        Retorna o status da configuração em formato legível
        """
        if not self.ativo:
            return "Inativa"
        
        if self.ativar_video and self.nome_video:
            video_name = self.nome_video.video.name if self.nome_video.video else f"Vídeo {self.nome_video.id}"
            return f"Ativa - Vídeo: {video_name}"
        elif self.ativar_video:
            return "Ativa - Aguardando seleção de vídeo"
        else:
            return "Ativa - Vídeo desativado"

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
