from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

def test_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("Teste PDF", styles['Title']))
    story.append(Paragraph("Conteúdo de teste", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    pdf_data = buffer.getvalue()
    print(f"PDF gerado: {len(pdf_data)} bytes")
    
    # Salvar arquivo
    with open('teste_debug.pdf', 'wb') as f:
        f.write(pdf_data)
    
    # Verificar cabeçalho
    if pdf_data.startswith(b'%PDF-'):
        print("Cabeçalho PDF válido")
    else:
        print("Cabeçalho PDF inválido!")
        print(f"Primeiros bytes: {pdf_data[:20]}")

if __name__ == "__main__":
    try:
        test_pdf()
        print("Teste concluído!")
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
