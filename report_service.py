import io
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
def export_attendance_to_excel(records):
    """
    Exports a list of attendance records to an Excel spreadsheet in memory.
    """
    data = []
    for record in records:
        data.append({
            'Date': record.date.strftime('%Y-%m-%d'),
            'Time': record.time.strftime('%H:%M:%S'),
            'Student ID': record.student.student_id,
            'Student Name': record.student.name,
            'Class': record.student.class_name,
            'Roll No': record.student.roll_no,
            'Subject Code': record.subject.subject_code,
            'Subject Name': record.subject.subject_name,
            'Teacher': record.teacher.name if record.teacher else 'Manual/System',
            'Status': record.status,
            'Method': record.method
        })
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance Records')
        
        # Access openpyxl objects to auto-fit columns
        workbook = writer.book
        worksheet = writer.sheets['Attendance Records']
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
    output.seek(0)
    return output
def export_attendance_to_pdf(records, title_context="Attendance Report"):
    """
    Exports a list of attendance records to a PDF file in memory.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=20
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#2c3e50')
    )
    
    # Document Header
    story.append(Paragraph(title_context, title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Table Data Definition
    # Columns: Date, Student, Class, Roll No, Subject, Status, Method
    headers = ["Date", "Student", "Class", "Roll", "Subject", "Status", "Method"]
    table_data = [[Paragraph(h, table_header_style) for h in headers]]
    
    for r in records:
        row = [
            Paragraph(r.date.strftime('%Y-%m-%d'), table_cell_style),
            Paragraph(f"{r.student.name} ({r.student.student_id})", table_cell_style),
            Paragraph(r.student.class_name, table_cell_style),
            Paragraph(r.student.roll_no, table_cell_style),
            Paragraph(r.subject.subject_code, table_cell_style),
            Paragraph(r.status, table_cell_style),
            Paragraph(r.method, table_cell_style),
        ]
        table_data.append(row)
        
    # Build Table
    # Letter Page Width = 612pt. Margins = 36pt * 2 = 72pt. Available Width = 540pt.
    col_widths = [65, 125, 75, 45, 80, 75, 75]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    t_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])
    
    # Alternating row colors
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            t_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa'))
            
    t.setStyle(t_style)
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer
