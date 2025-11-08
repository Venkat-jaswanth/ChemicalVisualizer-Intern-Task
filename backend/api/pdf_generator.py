# backend/api/pdf_generator.py

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

def generate_summary_pdf(dataset):
    """
    Generates a PDF summary for a given Dataset object.
    Returns the PDF as raw bytes.
    """
    # Create a buffer to hold the PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    summary = dataset.summary
    if not summary:
        # Handle case where summary might be missing
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Error: No summary data available for this dataset.", styles['h1']))
        doc.build(elements)
        buffer.seek(0)
        return buffer.read()

    # --- Title ---
    styles = getSampleStyleSheet()
    title = Paragraph(f"Analysis Report: {dataset.name}", styles['h1'])
    elements.append(title)
    elements.append(Paragraph(f"Uploaded on: {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))

    # --- Summary Table ---
    elements.append(Paragraph("Key Metrics", styles['h2']))
    
    avg = summary.get('averages', {})
    table_data = [
        ['Metric', 'Value'],
        ['Total Equipment Count', summary.get('total_count', 'N/A')],
        ['Average Flowrate', f"{avg.get('avg_flowrate', 0):.2f}"],
        ['Average Pressure', f"{avg.get('avg_pressure', 0):.2f}"],
        ['Average Temperature', f"{avg.get('avg_temperature', 0):.2f}"],
    ]
    
    # Create and style the table
    summary_table = Table(table_data, colWidths=[2.5 * inch, 2.5 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F8BDB")), # Header bg
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F0F4F8")),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(summary_table)

    # --- Pie Chart ---
    elements.append(Paragraph("Equipment Type Distribution", styles['h2']))
    
    type_dist = summary.get('type_distribution', {})
    if type_dist:
        pie = Pie()
        pie.width = 3 * inch
        pie.height = 3 * inch
        pie.data = list(type_dist.values())
        pie.labels = list(type_dist.keys())
        
        # Simple styling
        pie.slices.strokeWidth = 0.5
        pie.sideLabels = 1 # Show labels on the side
        
        drawing = Drawing(4 * inch, 4 * inch)
        drawing.add(pie)
        
        # Add a legend
        legend = Legend()
        legend.alignment = 'right'
        legend.x = 10
        legend.y = 70
        legend.colorNamePairs = [(pie.slices[i].fillColor, (pie.labels[i], f'{pie.data[i]}')) for i in range(len(pie.data))]
        
        legend_drawing = Drawing(2 * inch, 2 * inch)
        legend_drawing.add(legend)
        
        # Add chart and legend to a container
        chart_with_legend = Table(
            [[drawing, legend_drawing]], 
            colWidths=[4.2 * inch, 2 * inch]
        )
        chart_with_legend.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        
        elements.append(chart_with_legend)

    # Build the PDF
    doc.build(elements)
    
    # Get the value of the buffer and return it
    buffer.seek(0)
    pdf_bytes = buffer.read()
    buffer.close()
    
    return pdf_bytes