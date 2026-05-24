from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import qrcode
from io import BytesIO


class InvoicePDFGenerator:
    """Generador de facturas en PDF con formato fiscal venezolano"""
    
    def __init__(self, sale_data: dict, company_info: dict):
        self.sale = sale_data
        self.company = company_info
        self.styles = getSampleStyleSheet()
        
        # Estilos personalizados
        self.styles.add(ParagraphStyle(
            name='CenterTitle',
            parent=self.styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=16,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT
        ))
    
    def generate_qr_code(self) -> bytes:
        """Genera código QR con información de la factura"""
        qr_data = f"""RIF:{self.company['rif']}|
Factura:{self.sale['invoice_number']}|
Fecha:{self.sale['created_at'].strftime('%Y-%m-%d')}|
Total:{self.sale['total_bsf']:.2f}|
IVA:{self.sale['iva_amount_bsf']:.2f}"""
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_pdf(self, filename: str):
        """Genera el archivo PDF de la factura"""
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        elements = []
        
        # Encabezado de la empresa
        elements.append(Paragraph(self.company['name'], self.styles['CenterTitle']))
        elements.append(Paragraph(f"RIF: {self.company['rif']}", self.styles['Normal']))
        elements.append(Paragraph(self.company['address'], self.styles['Normal']))
        elements.append(Paragraph(f"Teléfono: {self.company['phone']}", self.styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Información de la factura
        invoice_info = [
            ['FACTURA N°:', self.sale['invoice_number']],
            ['FECHA:', self.sale['created_at'].strftime('%d/%m/%Y %H:%M')],
            ['Punto de Venta:', '0001'],
            ['Equipo:', '01']
        ]
        
        table_info = Table(invoice_info, colWidths=[2*inch, 2*inch])
        table_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        elements.append(table_info)
        elements.append(Spacer(1, 0.3*inch))
        
        # Información del cliente
        elements.append(Paragraph("INFORMACIÓN DEL CLIENTE", self.styles['Heading2']))
        
        customer_info = [
            ['Nombre/Razón Social:', self.sale['customer']['name']],
            ['RIF:', self.sale['customer']['rif']],
            ['Dirección:', self.sale['customer'].get('address', 'N/A')],
            ['Teléfono:', self.sale['customer'].get('phone', 'N/A')]
        ]
        
        table_customer = Table(customer_info, colWidths=[2.5*inch, 3.5*inch])
        table_customer.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        elements.append(table_customer)
        elements.append(Spacer(1, 0.3*inch))
        
        # Tabla de productos
        elements.append(Paragraph("DETALLE DE LA VENTA", self.styles['Heading2']))
        
        # Encabezados de la tabla
        headers = [
            ['Cant.', 'Descripción', 'Precio Unit.', 'Subtotal', 'IVA', 'Total'],
        ]
        
        # Datos de productos
        product_rows = []
        for item in self.sale['items']:
            product_rows.append([
                str(item['quantity']),
                item['product']['name'],
                f"{item['unit_price_bsf']:.2f}",
                f"{item['subtotal_bsf']:.2f}",
                f"{item['iva_amount_bsf']:.2f}" if item['iva_rate'] > 0 else "Exento",
                f"{item['total_bsf']:.2f}"
            ])
        
        all_rows = headers + product_rows
        
        table_products = Table(all_rows, colWidths=[0.8*inch, 2.5*inch, 1.2*inch, 1.2*inch, 1*inch, 1.2*inch])
        table_products.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        elements.append(table_products)
        elements.append(Spacer(1, 0.3*inch))
        
        # Totales
        totals_data = [
            ['SUBTOTAL USD:', f"${self.sale['subtotal_usd']:.2f}"],
            ['SUBTOTAL BSF:', f"Bs. {self.sale['subtotal_bsf']:.2f}"],
            ['IVA USD:', f"${self.sale['iva_amount_usd']:.2f}"],
            ['IVA BSF:', f"Bs. {self.sale['iva_amount_bsf']:.2f}"],
        ]
        
        # Agregar IGTF si aplica
        if self.sale.get('igtf_amount_usd', 0) > 0:
            totals_data.append(['IGTF (3%) USD:', f"${self.sale['igtf_amount_usd']:.2f}"])
            totals_data.append(['IGTF (3%) BSF:', f"Bs. {self.sale['igtf_amount_bsf']:.2f}"])
        
        totals_data.append(['TOTAL USD:', f"${self.sale['total_usd']:.2f}"])
        totals_data.append(['TOTAL BSF:', f"Bs. {self.sale['total_bsf']:.2f}"])
        totals_data.append(['TASA DE CAMBIO:', f"Bs. {self.sale['exchange_rate']:.2f}"])
        
        table_totals = Table(totals_data, colWidths=[3*inch, 2*inch], style=[
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, -3), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, -3), (0, -1), 'Helvetica-Bold'),
        ])
        elements.append(table_totals)
        elements.append(Spacer(1, 0.3*inch))
        
        # Código QR
        elements.append(Paragraph("CÓDIGO QR FISCAL", self.styles['Heading3']))
        
        qr_buffer = self.generate_qr_code()
        qr_image = Image(BytesIO(qr_buffer), width=1.5*inch, height=1.5*inch)
        elements.append(qr_image)
        elements.append(Spacer(1, 0.2*inch))
        
        # Notas legales
        legal_text = """
        <para style="font-size: 8px; text-align: center;">
        Esta factura tiene una validez de 30 días a partir de su emisión.<br/>
        De conformidad con lo establecido en los artículos 10 y 11 del Providencia Administrativa SNAT/2015/0049.
        </para>
        """
        elements.append(Paragraph(legal_text, self.styles['Normal']))
        
        # Construir PDF
        doc.build(elements)


def generate_invoice_pdf(sale_data: dict, company_info: dict, filename: str = "factura.pdf"):
    """Función auxiliar para generar factura PDF"""
    generator = InvoicePDFGenerator(sale_data, company_info)
    generator.generate_pdf(filename)
    return filename
