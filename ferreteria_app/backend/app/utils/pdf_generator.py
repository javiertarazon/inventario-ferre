from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import qrcode
import io
import base64

from app.models.models import Invoice


def generate_invoice_pdf(invoice: Invoice, company_info: dict) -> bytes:
    """
    Genera un PDF de factura con formato fiscal venezolano.
    Incluye código QR con información de la factura.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT
    )
    
    right_style = ParagraphStyle(
        'Right',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT
    )
    
    center_style = ParagraphStyle(
        'Center',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER
    )
    
    elements = []
    
    # Encabezado de la empresa
    company_data = [
        [Paragraph(f"<b>{company_info.get('name', 'FERRETERÍA')}</b>", header_style)],
        [Paragraph(f"RIF: {company_info.get('rif', 'J-00000000-0')}", header_style)],
        [Paragraph(company_info.get('address', ''), header_style)],
        [Paragraph(f"Teléfono: {company_info.get('phone', '')}", header_style)],
    ]
    
    company_table = Table(company_data, colWidths=[6*cm])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    # Título y número de factura
    invoice_title = Paragraph("<b>FACTURA</b>", title_style)
    invoice_number = Paragraph(f"<b>N° {invoice.invoice_number}</b>", right_style)
    
    # Fecha y tasa BCV
    date_info = Paragraph(f"Fecha: {invoice.created_at.strftime('%d/%m/%Y %H:%M:%S')}", right_style)
    rate_info = Paragraph(f"Tasa BCV: Bs. {invoice.exchange_rate:.2f}", right_style)
    
    # Información del cliente
    customer_info = Paragraph("<b>Datos del Cliente</b>", header_style)
    
    # Obtener datos del cliente (asumiendo que están cargados)
    customer_rif = getattr(invoice.customer, 'rif', 'N/A') if hasattr(invoice, 'customer') else 'N/A'
    customer_name = getattr(invoice, 'customer', None)
    customer_name_str = customer_name.name if customer_name else 'N/A'
    customer_address = getattr(invoice, 'customer', None)
    customer_address_str = getattr(customer_address, 'address', '') if customer_address else ''
    
    customer_data = [
        [Paragraph(f"RIF: {customer_rif}", header_style)],
        [Paragraph(f"Nombre: {customer_name_str}", header_style)],
        [Paragraph(f"Dirección: {customer_address_str}", header_style)],
    ]
    
    customer_table = Table(customer_data, colWidths=[12*cm])
    customer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    # Tabla de productos
    items_data = [['Cant.', 'Descripción', 'Precio Unit. ($)', 'Subtotal ($)', 'IVA (%)', 'IVA ($)', 'Total ($)']]
    
    for item in invoice.items:
        product_name = getattr(item.product, 'name', f'Producto {item.product_id}') if hasattr(item, 'product') else f'Producto {item.product_id}'
        items_data.append([
            str(item.quantity),
            product_name,
            f"${item.unit_price_usd:.2f}",
            f"${item.subtotal_usd:.2f}",
            f"{item.iva_rate*100:.0f}%",
            f"${item.iva_amount_usd:.2f}",
            f"${item.total_usd:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[1.5*cm, 5*cm, 2*cm, 2*cm, 1.5*cm, 1.5*cm, 2*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    # Totales
    igtf_text = f"IGTF ({3 if invoice.apply_igtf else 0}%): ${invoice.igtf_amount_usd:.2f}" if invoice.apply_igtf else "IGTF: No aplica"
    
    totals_data = [
        ['Subtotal:', f"${invoice.subtotal_usd:.2f}"],
        ['IVA:', f"${invoice.iva_amount_usd:.2f}"],
        [igtf_text, f"${invoice.igtf_amount_usd:.2f}" if invoice.apply_igtf else "$0.00"],
        ['TOTAL (USD):', f"${invoice.total_usd:.2f}"],
        ['TOTAL (VES):', f"Bs. {invoice.total_vef:.2f}"],
    ]
    
    totals_table = Table(totals_data, colWidths=[10*cm, 4*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 3), (-1, 4), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEABOVE', (0, 3), (-1, 3), 2, colors.black),
        ('LINEABOVE', (0, 4), (-1, 4), 2, colors.black),
    ]))
    
    # Generar código QR con información de la factura
    qr_data = f"""RIF:{company_info.get('rif', '')}|FACTURA:{invoice.invoice_number}|FECHA:{invoice.created_at.strftime('%Y-%m-%d')}|MONTO:${invoice.total_usd:.2f}|BCV:{invoice.exchange_rate:.2f}"""
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Agregar elementos al documento
    elements.append(company_table)
    elements.append(Spacer(1, 0.3*cm))
    elements.append(invoice_title)
    elements.append(invoice_number)
    elements.append(date_info)
    elements.append(rate_info)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(customer_info)
    elements.append(customer_table)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(items_table)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(totals_table)
    elements.append(Spacer(1, 1*cm))
    
    # Nota legal
    legal_note = Paragraph(
        "<i>Esta factura tiene validez fiscal según la normativa del SENIAT. "
        "Conserve este documento como comprobante de su compra.</i>",
        ParagraphStyle('LegalNote', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)
    )
    elements.append(legal_note)
    
    # Construir PDF
    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def generate_invoice_summary(invoice: Invoice) -> dict:
    """
    Genera un resumen de la factura en formato JSON para APIs o frontend.
    """
    return {
        "invoice_number": invoice.invoice_number,
        "date": invoice.created_at.isoformat(),
        "customer": {
            "rif": getattr(invoice.customer, 'rif', 'N/A') if hasattr(invoice, 'customer') else 'N/A',
            "name": getattr(invoice.customer, 'name', 'N/A') if hasattr(invoice, 'customer') else 'N/A',
        },
        "items_count": len(invoice.items),
        "subtotal_usd": invoice.subtotal_usd,
        "iva_amount_usd": invoice.iva_amount_usd,
        "igtf_amount_usd": invoice.igtf_amount_usd,
        "total_usd": invoice.total_usd,
        "exchange_rate": invoice.exchange_rate,
        "total_vef": invoice.total_vef,
        "payment_method": invoice.payment_method,
        "status": invoice.status.value,
    }
