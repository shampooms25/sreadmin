#!/usr/bin/env python
import os
import django
import sys

# Configurar Django
sys.path.append('/C/Projetos/Poppnet/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

# Testar importações de reportlab
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    from io import BytesIO
    print("✅ Todas as importações do ReportLab funcionaram!")
    
    # Teste simples de criação de PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.darkblue
    )
    
    # Conteúdo do PDF
    story = []
    title = Paragraph("Teste de PDF - Starlink", title_style)
    story.append(title)
    story.append(Spacer(1, 15))
    
    # Teste de tabela
    table_data = [['Service Line', 'Status', 'Uptime'], 
                  ['SL-854897-75238-43', 'Online', '99.5%'],
                  ['SL-854897-75238-45', 'Online', '98.2%']]
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    
    # Gerar PDF
    doc.build(story)
    buffer.seek(0)
    
    # Salvar arquivo de teste
    with open('test_pdf_output.pdf', 'wb') as f:
        f.write(buffer.getvalue())
    
    print("✅ PDF de teste gerado com sucesso: test_pdf_output.pdf")
    print(f"Tamanho do arquivo: {len(buffer.getvalue())} bytes")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro ao gerar PDF: {e}")
    import traceback
    traceback.print_exc()
