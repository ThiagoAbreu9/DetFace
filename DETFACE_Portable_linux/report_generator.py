#!/usr/bin/env python3
"""
DETFACE - Gerador de Relatórios
Responsável por gerar relatórios em CSV e PDF dos registros de presença
"""

import pandas as pd
import datetime
from pathlib import Path
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json

class ReportGenerator:
    """Classe responsável pela geração de relatórios"""
    
    def __init__(self):
        """Inicializa o gerador de relatórios"""
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        self.attendance_file = "registro_presenca.csv"
        
    def load_attendance_data(self):
        """Carrega os dados de presença do arquivo CSV"""
        if not os.path.exists(self.attendance_file):
            return pd.DataFrame()
            
        try:
            df = pd.read_csv(self.attendance_file, encoding='utf-8')
            df['Data'] = pd.to_datetime(df['Data'])
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            return df
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {str(e)}")
            return pd.DataFrame()
            
    def generate_weekly_report(self):
        """Gera relatório da última semana"""
        # Calcular período da última semana
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=7)
        
        return self.generate_period_report(start_date, end_date, "semanal")
        
    def generate_monthly_report(self):
        """Gera relatório do último mês"""
        # Calcular período do último mês
        end_date = datetime.date.today()
        start_date = end_date.replace(day=1)  # Primeiro dia do mês atual
        
        # Se quisermos o mês anterior completo
        if start_date == end_date:
            # Último dia do mês anterior
            end_date = start_date - datetime.timedelta(days=1)
            start_date = end_date.replace(day=1)
        
        return self.generate_period_report(start_date, end_date, "mensal")
        
    def generate_period_report(self, start_date, end_date, period_type):
        """Gera relatório para um período específico"""
        df = self.load_attendance_data()
        
        if df.empty:
            print("❌ Nenhum dado de presença encontrado")
            return None, None
            
        # Filtrar dados pelo período
        mask = (df['Data'].dt.date >= start_date) & (df['Data'].dt.date <= end_date)
        period_data = df[mask].copy()
        
        if period_data.empty:
            print(f"❌ Nenhum registro encontrado para o período {start_date} a {end_date}")
            return None, None
            
        # Gerar relatórios
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"relatorio_{period_type}_{timestamp}.csv"
        pdf_filename = f"relatorio_{period_type}_{timestamp}.pdf"
        
        csv_path = self.reports_dir / csv_filename
        pdf_path = self.reports_dir / pdf_filename
        
        # Gerar CSV
        self.generate_csv_report(period_data, csv_path, start_date, end_date, period_type)
        
        # Gerar PDF
        self.generate_pdf_report(period_data, pdf_path, start_date, end_date, period_type)
        
        return str(csv_path), str(pdf_path)
        
    def generate_csv_report(self, data, filepath, start_date, end_date, period_type):
        """Gera relatório em formato CSV"""
        # Criar relatório detalhado
        detailed_report = data[['Data', 'Hora', 'Nome', 'ID_Usuario', 'Tipo']].copy()
        detailed_report = detailed_report.sort_values(['Data', 'Hora'])
        
        # Criar resumo por usuário
        summary = self.create_user_summary(data)
        
        # Salvar CSV com múltiplas abas (sheets)
        with pd.ExcelWriter(str(filepath).replace('.csv', '.xlsx'), engine='openpyxl') as writer:
            detailed_report.to_excel(writer, sheet_name='Detalhado', index=False)
            summary.to_excel(writer, sheet_name='Resumo', index=False)
            
        # Salvar também em CSV simples
        detailed_report.to_csv(filepath, index=False, encoding='utf-8')
        
    def create_user_summary(self, data):
        """Cria resumo por usuário"""
        summary_data = []
        
        for user_id in data['ID_Usuario'].unique():
            user_data = data[data['ID_Usuario'] == user_id]
            user_name = user_data['Nome'].iloc[0]
            
            total_entries = len(user_data[user_data['Tipo'] == 'ENTRADA'])
            total_exits = len(user_data[user_data['Tipo'] == 'SAÍDA'])
            
            # Calcular tempo total (aproximado)
            total_time = self.calculate_total_time(user_data)
            
            first_entry = user_data['Data'].min().strftime('%Y-%m-%d') if not user_data.empty else 'N/A'
            last_entry = user_data['Data'].max().strftime('%Y-%m-%d') if not user_data.empty else 'N/A'
            
            summary_data.append({
                'Nome': user_name,
                'ID_Usuario': user_id,
                'Total_Entradas': total_entries,
                'Total_Saidas': total_exits,
                'Tempo_Total_Horas': total_time,
                'Primeira_Entrada': first_entry,
                'Ultima_Entrada': last_entry,
                'Total_Registros': len(user_data)
            })
            
        return pd.DataFrame(summary_data)
        
    def calculate_total_time(self, user_data):
        """Calcula tempo total aproximado baseado em pares entrada/saída"""
        user_data = user_data.sort_values('Timestamp')
        total_hours = 0
        
        entries = user_data[user_data['Tipo'] == 'ENTRADA']['Timestamp'].tolist()
        exits = user_data[user_data['Tipo'] == 'SAÍDA']['Timestamp'].tolist()
        
        # Emparelhar entradas com saídas
        for i, entry_time in enumerate(entries):
            # Procurar próxima saída após esta entrada
            next_exits = [exit_time for exit_time in exits if exit_time > entry_time]
            if next_exits:
                exit_time = min(next_exits)
                duration = (exit_time - entry_time).total_seconds() / 3600  # Converter para horas
                total_hours += duration
                exits.remove(exit_time)  # Remover para não usar novamente
                
        return round(total_hours, 2)
        
    def generate_pdf_report(self, data, filepath, start_date, end_date, period_type):
        """Gera relatório em formato PDF"""
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            spaceAfter=30,
            fontSize=16,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            alignment=TA_LEFT,
            spaceAfter=12,
            fontSize=12,
            textColor=colors.darkblue
        )
        
        # Título
        title = Paragraph(f"DETFACE - Relatório {period_type.title()}", title_style)
        elements.append(title)
        
        # Informações do período
        period_info = Paragraph(
            f"<b>Período:</b> {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}<br/>"
            f"<b>Data de Geração:</b> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br/>"
            f"<b>Total de Registros:</b> {len(data)}",
            styles['Normal']
        )
        elements.append(period_info)
        elements.append(Spacer(1, 20))
        
        # Resumo Executivo
        elements.append(Paragraph("Resumo Executivo", heading_style))
        
        summary = self.create_user_summary(data)
        if not summary.empty:
            total_users = len(summary)
            total_entries = summary['Total_Entradas'].sum()
            total_exits = summary['Total_Saidas'].sum()
            total_time = summary['Tempo_Total_Horas'].sum()
            
            summary_text = Paragraph(
                f"• <b>Usuários ativos:</b> {total_users}<br/>"
                f"• <b>Total de entradas:</b> {total_entries}<br/>"
                f"• <b>Total de saídas:</b> {total_exits}<br/>"
                f"• <b>Tempo total registrado:</b> {total_time:.2f} horas<br/>"
                f"• <b>Média de tempo por usuário:</b> {(total_time/total_users if total_users > 0 else 0):.2f} horas",
                styles['Normal']
            )
            elements.append(summary_text)
            elements.append(Spacer(1, 20))
            
            # Tabela de resumo por usuário
            elements.append(Paragraph("Resumo por Usuário", heading_style))
            
            summary_table_data = [['Nome', 'Entradas', 'Saídas', 'Tempo (h)']]
            for _, row in summary.iterrows():
                summary_table_data.append([
                    row['Nome'][:20],  # Limitar tamanho do nome
                    str(row['Total_Entradas']),
                    str(row['Total_Saidas']),
                    f"{row['Tempo_Total_Horas']:.1f}"
                ])
                
            summary_table = Table(summary_table_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 20))
        
        # Registros detalhados
        elements.append(Paragraph("Registros Detalhados", heading_style))
        
        # Limitar a 50 registros mais recentes para não sobrecarregar o PDF
        recent_data = data.nlargest(50, 'Timestamp') if len(data) > 50 else data
        
        if not recent_data.empty:
            table_data = [['Data', 'Hora', 'Nome', 'Tipo']]
            
            for _, row in recent_data.iterrows():
                table_data.append([
                    row['Data'].strftime('%d/%m/%Y'),
                    row['Hora'],
                    row['Nome'][:25],  # Limitar tamanho do nome
                    row['Tipo']
                ])
                
            detailed_table = Table(table_data, colWidths=[1.5*inch, 1*inch, 2.5*inch, 1*inch])
            detailed_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            elements.append(detailed_table)
            
            if len(data) > 50:
                note = Paragraph(
                    f"<i>Nota: Mostrando apenas os 50 registros mais recentes de {len(data)} total.</i>",
                    styles['Normal']
                )
                elements.append(Spacer(1, 10))
                elements.append(note)
        
        # Rodapé
        elements.append(Spacer(1, 30))
        footer = Paragraph(
            "Relatório gerado automaticamente pelo sistema DETFACE<br/>"
            "Sistema de Reconhecimento Facial para Controle de Presença",
            ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                alignment=TA_CENTER,
                fontSize=8,
                textColor=colors.grey
            )
        )
        elements.append(footer)
        
        # Construir PDF
        doc.build(elements)
        
    def generate_custom_report(self, start_date, end_date, users=None, report_type="custom"):
        """Gera relatório personalizado"""
        df = self.load_attendance_data()
        
        if df.empty:
            print("❌ Nenhum dado de presença encontrado")
            return None, None
            
        # Filtrar por período
        mask = (df['Data'].dt.date >= start_date) & (df['Data'].dt.date <= end_date)
        filtered_data = df[mask].copy()
        
        # Filtrar por usuários se especificado
        if users:
            filtered_data = filtered_data[filtered_data['ID_Usuario'].isin(users)]
            
        if filtered_data.empty:
            print("❌ Nenhum registro encontrado para os critérios especificados")
            return None, None
            
        return self.generate_period_report(start_date, end_date, report_type)
        
    def get_attendance_statistics(self):
        """Retorna estatísticas gerais de presença"""
        df = self.load_attendance_data()
        
        if df.empty:
            return {}
            
        stats = {
            'total_records': len(df),
            'unique_users': df['ID_Usuario'].nunique(),
            'date_range': {
                'start': df['Data'].min().strftime('%Y-%m-%d') if not df.empty else None,
                'end': df['Data'].max().strftime('%Y-%m-%d') if not df.empty else None
            },
            'entries_today': len(df[(df['Data'].dt.date == datetime.date.today()) & 
                                   (df['Tipo'] == 'ENTRADA')]),
            'exits_today': len(df[(df['Data'].dt.date == datetime.date.today()) & 
                                 (df['Tipo'] == 'SAÍDA')])
        }
        
        return stats
