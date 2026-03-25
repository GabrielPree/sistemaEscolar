import os
import sys
from openpyxl import Workbook
from openpyxl.styles import Font
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image
from datetime import datetime
from pathlib import Path

def caminho_recurso(arquivo):
    try:
        caminho = sys._MEIPASS  # quando vira .exe
    except Exception:
        caminho = os.path.abspath(".")  # quando roda normal

    return os.path.join(caminho, arquivo)

def _normalizar_dados_exportacao(dados, colunas):
    colunas_norm = list(colunas)
    dados_norm = [list(linha) for linha in dados]

    if colunas_norm:
        # garantir que o cabeçalho tenha o mesmo tamanho das colunas
        tamanho_esperado = len(colunas_norm)
        dados_norm = [
            linha[-tamanho_esperado:] if len(linha) > tamanho_esperado else linha
            for linha in dados_norm
        ]

    remover = {
        # remover colunas que contenham "excluir" ou "id"
        idx
        for idx, coluna in enumerate(colunas_norm)
        if coluna.strip().lower() == "excluir" or "id" in coluna.strip().lower()
    }

    if remover:
        # remover colunas
        colunas_norm = [c for i, c in enumerate(colunas_norm) if i not in remover]
        dados_norm = [
            [valor for i, valor in enumerate(linha) if i not in remover]
            for linha in dados_norm
        ]

    return dados_norm, colunas_norm

def exportar_excel(dados, colunas, caminho):
    wb = Workbook()
    ws = wb.active
    ws.title = "Dados"

    dados, colunas = _normalizar_dados_exportacao(dados, colunas)

    ws.append(colunas)

    # cabeçalho em negrito
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for linha in dados:
        ws.append(linha)

    # ajuste automático das colunas
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter

        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))

        ws.column_dimensions[col_letter].width = max_length + 2

    wb.save(caminho)

def exportar_pdf(dados, colunas, caminho):
    dados, colunas = _normalizar_dados_exportacao(dados, colunas)

    doc = SimpleDocTemplate(caminho, pagesize=A4)
    elementos = []
    styles = getSampleStyleSheet()

    # header com logo, título e data
    logo_path = caminho_recurso("logopdf.png")
    logo = Image(str(logo_path), width=1.5*cm, height=1.5*cm)

    titulo = Paragraph(
        "<b>Sistema Escolar</b><br/><font size=15>Gerenciamento de Alunos e Notas</font>",
        styles["Heading1"]
    )

    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    data_texto = Paragraph(
        f"<b>Gerado em:</b><br/>{data_geracao}",
        styles["Normal"]
    )

    logo_titulo = Table(
        [[logo, titulo]],
        colWidths=[1.5*cm, 10*cm]
    )

    logo_titulo.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))

    # header principal
    header = Table(
        [[logo_titulo, data_texto]],
        colWidths=[13*cm, 4*cm]
    )

    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    elementos.append(header)
    elementos.append(Spacer(1, 25))

    titulo_relatorio = Paragraph(
        "<b>Relatório - Sistema Escolar</b>",
        styles["Title"]
    )

    elementos.append(titulo_relatorio)
    elementos.append(Spacer(1, 20))

    tabela = Table([colunas] + dados, hAlign="CENTER")
    tabela.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), "#0f172a"),
    ("TEXTCOLOR", (0, 0), (-1, 0), "#ffffff"),

    ("ALIGN", (0, 0), (-1, -1), "CENTER"),

    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),

    ("GRID", (0, 0), (-1, -1), 0.5, "#9ca3af"),

    ("BACKGROUND", (0, 1), (-1, -1), "#f8fafc"),
    ]))

    elementos.append(tabela)
    doc.build(elementos)