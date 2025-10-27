from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict
import json
import os

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=12,
            spaceBefore=12
        ))
    
    def generate_pdf_report(
        self,
        interview_data: Dict,
        scores_data: Dict,
        transcript_data: list,
        output_path: str
    ) -> str:
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        story.append(Paragraph("LAPORAN WAWANCARA SELEKSI ASN", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        info_data = [
            ['Nama Kandidat', interview_data.get('candidate_name', '-')],
            ['Posisi', interview_data.get('position', '-')],
            ['Tanggal Wawancara', self._format_datetime(interview_data.get('started_at'))],
            ['Durasi', f"{interview_data.get('duration_seconds', 0) // 60} menit"],
            ['Pewawancara', interview_data.get('interviewer_name', '-')],
            ['Status', interview_data.get('status', '-').upper()]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("NILAI BerAKHLAK", self.styles['SectionHeader']))
        
        berakhlak_dimensions = [
            ('Berorientasi Pelayanan', 'berorientasi_pelayanan'),
            ('Akuntabel', 'akuntabel'),
            ('Kompeten', 'kompeten'),
            ('Harmonis', 'harmonis'),
            ('Loyal', 'loyal'),
            ('Adaptif', 'adaptif'),
            ('Kolaboratif', 'kolaboratif')
        ]
        
        berakhlak_data = [['Dimensi', 'Skor AI', 'Skor Manual', 'Rata-rata']]
        for label, key in berakhlak_dimensions:
            ai_score = scores_data.get(f'{key}_ai', 0.0) or 0.0
            manual_score = scores_data.get(f'{key}_manual', 0.0) or 0.0
            avg = (ai_score + manual_score) / 2 if manual_score > 0 else ai_score
            berakhlak_data.append([
                label,
                f"{ai_score:.2f}",
                f"{manual_score:.2f}" if manual_score > 0 else "-",
                f"{avg:.2f}"
            ])
        
        berakhlak_table = Table(berakhlak_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
        berakhlak_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(berakhlak_table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("INDIKATOR PERILAKU", self.styles['SectionHeader']))
        
        behavioral_data = [
            ['Indikator', 'Skor'],
            ['Stabilitas Emosi', f"{scores_data.get('emotion_stability', 0.0):.2f}/5.00"],
            ['Kejelasan Komunikasi', f"{scores_data.get('speech_clarity', 0.0):.2f}/5.00"],
            ['Koherensi Jawaban', f"{scores_data.get('answer_coherence', 0.0):.2f}/5.00"]
        ]
        
        behavioral_table = Table(behavioral_data, colWidths=[3*inch, 2*inch])
        behavioral_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(behavioral_table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("SKOR KESELURUHAN", self.styles['SectionHeader']))
        
        overall_data = [
            ['Metrik', 'Nilai'],
            ['Skor AI', f"{scores_data.get('overall_ai_score', 0.0):.2f}/5.00"],
            ['Skor Manual', f"{scores_data.get('overall_manual_score', 0.0):.2f}/5.00" if scores_data.get('overall_manual_score') else "-"],
            ['Skor Akhir', f"{scores_data.get('final_score', 0.0):.2f}/5.00"]
        ]
        
        overall_table = Table(overall_data, colWidths=[3*inch, 2*inch])
        overall_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#48bb78')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(overall_table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("REKOMENDASI", self.styles['SectionHeader']))
        recommendation = interview_data.get('recommendation', 'dipertimbangkan').upper()
        rec_color = {
            'LAYAK': colors.green,
            'DIPERTIMBANGKAN': colors.orange,
            'TIDAK_LAYAK': colors.red
        }.get(recommendation, colors.grey)
        
        rec_style = ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=rec_color,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(recommendation, rec_style))
        story.append(Spacer(1, 0.3*inch))
        
        if scores_data.get('ai_analysis_summary'):
            story.append(PageBreak())
            story.append(Paragraph("RINGKASAN ANALISIS AI", self.styles['SectionHeader']))
            summary_text = scores_data['ai_analysis_summary'].replace('\n', '<br/>')
            story.append(Paragraph(summary_text, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        if scores_data.get('interviewer_notes'):
            story.append(Paragraph("CATATAN PEWAWANCARA", self.styles['SectionHeader']))
            notes_text = scores_data['interviewer_notes'].replace('\n', '<br/>')
            story.append(Paragraph(notes_text, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        if transcript_data:
            story.append(PageBreak())
            story.append(Paragraph("TRANSKRIP WAWANCARA", self.styles['SectionHeader']))
            
            for entry in transcript_data[:50]:
                speaker = entry.get('speaker', 'Unknown')
                text = entry.get('text', '')
                timestamp = entry.get('timestamp', 0)
                
                speaker_style = ParagraphStyle(
                    name='Speaker',
                    parent=self.styles['Normal'],
                    fontName='Helvetica-Bold',
                    fontSize=10
                )
                story.append(Paragraph(f"[{self._format_timestamp(timestamp)}] {speaker}:", speaker_style))
                story.append(Paragraph(text, self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        return output_path
    
    def generate_json_report(
        self,
        interview_data: Dict,
        scores_data: Dict,
        transcript_data: list,
        emotion_logs: list,
        output_path: str
    ) -> str:
        report_data = {
            "interview_info": interview_data,
            "scores": scores_data,
            "transcript": transcript_data,
            "emotion_logs": emotion_logs,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def _format_datetime(self, dt) -> str:
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        if dt:
            return dt.strftime('%d %B %Y, %H:%M WIB')
        return '-'
    
    def _format_timestamp(self, seconds: float) -> str:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
