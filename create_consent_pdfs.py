#!/usr/bin/env python3
"""
Script para generar documentos PDF de consentimiento informado
para la clínica RUBIO GARCÍA DENTAL
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime
import os

def create_consent_pdf(filename, title, content, treatment_info):
    """Crear un PDF de consentimiento informado"""
    
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=1*inch)
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.darkblue,
        alignment=1,  # Centrado
        spaceAfter=20
    )
    
    clinic_style = ParagraphStyle(
        'ClinicInfo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=1,  # Centrado
        spaceAfter=15
    )
    
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        alignment=0,  # Justificado
        spaceAfter=12,
        leftIndent=10,
        rightIndent=10
    )
    
    # Contenido del documento
    story = []
    
    # Encabezado de la clínica
    clinic_info = """
    <b>RUBIO GARCÍA DENTAL</b><br/>
    Calle Mayor 19, Alcorcón, 28921 Madrid<br/>
    Teléfono: 916 410 841 | WhatsApp: 664 218 253<br/>
    Email: info@rubiogarciadental.com
    """
    story.append(Paragraph(clinic_info, clinic_style))
    
    # Título del documento  
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Información del tratamiento
    if treatment_info:
        treatment_table = Table([
            ['Tratamiento:', treatment_info['name']],
            ['Código:', str(treatment_info['code'])],
            ['Descripción:', treatment_info['description']]
        ], colWidths=[2*inch, 4*inch])
        
        treatment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(treatment_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Contenido principal
    for paragraph in content:
        story.append(Paragraph(paragraph, content_style))
        story.append(Spacer(1, 0.15*inch))
    
    # Sección de firma
    story.append(Spacer(1, 0.4*inch))
    
    signature_table = Table([
        ['Fecha: _______________', 'Firma del Paciente: _______________'],
        ['', ''],
        ['Nombre del Paciente:', ''],
        ['_________________________________', ''],
        ['', ''],
        ['Firma del Profesional: _______________', 'Colegiado Nº: _______________']
    ], colWidths=[3*inch, 3*inch])
    
    signature_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
    ]))
    
    story.append(signature_table)
    
    # Pie de página
    footer = f"<i>Documento generado automáticamente - {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>"
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(footer, clinic_style))
    
    # Generar PDF
    doc.build(story)
    print(f"✅ PDF creado: {filename}")

def main():
    """Generar todos los PDFs de consentimiento"""
    
    # Asegurar que el directorio existe
    os.makedirs('/app/documents', exist_ok=True)
    
    # Definir los consentimientos
    consents = {
        'consent_treatment_9.pdf': {
            'title': 'CONSENTIMIENTO INFORMADO - PERIODONCIA',
            'treatment_info': {
                'name': 'Periodoncia',
                'code': 9,
                'description': 'Tratamiento de enfermedades de las encías y tejidos de soporte dental'
            },
            'content': [
                '<b>1. NATURALEZA DEL TRATAMIENTO:</b><br/>El tratamiento periodontal tiene como objetivo controlar la infección de las encías y preservar los tejidos de soporte de los dientes. Puede incluir raspado y alisado radicular, cirugía periodontal y mantenimiento.',
                
                '<b>2. RIESGOS Y COMPLICACIONES:</b><br/>Como en cualquier procedimiento médico, pueden existir riesgos incluyendo: sensibilidad dental temporal, sangrado de encías, recesión gingival, y en casos excepcionales, pérdida dental.',
                
                '<b>3. ALTERNATIVAS DE TRATAMIENTO:</b><br/>Las alternativas incluyen no realizar tratamiento (con riesgo de progresión de la enfermedad), tratamientos menos conservadores, o extracción dental.',
                
                '<b>4. CUIDADOS POST-TRATAMIENTO:</b><br/>Es fundamental mantener una higiene oral excelente y acudir a las citas de mantenimiento programadas. El éxito del tratamiento depende en gran medida de la colaboración del paciente.',
                
                '<b>5. CONSENTIMIENTO:</b><br/>He sido informado/a de la naturaleza del tratamiento, sus riesgos, beneficios y alternativas. He tenido la oportunidad de hacer preguntas y todas han sido respondidas satisfactoriamente.'
            ]
        },
        
        'consent_treatment_10.pdf': {
            'title': 'CONSENTIMIENTO INFORMADO - CIRUGÍA E IMPLANTES',
            'treatment_info': {
                'name': 'Cirugía e Implantes',
                'code': 10,
                'description': 'Procedimientos quirúrgicos orales y colocación de implantes dentales'
            },
            'content': [
                '<b>1. NATURALEZA DEL TRATAMIENTO:</b><br/>El tratamiento incluye procedimientos quirúrgicos como extracciones, colocación de implantes dentales, injertos óseos y cirugía oral. Los implantes son raíces artificiales de titanio que se integran al hueso.',
                
                '<b>2. RIESGOS Y COMPLICACIONES:</b><br/>Los riesgos incluyen: dolor post-operatorio, inflamación, sangrado, infección, daño a estructuras vecinas, fallo de osteointegración del implante, parestesias temporales o permanentes.',
                
                '<b>3. PROCESO DE CICATRIZACIÓN:</b><br/>La osteointegración del implante requiere de 3-6 meses. Durante este período es crucial seguir las indicaciones post-operatorias y mantener una higiene oral adecuada.',
                
                '<b>4. ÉXITO DEL TRATAMIENTO:</b><br/>Aunque los implantes tienen una alta tasa de éxito (>95%), no se puede garantizar el éxito al 100%. Factores como tabaco, diabetes y mala higiene pueden afectar el resultado.',
                
                '<b>5. ALTERNATIVAS:</b><br/>Las alternativas incluyen prótesis removibles, puentes fijos, o no realizar tratamiento. Cada opción tiene sus propias ventajas y limitaciones.',
                
                '<b>6. CONSENTIMIENTO:</b><br/>Entiendo los riesgos y beneficios del tratamiento quirúrgico e implantológico y consiento su realización.'
            ]
        },
        
        'consent_treatment_11.pdf': {
            'title': 'CONSENTIMIENTO INFORMADO - ORTODONCIA',
            'treatment_info': {
                'name': 'Ortodoncia',
                'code': 11,
                'description': 'Tratamiento para corregir la posición de dientes y maxilares'
            },
            'content': [
                '<b>1. NATURALEZA DEL TRATAMIENTO:</b><br/>El tratamiento de ortodoncia tiene como objetivo corregir la malposición dental y las alteraciones de crecimiento de los maxilares mediante aparatos fijos o removibles.',
                
                '<b>2. DURACIÓN DEL TRATAMIENTO:</b><br/>La duración estimada es de 18-36 meses, aunque puede variar según la complejidad del caso y la colaboración del paciente. Se requieren visitas regulares cada 4-8 semanas.',
                
                '<b>3. MOLESTIAS Y RIESGOS:</b><br/>Es normal experimentar molestias los primeros días tras cada ajuste. Los riesgos incluyen: descalcificación del esmalte, reabsorción radicular, problemas periodontales si no se mantiene buena higiene.',
                
                '<b>4. HIGIENE DURANTE EL TRATAMIENTO:</b><br/>Es fundamental mantener una higiene oral excelente durante todo el tratamiento. Se proporcionarán instrucciones específicas sobre cepillado y uso de hilo dental con aparatos.',
                
                '<b>5. RETENCIÓN:</b><br/>Tras la fase activa es necesario usar retenedores para mantener los resultados obtenidos. El no uso de retenedores puede causar recidiva del tratamiento.',
                
                '<b>6. CONSENTIMIENTO:</b><br/>He comprendido el tratamiento de ortodoncia, su duración, limitaciones y la importancia de mi colaboración para el éxito del mismo.'
            ]
        },
        
        'consent_treatment_16.pdf': {
            'title': 'CONSENTIMIENTO INFORMADO - ENDODONCIA',
            'treatment_info': {
                'name': 'Endodoncia',
                'code': 16,
                'description': 'Tratamiento del conducto radicular (tratamiento de nervio)'
            },
            'content': [
                '<b>1. NATURALEZA DEL TRATAMIENTO:</b><br/>La endodoncia consiste en la eliminación del tejido pulpar infectado o dañado del interior del diente, limpieza y desinfección de los conductos radiculares, y posterior sellado de los mismos.',
                
                '<b>2. INDICACIONES:</b><br/>Este tratamiento está indicado cuando la pulpa dental está irreversiblemente dañada por caries profunda, traumatismo, o por otras causas, y es la alternativa conservadora a la extracción dental.',
                
                '<b>3. PROCEDIMIENTO:</b><br/>El tratamiento puede requerir una o varias sesiones bajo anestesia local. Se accede a la pulpa a través de la corona del diente, se limpian los conductos y se sellan.',
                
                '<b>4. RIESGOS Y COMPLICACIONES:</b><br/>Aunque poco frecuentes, pueden incluir: fractura de instrumentos, perforación radicular, dolor post-operatorio, infección persistente, necesidad de retratamiento o cirugía.',
                
                '<b>5. PRONÓSTICO:</b><br/>El éxito de la endodoncia es superior al 90%. Sin embargo, no se puede garantizar el éxito al 100%. Algunos casos pueden requerir retratamiento o extracción.',
                
                '<b>6. RESTAURACIÓN POSTERIOR:</b><br/>Tras la endodoncia, el diente deberá ser restaurado adecuadamente, generalmente con una corona, para protegerlo de futuras fracturas.',
                
                '<b>7. CONSENTIMIENTO:</b><br/>He sido informado/a sobre el tratamiento endodóntico, comprendo los riesgos y beneficios, y consiento su realización.'
            ]
        },
        
        'consent_lopd_13.pdf': {
            'title': 'INFORMACIÓN SOBRE PROTECCIÓN DE DATOS - LOPD',
            'treatment_info': {
                'name': 'Protección de Datos LOPD',
                'code': 13,
                'description': 'Información sobre el tratamiento de datos personales según normativa vigente'
            },
            'content': [
                '<b>RESPONSABLE DEL TRATAMIENTO:</b><br/>RUBIO GARCÍA DENTAL - Dr. Mario Rubio García<br/>Dirección: Calle Mayor 19, Alcorcón, 28921 Madrid<br/>Teléfono: 916 410 841 | Email: info@rubiogarciadental.com',
                
                '<b>FINALIDAD DEL TRATAMIENTO:</b><br/>Sus datos personales serán tratados para: gestión de la historia clínica, programación de citas, comunicación con el paciente, facturación, y cumplimiento de obligaciones legales sanitarias.',
                
                '<b>LEGITIMACIÓN:</b><br/>El tratamiento de sus datos se basa en: consentimiento del interesado, relación contractual para la prestación de servicios sanitarios, y cumplimiento de obligaciones legales.',
                
                '<b>CONSERVACIÓN:</b><br/>Los datos se conservarán durante el tiempo necesario para cumplir con las finalidades descritas y las obligaciones legales. Los datos clínicos se conservarán según la normativa sanitaria vigente.',
                
                '<b>DESTINATARIOS:</b><br/>No se cederán datos a terceros salvo obligación legal. Pueden ser comunicados a: laboratorios de prótesis dental, compañías de seguros (si aplica), autoridades sanitarias cuando sea requerido.',
                
                '<b>DERECHOS DEL INTERESADO:</b><br/>Tiene derecho a: acceder a sus datos, rectificarlos, suprimirlos, limitar su tratamiento, oponerse al tratamiento, y portabilidad de datos. Para ejercer estos derechos, contacte con nosotros.',
                
                '<b>MEDIDAS DE SEGURIDAD:</b><br/>Hemos implementado medidas técnicas y organizativas apropiadas para proteger sus datos personales contra el acceso no autorizado, alteración, divulgación o destrucción.',
                
                '<b>CONSENTIMIENTO:</b><br/>Al firmar este documento, consiento el tratamiento de mis datos personales conforme a lo expuesto anteriormente y para las finalidades descritas.'
            ]
        }
    }
    
    # Generar cada PDF
    for filename, data in consents.items():
        filepath = f"/app/documents/{filename}"
        create_consent_pdf(
            filepath,
            data['title'],
            data['content'],
            data['treatment_info']
        )
    
    print(f"\n🎉 Se han generado {len(consents)} documentos PDF de consentimiento en /app/documents/")
    print("📋 Documentos creados:")
    for filename in consents.keys():
        print(f"   • {filename}")

if __name__ == "__main__":
    main()