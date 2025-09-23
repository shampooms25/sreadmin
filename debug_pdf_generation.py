#!/usr/bin/env python3
"""
Script para testar a geração de PDF e identificar problemas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
sys.path.append(r'c:\Projetos\Poppnet\sreadmin')
django.setup()

from io import BytesIO
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from django.http import HttpResponse

def test_simple_pdf():
    """Testa geração de PDF simples"""
    print("🔍 Testando geração de PDF simples...")
    
    try:
        # Criar buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Conteúdo simples
        story = []
        story.append(Paragraph("Teste de PDF", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Este é um teste simples de geração de PDF.", styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        
        # Salvar arquivo de teste
        pdf_content = buffer.getvalue()
        
        with open('teste_simples.pdf', 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ PDF simples gerado: {len(pdf_content)} bytes")
        print(f"📁 Arquivo salvo: teste_simples.pdf")
        
        # Verificar cabeçalho PDF
        if pdf_content.startswith(b'%PDF-'):
            print("✅ Cabeçalho PDF válido")
        else:
            print("❌ Cabeçalho PDF inválido")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na geração de PDF simples: {e}")
        return False

def test_complex_pdf():
    """Testa geração de PDF com tabela (similar ao relatório)"""
    print("\n🔍 Testando geração de PDF com tabela...")
    
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue
        )
        
        story = []
        
        # Título
        title = Paragraph("Relatório de Disponibilidade Starlink - TESTE", title_style)
        story.append(title)
        story.append(Spacer(1, 15))
        
        # Data
        date_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Tabela de teste
        table_data = [
            ['Service Line', 'Localização', 'Uptime %', 'Downtime (h)', 'Status'],
            ['SL-123456-789', 'Teste Local', '99.5%', '1.2h', 'Ativo'],
            ['SL-987654-321', 'Outro Local', '98.8%', '2.9h', 'Ativo']
        ]
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Notas
        notes = [
            "• Teste de geração de PDF com tabela",
            "• Verificando formatação e estrutura",
            "• Sistema de relatórios funcionando"
        ]
        
        for note in notes:
            story.append(Paragraph(note, styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        
        pdf_content = buffer.getvalue()
        
        with open('teste_complexo.pdf', 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ PDF complexo gerado: {len(pdf_content)} bytes")
        print(f"📁 Arquivo salvo: teste_complexo.pdf")
        
        if pdf_content.startswith(b'%PDF-'):
            print("✅ Cabeçalho PDF válido")
        else:
            print("❌ Cabeçalho PDF inválido")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na geração de PDF complexo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔬 Teste de Geração de PDF - Diagnóstico")
    print("="*50)
    
    # Testar PDF simples
    simple_ok = test_simple_pdf()
    
    # Testar PDF complexo
    complex_ok = test_complex_pdf()
    
    print("\n" + "="*50)
    print("📊 RESULTADOS:")
    print(f"PDF Simples: {'✅ OK' if simple_ok else '❌ ERRO'}")
    print(f"PDF Complexo: {'✅ OK' if complex_ok else '❌ ERRO'}")
    
    if simple_ok and complex_ok:
        print("\n✅ ReportLab funcionando corretamente!")
        print("💡 O problema pode estar nos dados do relatório.")
    else:
        print("\n❌ Problema na biblioteca ReportLab ou configuração.")
