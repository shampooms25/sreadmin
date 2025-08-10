# Este arquivo vazio é necessário para o Django reconhecer como um módulo de modelos
# Os modelos estão definidos em painel.models para facilitar as migrações

from django.db import models
from django.utils import timezone
import uuid


class ApplianceToken(models.Model):
    """
    Modelo para gerenciar tokens de autenticação dos Appliances POPPFIRE
    """
    id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=64, unique=True, help_text="Token único para autenticação")
    appliance_id = models.CharField(max_length=100, unique=True, help_text="ID único do appliance")
    appliance_name = models.CharField(max_length=200, help_text="Nome descritivo do appliance")
    description = models.TextField(blank=True, null=True, help_text="Descrição adicional do appliance")
    is_active = models.BooleanField(default=True, help_text="Se o token está ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(blank=True, null=True, help_text="Última vez que o token foi usado")
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="Último IP que usou o token")
    
    class Meta:
        verbose_name = "Token do Appliance POPPFIRE"
        verbose_name_plural = "Tokens dos Appliances POPPFIRE"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.appliance_name} ({self.appliance_id})"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_token():
        """
        Gera um token único para o appliance
        """
        import hashlib
        import time
        
        # Usar timestamp e UUID para garantir unicidade
        unique_string = f"poppfire-{time.time()}-{uuid.uuid4()}"
        token = hashlib.sha256(unique_string.encode()).hexdigest()[:32]
        
        # Verificar se já existe (muito improvável, mas por segurança)
        while ApplianceToken.objects.filter(token=token).exists():
            unique_string = f"poppfire-{time.time()}-{uuid.uuid4()}"
            token = hashlib.sha256(unique_string.encode()).hexdigest()[:32]
        
        return token
    
    def mark_as_used(self, ip_address=None):
        """
        Marca o token como usado agora
        """
        self.last_used = timezone.now()
        if ip_address:
            self.ip_address = ip_address
        self.save(update_fields=['last_used', 'ip_address'])
    
    def is_expired(self):
        """
        Verifica se o token está expirado (pode ser implementado conforme necessário)
        """
        # Por enquanto, tokens não expiram automaticamente
        return False
    
    @property
    def status_display(self):
        """
        Retorna o status visual do token
        """
        if not self.is_active:
            return "🔴 Inativo"
        elif self.last_used:
            return f"🟢 Ativo (usado em {self.last_used.strftime('%d/%m/%Y %H:%M')})"
        else:
            return "🟡 Ativo (nunca usado)"
