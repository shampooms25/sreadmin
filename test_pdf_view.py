from django.http import HttpResponse
from io import BytesIO

def test_pdf_download(request):
    """Teste simples de download de PDF"""
    try:
        # Verificar se reportlab está disponível
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        
        # Criar PDF simples
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph("Teste de PDF - Funcionalidade OK!", styles['Title']))
        story.append(Paragraph("Este é um teste simples para verificar se o PDF está funcionando.", styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        
        # Criar resposta HTTP
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="teste.pdf"'
        
        return response
        
    except ImportError as e:
        return HttpResponse(f"Erro: ReportLab não está instalado - {e}", content_type='text/plain')
    except Exception as e:
        return HttpResponse(f"Erro ao gerar PDF: {e}", content_type='text/plain')
