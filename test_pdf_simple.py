from django.http import HttpResponse
from io import BytesIO
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet

def test_pdf_view(request):
    """View de teste para geração de PDF"""
    try:
        # Criar buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Conteúdo simples
        story = []
        story.append(Paragraph("TESTE - Relatório PDF", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Este é um teste de geração de PDF.", styles['Normal']))
        story.append(Paragraph("Se você conseguir visualizar este arquivo, o sistema está funcionando.", styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        
        # Retornar resposta HTTP com PDF
        pdf_data = buffer.getvalue()
        response = HttpResponse(pdf_data, content_type='application/pdf')
        
        # Headers para forçar download
        filename = f"teste_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = str(len(pdf_data))
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Erro na geração do PDF: {str(e)}", status=500)
