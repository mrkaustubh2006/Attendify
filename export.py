import io
import os
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
class ExportService:
    @staticmethod
    def export_to_excel(records_data: list, title: str = "Attendance Report") -> io.BytesIO:
        """
        Exports list of attendance records to an Excel spreadsheet in memory.
        Returns a BytesIO stream.
        """
        # Convert records to a DataFrame
        df = pd.DataFrame(records_data)
        
        # Ensure column names are human readable
        column_mapping = {
            'student_id': 'Student ID',
            'name': 'Student Name',
            'class_name': 'Class/Department',
            'roll_no': 'Roll No',
            'subject_name': 'Subject',
            'subject_code': 'Subject Code',
            'date': 'Date',
            'time': 'Time',
            'status': 'Status',
            'attendance_method': 'Method'
        }
        
        # Rename columns that exist in the record
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Create an in-memory buffer
        output = io.BytesIO()
        
        # Write to excel using openpyxl
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Attendance', index=False)
            
            # Auto-adjust columns width in Excel sheet
            workbook = writer.book
            worksheet = writer.sheets['Attendance']
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
                
        output.seek(0)
        return output
    @staticmethod
    def export_to_pdf(records_data: list, title: str = "Attendance Report") -> io.BytesIO:
        """
        Exports list of attendance records to a beautifully styled PDF in memory.
        Returns a BytesIO stream.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles for clean, modern look
        title_style = ParagraphStyle(
            name='TitleStyle',
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#1e293b'), # Sleek slate-dark color
            alignment=1, # Centered
            spaceAfter=15
        )
        
        header_style = ParagraphStyle(
            name='HeaderStyle',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.white,
            alignment=1
        )
        
        cell_style = ParagraphStyle(
            name='CellStyle',
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#334155'),
            alignment=1
        )
        
        # Document Title
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Build table headers and data
        headers = ["Roll No", "Student Name", "Class", "Subject", "Date", "Time", "Status", "Method"]
        table_data = [[Paragraph(h, header_style) for h in headers]]
        
        for r in records_data:
            # Format time if it is a time object
            t_str = r.get('time', '')
            if isinstance(t_str, (datetime, time)):
                t_str = t_str.strftime('%H:%M:%S')
            elif hasattr(t_str, 'strftime'):
                t_str = t_str.strftime('%H:%M:%S')
            
            d_str = r.get('date', '')
            if hasattr(d_str, 'strftime'):
                d_str = d_str.strftime('%Y-%m-%d')
                
            row = [
                Paragraph(str(r.get('roll_no', '')), cell_style),
                Paragraph(str(r.get('name', '')), cell_style),
                Paragraph(str(r.get('class_name', '')), cell_style),
                Paragraph(str(r.get('subject_name', '')), cell_style),
                Paragraph(str(d_str), cell_style),
                Paragraph(str(t_str), cell_style),
                Paragraph(str(r.get('status', 'Present')), cell_style),
                Paragraph(str(r.get('attendance_method', 'QR')), cell_style)
            ]
            table_data.append(row)
            
        # Table Styling
        # 540 pt is the printable width for standard letter page size with 30 pt margins (612 - 60)
        col_widths = [45, 110, 80, 100, 65, 55, 45, 40]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')), # Slate-900 background for header
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')), # light grey grid
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]) # alternating rows
        ]))
        
        story.append(t)
        doc.build(story)
        buffer.seek(0)
        return buffer