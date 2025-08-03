"""
Versão simplificada do método save() do EldUploadVideo
para testar upload sem processamento adicional
"""

def save(self, *args, **kwargs):
    """
    VERSÃO SIMPLIFICADA PARA TESTE
    Remove notificações e processamento de ZIP
    """
    # Verificar se é um novo registro
    is_new = self.pk is None
    
    # Calcular tamanho do arquivo em MB
    if self.video:
        self.tamanho = round(self.video.size / (1024 * 1024), 2)
    
    # Salvar o modelo (sem processamento adicional)
    super().save(*args, **kwargs)
    
    # REMOVIDO: todo o processamento de notificações e ZIP
    # para isolar o problema
    
    print(f"✅ Vídeo salvo com sucesso: {self.video.name}")
