import sys
import os

# Adicionar o caminho do projeto ao Python path
sys.path.insert(0, 'C:/Projetos/Poppnet/sreadmin')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

try:
    import django
    django.setup()
    print("✅ Django setup OK")
except Exception as e:
    print(f"❌ Erro no Django setup: {e}")

# Testar importações do reportlab
try:
    from reportlab.pdfgen import canvas
    print("✅ reportlab.pdfgen.canvas OK")
    
    from reportlab.lib.pagesizes import A4
    print("✅ reportlab.lib.pagesizes OK")
    
    from reportlab.platypus import SimpleDocTemplate
    print("✅ reportlab.platypus OK")
    
    from io import BytesIO
    print("✅ io.BytesIO OK")
    
    # Teste básico de criação
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    print("✅ SimpleDocTemplate criado OK")
    
    # Teste de HttpResponse
    from django.http import HttpResponse
    print("✅ HttpResponse OK")
    
    # Teste básico de PDF
    response = HttpResponse(b'test content', content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="test.pdf"'
    print("✅ HttpResponse PDF headers OK")
    
    print("\n🎉 TODOS OS TESTES PASSARAM! A funcionalidade de PDF deve estar funcionando.")

except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
