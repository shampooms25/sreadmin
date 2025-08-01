#!/usr/bin/env python3
"""
Teste de upload de arquivo via código
"""

import os
import sys
import django
from django.core.files.uploadedfile import SimpleUploadedFile

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldUploadVideo

def create_test_video():
    """Criar um vídeo de teste"""
    print("🎬 CRIANDO VÍDEO DE TESTE...")
    print("=" * 50)
    
    try:
        # Criar arquivo de teste (simular vídeo pequeno)
        test_content = b"Test video content - not a real video but for testing"
        test_file = SimpleUploadedFile(
            "test_video.mp4",
            test_content,
            content_type="video/mp4"
        )
        
        # Criar registro no banco
        video = EldUploadVideo(video=test_file)
        video.save()
        
        print(f"✅ Vídeo criado com ID: {video.id}")
        print(f"📁 Arquivo: {video.video.name}")
        print(f"📊 Tamanho: {video.tamanho} MB")
        print(f"📅 Data: {video.data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_videos():
    """Listar vídeos existentes"""
    print("\n📋 LISTANDO VÍDEOS...")
    print("=" * 50)
    
    try:
        videos = EldUploadVideo.objects.all()
        
        if videos:
            for video in videos:
                print(f"ID: {video.id} | {video.video.name} | {video.tamanho}MB | {video.data}")
        else:
            print("📭 Nenhum vídeo encontrado")
            
        print(f"📊 Total: {len(videos)} vídeos")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE COMPLETO DO SISTEMA ELD")
    print("=" * 60)
    
    test1 = list_videos()
    test2 = create_test_video() 
    test3 = list_videos()
    
    print(f"\n🎯 Resultado: {'✅ TODOS OS TESTES PASSARAM' if (test1 and test2 and test3) else '❌ ALGUM TESTE FALHOU'}")
    print("\n💡 Agora acesse: http://localhost:8000/admin/eld/")
