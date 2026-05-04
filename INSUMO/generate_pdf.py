#!/usr/bin/env python3
"""
Generador PDF — Manual de Instalación Plataforma Algarrobo BASE2
Formato institucional Municipalidad de Algarrobo
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, NextPageTemplate
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors

# ─── COLORES INSTITUCIONALES ──────────────────────────────────────────────────
NAVY       = HexColor('#1A2E4A')
NAVY_MED   = HexColor('#1D3557')
YELLOW     = HexColor('#F5B700')
GRAY_LIGHT = HexColor('#F7F9FC')
GRAY_LINE  = HexColor('#DEE2E6')
CODE_BG    = HexColor('#1E1E1E')
CODE_GRAY  = HexColor('#D4D4D4')
TEXT_DARK  = HexColor('#2D3748')
TEXT_MED   = HexColor('#4A5568')
TEXT_LIGHT = HexColor('#718096')
WARN_BG    = HexColor('#FFFBEB')
WARN_BORDER= HexColor('#D69E2E')
WARN_TEXT  = HexColor('#744210')

PAGE_W, PAGE_H = A4
ML = 2.5 * cm
MR = 2.5 * cm
MT = 2.5 * cm
MB = 2.0 * cm
CONTENT_W = PAGE_W - ML - MR

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'Manual_Instalacion_Algarrobo_BASE2.pdf')


# ═══════════════════════════════════════════════════════════════════════════════
# FLOWABLES CUSTOM
# ═══════════════════════════════════════════════════════════════════════════════

class YellowHeader(Flowable):
    """Header de sección con borde izquierdo amarillo y texto navy."""
    def __init__(self, text, level=1, space_before=16):
        Flowable.__init__(self)
        self.text    = text
        self.level   = level
        self.fs      = 13 if level == 1 else 11
        self.ht      = 28 if level == 1 else 23
        self.width   = CONTENT_W
        self.height  = self.ht
        self.space_before = space_before

    def wrap(self, availW, availH):
        return self.width, self.height + self.space_before

    def draw(self):
        c = self.canv
        c.saveState()
        c.translate(0, self.space_before)
        # Borde izquierdo amarillo
        c.setFillColor(YELLOW)
        c.rect(0, 0, 4, self.ht, fill=1, stroke=0)
        # Texto
        c.setFillColor(NAVY)
        c.setFont('Helvetica-Bold', self.fs)
        c.drawString(12, (self.ht - self.fs) / 2 + 1, self.text)
        c.restoreState()


def code_block(lines, extra_space_before=6, extra_space_after=8):
    """Bloque de código con fondo oscuro estilo VSCode."""
    safe_lines = []
    for line in lines:
        l = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        safe_lines.append(l)
    content = '<br/>'.join(safe_lines)

    p = Paragraph(
        f'<font color="#D4D4D4">{content}</font>',
        ParagraphStyle(
            'code_inner',
            fontName='Courier',
            fontSize=8.5,
            leading=13.5,
            textColor=CODE_GRAY,
        )
    )
    t = Table([[p]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), CODE_BG),
        ('LEFTPADDING',   (0, 0), (-1, -1), 14),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 14),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('SPACEBEFORE',   (0, 0), (-1, -1), extra_space_before),
        ('SPACEAFTER',    (0, 0), (-1, -1), extra_space_after),
    ]))
    return t


def warn_box(text):
    """Caja de advertencia/importante con fondo amarillo claro."""
    p = Paragraph(text, ParagraphStyle(
        'warn_inner',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=WARN_TEXT,
    ))
    t = Table([[p]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), WARN_BG),
        ('BOX',           (0, 0), (-1, -1), 1, WARN_BORDER),
        ('LEFTPADDING',   (0, 0), (-1, -1), 14),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 14),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('SPACEAFTER',    (0, 0), (-1, -1), 8),
    ]))
    return t


def nav_table(data, col_widths, has_header=True):
    """Tabla estándar con cabecera navy."""
    t = Table(data, colWidths=col_widths, repeatRows=1 if has_header else 0)
    style_cmds = [
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, -1), 8.5),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [white, GRAY_LIGHT]),
        ('GRID',          (0, 0), (-1, -1), 0.4, GRAY_LINE),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR',     (0, 1), (-1, -1), TEXT_DARK),
    ]
    if has_header:
        style_cmds += [
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('TEXTCOLOR',  (0, 0), (-1, 0), white),
            ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0, 0), (-1, 0), 9),
        ]
    t.setStyle(TableStyle(style_cmds))
    return t


# ═══════════════════════════════════════════════════════════════════════════════
# ESTILOS DE PÁRRAFO
# ═══════════════════════════════════════════════════════════════════════════════

def S(name):
    """Devuelve el estilo de párrafo por nombre."""
    return _STYLES[name]

_STYLES = {
    'body': ParagraphStyle('body', fontName='Helvetica', fontSize=10,
                           leading=15, textColor=TEXT_DARK, spaceAfter=6),
    'body_j': ParagraphStyle('body_j', fontName='Helvetica', fontSize=10,
                             leading=15, textColor=TEXT_DARK, spaceAfter=6,
                             alignment=TA_JUSTIFY),
    'bullet': ParagraphStyle('bullet', fontName='Helvetica', fontSize=10,
                             leading=14, textColor=TEXT_DARK,
                             leftIndent=14, spaceAfter=3),
    'bullet2': ParagraphStyle('bullet2', fontName='Helvetica', fontSize=10,
                              leading=14, textColor=TEXT_MED,
                              leftIndent=28, spaceAfter=2),
    'note': ParagraphStyle('note', fontName='Helvetica-Oblique', fontSize=9,
                           leading=13, textColor=TEXT_MED,
                           leftIndent=14, spaceAfter=6),
    'subhead': ParagraphStyle('subhead', fontName='Helvetica-Bold', fontSize=10,
                              leading=14, textColor=NAVY,
                              spaceBefore=10, spaceAfter=4),
    'toc1': ParagraphStyle('toc1', fontName='Helvetica', fontSize=10.5,
                           leading=22, textColor=TEXT_DARK),
    'toc2': ParagraphStyle('toc2', fontName='Helvetica', fontSize=10,
                           leading=20, textColor=TEXT_MED, leftIndent=18),
    'toc_pg': ParagraphStyle('toc_pg', fontName='Helvetica', fontSize=10,
                             leading=22, textColor=TEXT_MED, alignment=TA_RIGHT),
    'title_main': ParagraphStyle('title_main', fontName='Helvetica-Bold',
                                 fontSize=26, leading=32, textColor=NAVY,
                                 spaceAfter=8),
    'title_sub': ParagraphStyle('title_sub', fontName='Helvetica-Bold',
                                fontSize=20, leading=26, textColor=NAVY,
                                spaceAfter=16),
    'title_desc': ParagraphStyle('title_desc', fontName='Helvetica',
                                 fontSize=11, leading=17,
                                 textColor=HexColor('#4A5568'),
                                 spaceAfter=10, alignment=TA_JUSTIFY),
    'footer_note': ParagraphStyle('footer_note', fontName='Helvetica-Oblique',
                                  fontSize=9, textColor=TEXT_LIGHT,
                                  alignment=TA_CENTER, spaceAfter=2),
    'footer_inst': ParagraphStyle('footer_inst', fontName='Helvetica',
                                  fontSize=9, textColor=TEXT_LIGHT,
                                  alignment=TA_CENTER),
}


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CALLBACKS
# ═══════════════════════════════════════════════════════════════════════════════

def on_title_page(canvas, doc):
    canvas.saveState()
    panel_h = PAGE_H * 0.36

    # Panel navy inferior
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, panel_h, fill=1, stroke=0)

    # Línea amarilla divisoria
    canvas.setFillColor(YELLOW)
    canvas.rect(0, panel_h, PAGE_W, 4, fill=1, stroke=0)

    # Texto dentro del panel navy
    canvas.setFillColor(white)
    canvas.setFont('Helvetica-Bold', 11)
    canvas.drawString(ML, panel_h - 44,
                      'Manual de Instalación — Plataforma Geoportal Municipal')
    canvas.setFont('Helvetica', 10)
    canvas.drawString(ML, panel_h - 62,
                      'I. Municipalidad de Algarrobo, Unidad de Informática')
    canvas.setFont('Helvetica', 10)
    canvas.drawString(ML, panel_h - 80, 'Mayo 2026')

    # Logo institucional (texto estilizado, esquina superior izquierda)
    canvas.setFillColor(NAVY)
    canvas.setFont('Helvetica-Bold', 9.5)
    canvas.drawString(ML, PAGE_H - MT + 2, 'Municipalidad')
    canvas.drawString(ML, PAGE_H - MT - 13, 'de Algarrobo')
    canvas.setFillColor(YELLOW)
    canvas.rect(ML, PAGE_H - MT - 19, 76, 2.5, fill=1, stroke=0)

    canvas.restoreState()


def on_content_page(canvas, doc):
    canvas.saveState()

    # Barra navy superior
    canvas.setFillColor(NAVY)
    canvas.rect(ML, PAGE_H - MT + 4 * mm, CONTENT_W, 3, fill=1, stroke=0)

    # Nombre institucional arriba derecha
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(TEXT_LIGHT)
    canvas.drawRightString(PAGE_W - MR, PAGE_H - MT + 5 * mm,
                           'I. Municipalidad de Algarrobo')

    # Footer izquierdo
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(TEXT_LIGHT)
    canvas.drawString(ML, MB - 8 * mm,
                      'Manual de Instalación — Plataforma Algarrobo BASE2')

    # Número de página derecha
    canvas.drawRightString(PAGE_W - MR, MB - 8 * mm, str(doc.page))

    # Línea footer
    canvas.setStrokeColor(GRAY_LINE)
    canvas.setLineWidth(0.5)
    canvas.line(ML, MB - 4 * mm, PAGE_W - MR, MB - 4 * mm)

    canvas.restoreState()


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENTO
# ═══════════════════════════════════════════════════════════════════════════════

class AlgarroboDoc(BaseDocTemplate):
    def __init__(self, path):
        BaseDocTemplate.__init__(
            self, path,
            pagesize=A4,
            leftMargin=ML, rightMargin=MR,
            topMargin=MT, bottomMargin=MB + 1.5 * cm,
        )
        panel_h = PAGE_H * 0.36
        # Frame título: por encima del panel navy
        title_frame = Frame(
            ML, panel_h + 0.8 * cm,
            CONTENT_W, PAGE_H - MT - panel_h - 0.8 * cm,
            id='title'
        )
        # Frame contenido estándar
        content_frame = Frame(
            ML, MB + 1.5 * cm,
            CONTENT_W, PAGE_H - MT - MB - 1.5 * cm,
            id='content'
        )
        self.addPageTemplates([
            PageTemplate(id='Title',   frames=[title_frame],   onPage=on_title_page),
            PageTemplate(id='Content', frames=[content_frame], onPage=on_content_page),
        ])


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENIDO
# ═══════════════════════════════════════════════════════════════════════════════

def build_story():
    story = []

    # ── PÁGINA DE TÍTULO ────────────────────────────────────────────────────────
    story.append(Spacer(1, 2.5 * cm))
    story.append(Paragraph('Manual de Instalación y Despliegue', S('title_main')))
    story.append(Paragraph('Plataforma "Geoportal Municipal"', S('title_sub')))
    story.append(HRFlowable(width='100%', thickness=2.5, color=YELLOW, spaceAfter=14))
    story.append(Paragraph(
        'Guía técnica paso a paso elaborada a partir del despliegue real '
        'en el entorno de preproducción institucional. Incorpora el código '
        'fuente efectivo, la configuración de contenedores y las variables '
        'de entorno requeridas para la implementación sobre la infraestructura '
        'de la Municipalidad de Algarrobo.',
        S('title_desc')
    ))

    story.append(NextPageTemplate('Content'))
    story.append(PageBreak())

    # ── ÍNDICE ─────────────────────────────────────────────────────────────────
    story.append(YellowHeader('Índice'))
    story.append(Spacer(1, 6))

    toc = [
        ('1. Resumen Ejecutivo', '2', 1),
        ('2. Objetivo', '2', 1),
        ('3. Alcance y Limitaciones', '2', 1),
        ('4. Arquitectura de Despliegue Institucional', '3', 1),
        ('    4.1. Capas de Arquitectura', '3', 2),
        ('    4.2. Flujo de Red', '3', 2),
        ('    4.3. Exposición a Internet', '3', 2),
        ('5. Prerrequisitos del Entorno', '4', 1),
        ('6. Flujo de Despliegue por Fases', '5', 1),
        ('    6.1. Fase 1 — Base de Datos (LXC PostgreSQL)', '5', 2),
        ('    6.2. Fase 2 — VM Docker y Portainer', '6', 2),
        ('    6.3. Fase 3 — Dockerfiles y Configuración Nginx', '7', 2),
        ('    6.4. Fase 4 — Orquestación (Docker Compose)', '8', 2),
        ('    6.5. Fase 5 — Despliegue desde Portainer', '9', 2),
        ('    6.6. Fase 6 — Proxy Inverso Externo (Nginx CT)', '10', 2),
        ('    6.7. Fase 7 — Cloudflare Tunnel', '11', 2),
        ('7. Variables de Entorno', '12', 1),
        ('8. Persistencia de Datos', '12', 1),
        ('9. Validación de Despliegue', '13', 1),
        ('10. Consideraciones de Seguridad', '14', 1),
        ('11. Procedimiento de Actualización', '14', 1),
        ('12. Referencia Rápida', '15', 1),
    ]

    toc_rows = []
    for text, pg, lvl in toc:
        st = S('toc1') if lvl == 1 else S('toc2')
        toc_rows.append([Paragraph(text, st), Paragraph(pg, S('toc_pg'))])

    toc_t = Table(toc_rows, colWidths=[CONTENT_W - 1.5 * cm, 1.5 * cm])
    toc_t.setStyle(TableStyle([
        ('LINEBELOW',     (0, 0), (-1, -1), 0.3, GRAY_LINE),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(toc_t)
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. RESUMEN EJECUTIVO
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('1. Resumen Ejecutivo'))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'El presente documento describe el flujo completo de instalación del sistema '
        'Geoportal Municipal (Algarrobo BASE2) dentro de la infraestructura institucional '
        'de la Municipalidad. Fue elaborado a partir del despliegue real realizado en '
        'el entorno de preproducción, con el objetivo de:',
        S('body_j')
    ))
    for b in ['Validar el funcionamiento del sistema en la infraestructura municipal',
              'Ejecutar pruebas de auditoría técnica y de seguridad',
              'Verificar la compatibilidad con la arquitectura institucional de contenedores']:
        story.append(Paragraph(f'• {b}', S('bullet')))

    story.append(Spacer(1, 8))
    story.append(warn_box(
        '<b>Importante:</b> Este documento constituye el manual de instalación definitivo '
        'compatible con la arquitectura institucional de contenedores. '
        'Las variables de entorno <b>nunca</b> se almacenan en archivos '
        '<font face="Courier">.env</font> en el servidor — se inyectan '
        'exclusivamente desde el panel de Portainer.'
    ))

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. OBJETIVO
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('2. Objetivo'))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'Proporcionar al equipo de infraestructura una visión clara y ejecutable del:',
        S('body')
    ))
    for b in ['Modelo de infraestructura institucional utilizado',
              'Flujo de despliegue real con código fuente efectivo',
              'Dependencias externas del sistema y su configuración',
              'Restricciones operativas del entorno institucional']:
        story.append(Paragraph(f'• {b}', S('bullet')))

    # ═══════════════════════════════════════════════════════════════════════════
    # 3. ALCANCE Y LIMITACIONES
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('3. Alcance y Limitaciones'))
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>Alcance</b>', S('subhead')))
    for b in ['Construcción de contenedores Docker (backend y frontend)',
              'Orquestación con Docker Compose gestionado desde Portainer',
              'Configuración de red interna Docker y proxy inverso',
              'Integración con servicios externos (PostgreSQL, proxy Nginx, Cloudflare Tunnel)']:
        story.append(Paragraph(f'• {b}', S('bullet')))

    story.append(Paragraph('<b>Limitaciones</b>', S('subhead')))
    for b in ['No incluye configuración detallada del hipervisor (Proxmox VE)',
              'No incluye políticas completas de seguridad perimetral de red',
              'El esquema SQL de la base de datos debe ser entregado por separado por el equipo de desarrollo']:
        story.append(Paragraph(f'• {b}', S('bullet')))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 4. ARQUITECTURA
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('4. Arquitectura de Despliegue Institucional'))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'La infraestructura utilizada sigue un modelo de segregación por capas, '
        'basado en principios de aislamiento y defensa en profundidad.',
        S('body_j')
    ))

    story.append(YellowHeader('4.1. Capas de Arquitectura', level=2))
    story.append(Spacer(1, 4))

    capas = [
        ('Capa 0 — Hipervisor (Base)',
         'Proxmox VE: plataforma de virtualización que gestiona los recursos '
         'físicos y permite la creación de VMs y Contenedores (CT).'),
        ('Capa 1 — Gateway / Proxy Inverso',
         'CT LXC dedicado (Nginx) que gestiona el tráfico de entrada, terminación '
         'TLS y exposición controlada a internet mediante Cloudflare Tunnel.'),
        ('Capa 2 — Aplicaciones',
         'Máquina Virtual que ejecuta Docker Engine y Portainer. Contiene '
         'geoportal_frontend (Nginx interno) y geoportal_backend (Gunicorn/Flask) '
         'en contenedores orquestados por Docker Compose.'),
        ('Capa 3 — Datos',
         'CT LXC independiente con PostgreSQL. Solo acepta conexiones desde '
         'la Capa 2 por red interna. No expuesto a internet.'),
    ]
    for titulo, desc in capas:
        story.append(Paragraph(f'<b>• {titulo}:</b>', S('bullet')))
        story.append(Paragraph(desc, ParagraphStyle(
            '_cd', fontName='Helvetica', fontSize=10, leading=14,
            textColor=TEXT_MED, leftIndent=26, spaceAfter=6
        )))

    story.append(YellowHeader('4.2. Flujo de Red', level=2))
    story.append(Spacer(1, 4))
    story.append(code_block([
        'Internet',
        '   ↓',
        'Cloudflare Tunnel    (canal seguro saliente — sin exposición de IP pública)',
        '   ↓',
        'Nginx CT — LXC Proxmox    (proxy inverso + TLS, puerto 443)',
        '   ↓',
        'VM Docker    (puerto FRONTEND_DOCKER_PORT, red interna)',
        '   ↓',
        'geoportal_frontend    (Nginx interno, puerto 80, red geoportal_net)',
        '   ↓',
        'geoportal_backend     (Gunicorn/Flask, puerto 8000, red geoportal_net)',
        '   ↓                      ↓',
        'PostgreSQL CT          Volumen Docker /data',
        '(puerto 5432,          ├── docs/',
        ' solo red interna)     ├── fotos_reportes/',
        '                       └── auditoria_reportes/',
    ]))

    story.append(YellowHeader('4.3. Exposición a Internet', level=2))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'La plataforma no expone puertos directamente en la red pública. '
        'Se utiliza <b>Cloudflare Tunnel</b> ejecutándose en el CT Nginx, '
        'creando un canal seguro saliente. Esto permite:',
        S('body')
    ))
    for b in ['Evitar la exposición directa de la IP pública del servidor',
              'Reducir la superficie de ataque perimetral',
              'Centralizar la seguridad en la capa de Cloudflare (WAF, DDoS protection)']:
        story.append(Paragraph(f'• {b}', S('bullet')))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 5. PRERREQUISITOS
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('5. Prerrequisitos del Entorno'))
    story.append(Spacer(1, 6))

    prereq = [
        ['Recurso', 'Especificación', 'Notas'],
        ['Hipervisor',       'Proxmox VE 7.x o superior',                    'Base para VMs y CTs'],
        ['VM Docker',        'Ubuntu 22.04, 4 vCPU, 8 GB RAM, 50 GB disco',  'Capa de aplicaciones'],
        ['CT Nginx',         'Ubuntu 22.04, 1 vCPU, 512 MB RAM',             'Proxy inverso externo'],
        ['CT PostgreSQL',    'Ubuntu 22.04, 2 vCPU, 2 GB RAM, 20 GB disco',  'Base de datos aislada'],
        ['Red interna',      'Subred privada (ej. 192.168.1.0/24)',           'Comunicación entre nodos'],
        ['DNS / Dominio',    'geoportal.munialgarrobo.cl en Cloudflare',      'Proxy Cloudflare activo'],
        ['Cuenta Cloudflare','Acceso al servicio Tunnel (Zero Trust)',         'Para exposición segura'],
        ['Repositorio Git',  'Acceso de lectura a ALGARROBO_BASE2',           'Usuario + token de acceso'],
    ]
    story.append(nav_table(prereq, [3.5*cm, 7.2*cm, 4.8*cm]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 6. FLUJO DE DESPLIEGUE
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('6. Flujo de Despliegue por Fases'))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'El despliegue se realiza mediante Portainer utilizando la funcionalidad '
        'de Stacks desde un repositorio Git, precedido por la instalación de los '
        'servicios de infraestructura en sus respectivos contenedores LXC.',
        S('body_j')
    ))

    # ── 6.1 BASE DE DATOS ──────────────────────────────────────────────────────
    story.append(YellowHeader('6.1. Fase 1 — Base de Datos (LXC PostgreSQL)', level=2))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'Todos los comandos de esta fase se ejecutan dentro del CT LXC de '
        'PostgreSQL, accedido desde la consola de Proxmox.',
        S('note')
    ))

    story.append(Paragraph('<b>Acceso e instalación:</b>', S('subhead')))
    story.append(code_block([
        'pct enter 101   # Reemplazar 101 por el ID real del CT PostgreSQL',
        '',
        'apt-get update && apt-get upgrade -y',
        'apt-get install -y postgresql postgresql-contrib',
        'systemctl enable postgresql && systemctl start postgresql',
    ]))

    story.append(Paragraph('<b>Crear base de datos y usuario dedicado:</b>', S('subhead')))
    story.append(code_block([
        'su - postgres',
        'psql',
        '',
        '-- Dentro de psql — reemplazar PASSWORD_SEGURO por credencial real:',
        "CREATE USER geoportal_user WITH PASSWORD 'PASSWORD_SEGURO';",
        'CREATE DATABASE geoportal_db OWNER geoportal_user;',
        r'\l   -- Verificar que la base de datos aparece en el listado',
        r'\q   -- Salir de psql',
        'exit  -- Salir del usuario postgres',
    ]))

    story.append(Paragraph('<b>Habilitar acceso remoto desde la VM Docker:</b>', S('subhead')))
    story.append(Paragraph(
        'Editar <font face="Courier">/etc/postgresql/14/main/postgresql.conf</font>:',
        S('body')
    ))
    story.append(code_block([
        "listen_addresses = '*'   # Habilitar escucha en todas las interfaces",
    ]))
    story.append(Paragraph(
        'Editar <font face="Courier">/etc/postgresql/14/main/pg_hba.conf</font> '
        'y agregar al final (ajustar subred a la red interna real):',
        S('body')
    ))
    story.append(code_block([
        '# Permitir conexiones desde la VM Docker (subred interna)',
        'host    geoportal_db    geoportal_user    192.168.1.0/24    md5',
    ]))
    story.append(code_block([
        'systemctl restart postgresql',
        '',
        '# Verificar conectividad desde la VM Docker (ejecutar en la VM):',
        'nc -zv 192.168.1.50 5432',
        '# Respuesta esperada: Connection to 192.168.1.50 5432 succeeded!',
    ]))

    story.append(PageBreak())

    # ── 6.2 VM DOCKER ──────────────────────────────────────────────────────────
    story.append(YellowHeader('6.2. Fase 2 — VM Docker y Portainer', level=2))
    story.append(Spacer(1, 4))

    story.append(Paragraph('<b>Instalar Docker Engine (repositorio oficial):</b>', S('subhead')))
    story.append(code_block([
        'apt-get update && apt-get install -y curl git ca-certificates gnupg',
        '',
        '# Agregar clave GPG oficial de Docker',
        'install -m 0755 -d /etc/apt/keyrings',
        'curl -fsSL https://download.docker.com/linux/ubuntu/gpg \\',
        '    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg',
        'chmod a+r /etc/apt/keyrings/docker.gpg',
        '',
        '# Agregar repositorio',
        'echo \\',
        '  "deb [arch=$(dpkg --print-architecture) \\',
        '  signed-by=/etc/apt/keyrings/docker.gpg] \\',
        '  https://download.docker.com/linux/ubuntu \\',
        '  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \\',
        '  | tee /etc/apt/sources.list.d/docker.list > /dev/null',
        '',
        'apt-get update',
        'apt-get install -y docker-ce docker-ce-cli containerd.io \\',
        '    docker-buildx-plugin docker-compose-plugin',
        '',
        'systemctl enable docker && systemctl start docker',
        'docker --version && docker compose version',
    ]))

    story.append(Paragraph('<b>Desplegar Portainer:</b>', S('subhead')))
    story.append(code_block([
        '# Crear volumen persistente para Portainer',
        'docker volume create portainer_data',
        '',
        '# Levantar Portainer (panel de administración de contenedores)',
        'docker run -d \\',
        '    --name portainer \\',
        '    --restart=always \\',
        '    -p 9000:9000 \\',
        '    -p 9443:9443 \\',
        '    -v /var/run/docker.sock:/var/run/docker.sock \\',
        '    -v portainer_data:/data \\',
        '    portainer/portainer-ce:latest',
        '',
        '# Acceder desde la red interna municipal:',
        '# http://<IP_VM_DOCKER>:9000',
        '# En el primer acceso: crear usuario administrador y anotar credenciales',
    ]))
    story.append(warn_box(
        '<b>Seguridad:</b> El puerto 9000 de Portainer <b>nunca debe exponerse a internet</b>. '
        'El acceso al panel de administración debe ser exclusivamente desde '
        'la red interna municipal.'
    ))

    story.append(PageBreak())

    # ── 6.3 DOCKERFILES ────────────────────────────────────────────────────────
    story.append(YellowHeader('6.3. Fase 3 — Dockerfiles y Configuración Nginx', level=2))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'Los archivos Dockerfile y la configuración de Nginx deben existir en '
        'la raíz del repositorio Git con el siguiente contenido exacto:',
        S('body')
    ))

    story.append(Paragraph('<b>backend.Dockerfile</b>', S('subhead')))
    story.append(code_block([
        '# Imagen base Python slim — reduce la superficie del contenedor',
        'FROM python:3.10-slim',
        '',
        'WORKDIR /app',
        '',
        '# Dependencias del sistema:',
        '#   libpq-dev + gcc    → compilar psycopg2 para PostgreSQL',
        '#   poppler-utils      → extracción de texto desde archivos PDF',
        '#   tesseract-ocr      → motor OCR para imágenes y documentos escaneados',
        '#   tesseract-ocr-spa  → modelo de idioma español para OCR',
        'RUN apt-get update && apt-get install -y \\',
        '    libpq-dev \\',
        '    gcc \\',
        '    poppler-utils \\',
        '    tesseract-ocr \\',
        '    tesseract-ocr-spa \\',
        '    && rm -rf /var/lib/apt/lists/*',
        '',
        '# Crear directorio del volumen persistente',
        'RUN mkdir -p /data',
        '',
        '# Instalar dependencias Python antes de copiar el código',
        '# (optimiza el uso de la caché de capas de Docker en actualizaciones)',
        'COPY backend/requirements.txt .',
        'RUN pip install --no-cache-dir -r requirements.txt',
        '',
        '# Copiar el código fuente del backend',
        'COPY backend/ ./backend/',
        '',
        'WORKDIR /app/backend',
        '',
        'EXPOSE 8000',
        '',
        '# 4 workers × 2 threads = 8 requests concurrentes',
        '# --timeout 300s → soporta procesamiento OCR y generación de PDF',
        'CMD ["gunicorn", "app_railway:app",',
        '     "--bind", "0.0.0.0:8000",',
        '     "--workers", "4",',
        '     "--threads", "2",',
        '     "--timeout", "300"]',
    ]))

    story.append(Paragraph('<b>frontend.Dockerfile</b>', S('subhead')))
    story.append(code_block([
        '# Nginx Alpine: imagen mínima para servir archivos estáticos',
        'FROM nginx:alpine',
        '',
        '# Configuración del proxy interno (ruteo /api/ → backend)',
        'COPY nginx.conf /etc/nginx/conf.d/default.conf',
        '',
        '# Archivos estáticos del frontend (HTML, JS, CSS, assets)',
        'COPY frontend/ /usr/share/nginx/html',
        '',
        'EXPOSE 80',
        'CMD ["nginx", "-g", "daemon off;"]',
    ]))

    story.append(Paragraph('<b>nginx.conf (Nginx interno del contenedor frontend)</b>', S('subhead')))
    story.append(code_block([
        'server {',
        '    listen 80;',
        '',
        '    location = /frontend {',
        '        return 301 /frontend/;',
        '    }',
        '',
        '    location /frontend/ {',
        '        alias /usr/share/nginx/html/;',
        '        index index.html;',
        '        try_files $uri $uri/ /index.html;',
        '    }',
        '',
        '    # Servir archivos estáticos del frontend',
        '    location / {',
        '        root /usr/share/nginx/html;',
        '        index index.html;',
        '        try_files $uri $uri/ /index.html;',
        '    }',
        '',
        '    # Proxy inverso: redirigir /api/ al contenedor backend.',
        '    # "backend" resuelve por DNS interno de la red Docker geoportal_net.',
        '    location /api/ {',
        '        proxy_pass http://backend:8000;',
        '        proxy_set_header Host $host;',
        '        proxy_set_header X-Real-IP $remote_addr;',
        '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;',
        '        proxy_set_header X-Forwarded-Proto $http_x_forwarded_proto;',
        '    }',
        '}',
    ]))

    story.append(PageBreak())

    # ── 6.4 DOCKER COMPOSE ─────────────────────────────────────────────────────
    story.append(YellowHeader('6.4. Fase 4 — Orquestación (Docker Compose)', level=2))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'Este archivo define la jerarquía de los servicios, la red interna '
        '<font face="Courier">geoportal_net</font> y la persistencia del '
        'volumen <font face="Courier">geoportal_data</font>. '
        'Debe existir en la raíz del repositorio con el nombre '
        '<font face="Courier">docker-compose.yml</font>.',
        S('body_j')
    ))
    story.append(code_block([
        'version: "3.8"',
        '',
        'services:',
        '  backend:',
        '    build:',
        '      context: .',
        '      dockerfile: backend.Dockerfile',
        '    container_name: geoportal_backend',
        '    restart: always',
        '    volumes:',
        '      - geoportal_data:/data   # Volumen persistente para docs y reportes',
        '    networks:',
        '      - geoportal_net',
        '    # Variables de entorno inyectadas desde Portainer (no desde .env)',
        '',
        '  frontend:',
        '    build:',
        '      context: .',
        '      dockerfile: frontend.Dockerfile',
        '    container_name: geoportal_frontend',
        '    restart: always',
        '    depends_on:',
        '      - backend',
        '    ports:',
        '      # Puerto expuesto en la VM (accesible desde el CT Nginx externo)',
        '      - "${FRONTEND_DOCKER_PORT}:80"',
        '    networks:',
        '      - geoportal_net',
        '',
        'networks:',
        '  geoportal_net:',
        '    driver: bridge   # Red interna aislada entre frontend y backend',
        '',
        'volumes:',
        '  geoportal_data:    # Persiste entre redeployments del contenedor',
    ]))

    story.append(PageBreak())

    # ── 6.5 PORTAINER ──────────────────────────────────────────────────────────
    story.append(YellowHeader('6.5. Fase 5 — Despliegue desde Portainer', level=2))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'El despliegue se realiza mediante Portainer utilizando la funcionalidad '
        'de <b>Stacks</b> desde el repositorio Git.',
        S('body')
    ))

    story.append(Paragraph('<b>Resumen Operativo:</b>', S('subhead')))

    steps = [
        ('1', 'Acceder a Portainer → <b>Stacks → Add stack</b>'),
        ('2', 'Seleccionar <b>"Repository"</b> como método de despliegue'),
        ('3', 'Completar configuración: Name = <font face="Courier">geoportal</font>, '
              'URL del repositorio Git, Branch = <font face="Courier">main</font>, '
              'Compose path = <font face="Courier">docker-compose.yml</font>'),
        ('4', 'Si el repositorio es privado: activar <b>"Authentication"</b> '
              'e ingresar usuario y token de acceso personal (PAT)'),
        ('5', 'En la sección <b>"Environment variables"</b>, definir todas las '
              'variables de la Sección 7 de este documento'),
        ('6', 'Hacer clic en <b>"Deploy the stack"</b>'),
        ('7', 'Monitorear el progreso en <b>Logs</b> — la primera construcción '
              'toma entre 5 y 15 minutos'),
    ]

    for num, step in steps:
        row_data = [[
            Paragraph(num, ParagraphStyle(
                '_sn', fontName='Helvetica-Bold', fontSize=10,
                textColor=white, alignment=TA_CENTER
            )),
            Paragraph(step, S('body'))
        ]]
        t = Table(row_data, colWidths=[0.9*cm, CONTENT_W - 1.3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (0, 0), NAVY),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
            ('TOPPADDING',    (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('SPACEAFTER',    (0, 0), (-1, -1), 3),
        ]))
        story.append(t)
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 8))
    story.append(Paragraph('<b>Actualización del sistema:</b>', S('subhead')))
    story.append(code_block([
        '# 1. El equipo de desarrollo sube los cambios al repositorio',
        'git push origin main',
        '',
        '# 2. En Portainer:',
        '#    Stacks → geoportal → "Pull and redeploy"',
        '',
        '# Portainer ejecuta internamente:',
        '#   a) git pull  (descarga cambios del repositorio)',
        '#   b) docker build  (reconstruye imágenes con los cambios)',
        '#   c) docker compose up -d  (reinicia contenedores)',
        '',
        '# Tiempo estimado de downtime: 30 a 60 segundos',
    ]))

    story.append(PageBreak())

    # ── 6.6 NGINX EXTERNO ──────────────────────────────────────────────────────
    story.append(YellowHeader('6.6. Fase 6 — Proxy Inverso Externo (Nginx CT)', level=2))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'A continuación se presenta la configuración del proxy inverso externo. '
        'Se han conservado únicamente las directivas esenciales para el despliegue '
        'y comunicación del Geoportal. Los certificados SSL se configuran '
        'por separado (ver nota).',
        S('body_j')
    ))

    story.append(Paragraph('<b>Instalar Nginx en el CT:</b>', S('subhead')))
    story.append(code_block([
        'pct enter 100   # Acceder al CT Nginx desde Proxmox',
        '',
        'apt-get update && apt-get install -y nginx',
        'systemctl enable nginx && systemctl start nginx',
    ]))

    story.append(Paragraph(
        '<b>Archivo: /etc/nginx/sites-available/geoportal.conf</b>', S('subhead')
    ))
    story.append(Paragraph(
        'Reemplazar <font face="Courier">&lt;IP_VM_DOCKER&gt;</font> por la IP real '
        'de la VM Docker y <font face="Courier">&lt;FRONTEND_DOCKER_PORT&gt;</font> '
        'por el valor definido en Portainer:',
        S('body')
    ))
    story.append(code_block([
        'server {',
        '    listen 80;',
        '    server_name geoportal.munialgarrobo.cl;',
        '    # Redirigir tráfico HTTP a HTTPS',
        '    return 301 https://$host$request_uri;',
        '}',
        '',
        'server {',
        '    listen 443 ssl;',
        '    http2 on;',
        '    server_name geoportal.munialgarrobo.cl;',
        '',
        '    # Límite de subida de archivos (coincidir con MAX_UPLOAD_MB del backend)',
        '    client_max_body_size 50M;',
        '',
        '    # Recuperar IP real del cliente desde Cloudflare',
        '    real_ip_header CF-Connecting-IP;',
        '    set_real_ip_from 127.0.0.1;',
        '    real_ip_recursive on;',
        '',
        '    location / {',
        '        # Apunta a la IP de la VM Docker + puerto del Frontend',
        '        proxy_pass http://<IP_VM_DOCKER>:<FRONTEND_DOCKER_PORT>;',
        '',
        '        # Cabeceras estándar de enrutamiento',
        '        proxy_set_header Host $host;',
        '        proxy_set_header X-Real-IP $remote_addr;',
        '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;',
        '        proxy_set_header X-Forwarded-Proto $scheme;',
        '',
        '        # Recuperar la IP original desde Cloudflare',
        '        proxy_set_header CF-Connecting-IP $http_cf_connecting_ip;',
        '',
        '        # Timeouts extendidos para OCR y generación de PDF',
        '        proxy_connect_timeout 90s;',
        '        proxy_send_timeout 300s;',
        '        proxy_read_timeout 300s;',
        '    }',
        '}',
    ]))
    story.append(code_block([
        'ln -s /etc/nginx/sites-available/geoportal.conf /etc/nginx/sites-enabled/',
        'nginx -t          # Verificar sintaxis — debe decir "syntax is ok"',
        'systemctl reload nginx',
    ]))

    story.append(PageBreak())

    # ── 6.7 CLOUDFLARE TUNNEL ──────────────────────────────────────────────────
    story.append(YellowHeader('6.7. Fase 7 — Cloudflare Tunnel', level=2))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'Cloudflare Tunnel se instala en el mismo CT Nginx y crea un canal '
        'saliente seguro, eliminando la necesidad de abrir puertos en el '
        'firewall perimetral institucional.',
        S('body_j')
    ))

    story.append(Paragraph('<b>Instalar cloudflared:</b>', S('subhead')))
    story.append(code_block([
        'curl -L --output cloudflared.deb \\',
        '    https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb',
        'dpkg -i cloudflared.deb',
        'cloudflared --version',
    ]))

    story.append(Paragraph('<b>Autenticar y crear el tunnel:</b>', S('subhead')))
    story.append(code_block([
        '# Autenticar (abre URL — completar en el navegador seleccionando el dominio)',
        'cloudflared tunnel login',
        '',
        '# Crear tunnel institucional',
        'cloudflared tunnel create geoportal-tunnel',
        '',
        '# Registrar DNS en Cloudflare automáticamente',
        'cloudflared tunnel route dns geoportal-tunnel geoportal.munialgarrobo.cl',
    ]))

    story.append(Paragraph(
        '<b>Archivo: /etc/cloudflared/config.yml</b>', S('subhead')
    ))
    story.append(code_block([
        'tunnel: <ID_DEL_TUNNEL_GENERADO>',
        'credentials-file: /root/.cloudflared/<ID_DEL_TUNNEL_GENERADO>.json',
        '',
        'ingress:',
        '  - hostname: geoportal.munialgarrobo.cl',
        '    service: https://localhost:443',
        '    originRequest:',
        '      noTLSVerify: true   # Si se usa certificado de origen auto-firmado',
        '  - service: http_status:404',
    ]))
    story.append(code_block([
        '# Instalar como servicio del sistema y habilitar al inicio',
        'cloudflared service install',
        'systemctl enable cloudflared',
        'systemctl start cloudflared',
        'systemctl status cloudflared   # Debe mostrar "active (running)"',
    ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 7. VARIABLES DE ENTORNO
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('7. Variables de Entorno'))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'Las variables no se gestionan mediante archivo '
        '<font face="Courier">.env</font> en el servidor, sino mediante:',
        S('body')
    ))
    story.append(Paragraph(
        '<b>Portainer → Stacks → geoportal → Environment variables</b>',
        ParagraphStyle('_pp', fontName='Helvetica-Bold', fontSize=10,
                       textColor=NAVY, leading=16, leftIndent=14, spaceAfter=10)
    ))

    env_data = [
        ['Variable', 'Descripción', 'Valor de referencia'],
        ['DATABASE_URL',          'Cadena de conexión PostgreSQL completa',
         'postgresql://geoportal_user:PASS\n@192.168.1.50:5432/geoportal_db'],
        ['JWT_SECRET_KEY',        'Clave para firmar tokens JWT (mín. 32 chars)',
         'Generar: openssl rand -hex 32'],
        ['ALLOWED_ORIGINS',       'Orígenes CORS permitidos (separados por coma)',
         'https://geoportal.munialgarrobo.cl'],
        ['FLASK_ENV',             'Entorno de ejecución',                'production'],
        ['FLASK_DEBUG',           'Modo debug (siempre False en producción)', 'False'],
        ['PORT',                  'Puerto interno del backend',           '8000'],
        ['FRONTEND_DOCKER_PORT',  'Puerto expuesto de la VM al CT Nginx', '8080'],
        ['APP_HOST',              'Hostname público de la aplicación',    'geoportal.munialgarrobo.cl'],
        ['SESSION_EXPIRY_HOURS',  'Horas de validez de sesión JWT',       '24'],
        ['AUDIT_OUT_DIR',         'Directorio de reportes de auditoría',  '/data/auditoria_reportes'],
        ['MAX_UPLOAD_MB',         'Límite de subida de archivos (MB)',     '50'],
    ]

    cw = [4.2*cm, 6.0*cm, CONTENT_W - 4.2*cm - 6.0*cm]
    env_t = Table(env_data, colWidths=cw)
    env_t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR',     (0, 0), (-1, 0), white),
        ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0), 9),
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
        ('FONTNAME',      (0, 1), (0, -1), 'Courier'),
        ('FONTSIZE',      (0, 1), (-1, -1), 8.5),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [white, GRAY_LIGHT]),
        ('GRID',          (0, 0), (-1, -1), 0.4, GRAY_LINE),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR',     (0, 1), (-1, -1), TEXT_DARK),
    ]))
    story.append(env_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        '<b>Nota:</b> Listado no exhaustivo. El equipo de desarrollo debe '
        'proveer la lista definitiva completa con todas las variables requeridas.',
        S('note')
    ))
    story.append(code_block([
        '# Generar JWT_SECRET_KEY de forma segura (ejecutar en cualquier terminal):',
        'openssl rand -hex 32',
        '# Ejemplo de salida:',
        '# a3f2c8e1d5b4a7f9e2c1d8b5a3f2c8e1d5b4a7f9e2c1d8b5a3f2c8e1d5b4a7f9',
    ]))

    # ═══════════════════════════════════════════════════════════════════════════
    # 8. PERSISTENCIA DE DATOS
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('8. Persistencia de Datos'))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'Se utiliza el volumen Docker <font face="Courier">geoportal_data</font> '
        'que monta el directorio <font face="Courier">/data</font> dentro del '
        'contenedor backend:',
        S('body')
    ))
    story.append(code_block([
        '/data/',
        '  ├── docs/               # Documentos subidos por funcionarios',
        '  │     └── (PDF, DOCX, XLSX, imágenes...)',
        '  ├── fotos_reportes/     # Fotografías de reportes de inspección',
        '  │     └── (JPG, PNG...)',
        '  └── auditoria_reportes/ # Reportes PDF generados por el sistema',
        '        └── (archivos PDF generados automáticamente)',
    ]))
    story.append(Paragraph(
        'En <font face="Courier">FLASK_ENV=production</font>, si el volumen '
        '<font face="Courier">/data</font> no está montado, el backend '
        '<b>falla explícitamente</b> al arrancar, evitando pérdida silenciosa de datos.',
        S('body_j')
    ))
    story.append(code_block([
        '# Verificar que el volumen existe en la VM Docker:',
        'docker volume ls | grep geoportal',
        '',
        '# Verificar estructura interna y modo de storage del backend:',
        'docker exec geoportal_backend ls -la /data/',
        'docker logs geoportal_backend | grep -i storage',
        '# Salida esperada: STORAGE: /data/docs',
    ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 9. VALIDACIÓN DE DESPLIEGUE
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('9. Validación de Despliegue'))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'Una vez levantado el sistema, verificar sistemáticamente '
        'cada componente:',
        S('body')
    ))

    story.append(Paragraph('<b>Acceso al Frontend:</b>', S('subhead')))
    story.append(code_block([
        'docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"',
        '',
        '# Salida esperada:',
        '# NAMES                  STATUS          PORTS',
        '# geoportal_frontend     Up X minutes    0.0.0.0:8080->80/tcp',
        '# geoportal_backend      Up X minutes',
    ]))

    story.append(Paragraph('<b>Respuesta del Backend (/health):</b>', S('subhead')))
    story.append(code_block([
        'curl http://localhost:8080/health',
        '',
        '# Respuesta esperada (HTTP 200):',
        '# {',
        '#   "status": "healthy",',
        '#   "database": {"status": "connected"},',
        '#   "storage": {"active_root": "/data/docs"},',
        '#   "railway_optimized": true',
        '# }',
    ]))

    story.append(Paragraph('<b>Respuesta de la API (/api/):</b>', S('subhead')))
    story.append(code_block([
        'curl http://localhost:8080/api/',
        '',
        '# Respuesta esperada:',
        '# {',
        '#   "message": "SECPLAC ALGARROBO API - Railway Edition",',
        '#   "storage_mode": "Volume /data",',
        '#   "status": "online"',
        '# }',
    ]))

    story.append(Paragraph('<b>Acceso externo HTTPS:</b>', S('subhead')))
    story.append(code_block([
        'curl -I https://geoportal.munialgarrobo.cl/',
        '# Respuesta esperada: HTTP/2 200',
        '',
        '# Verificar logs sin errores críticos:',
        'docker logs geoportal_backend | tail -20',
    ]))

    story.append(Spacer(1, 8))
    story.append(Paragraph('<b>Errores comunes y resolución:</b>', S('subhead')))
    err_data = [
        ['Error observado', 'Causa probable', 'Resolución'],
        ['ValueError: DATABASE_URL no configurada',
         'Variable no definida en Portainer',
         'Portainer → Stack → Environment variables'],
        ['connection refused (host 192.168.1.50, port 5432)',
         'CT PostgreSQL inaccesible por red o pg_hba.conf',
         'Verificar IP, subred en pg_hba.conf y restart PostgreSQL'],
        ['STORAGE ERROR: /data no está montado',
         'Volumen no definido en docker-compose.yml',
         'Verificar sección volumes: en docker-compose.yml'],
        ['HTTP 502 Bad Gateway',
         'Backend no levantado o caído',
         'docker logs geoportal_backend para ver error'],
        ['nginx: configuration file test failed',
         'Error de sintaxis en geoportal.conf',
         'nginx -t y revisar el mensaje de error exacto'],
    ]
    story.append(nav_table(err_data, [4.5*cm, 5.0*cm, CONTENT_W - 9.5*cm]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 10. CONSIDERACIONES DE SEGURIDAD
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('10. Consideraciones de Seguridad'))
    story.append(Spacer(1, 4))

    seg = [
        ('Backend no expuesto directamente a internet',
         'geoportal_backend no mapea puertos a la VM. Solo accesible dentro '
         'de la red Docker geoportal_net desde el contenedor frontend.'),
        ('Base de datos aislada en red interna',
         'PostgreSQL en CT LXC independiente, solo acepta conexiones desde '
         'la subred interna (pg_hba.conf). No expuesto en ningún puerto público.'),
        ('Uso obligatorio de HTTPS',
         'El CT Nginx redirige todo HTTP a HTTPS (puerto 443). '
         'Cloudflare Tunnel también fuerza HTTPS en la capa pública.'),
        ('Variables sensibles fuera del código',
         'JWT_SECRET_KEY, DATABASE_URL y credenciales de APIs externas se '
         'definen exclusivamente en Portainer. Nunca en el repositorio Git.'),
        ('CORS restrictivo en producción',
         'Con FLASK_ENV=production, ALLOWED_ORIGINS es obligatoria. Si no '
         'está configurada el sistema rechaza el arranque con ValueError.'),
        ('Validación de archivos subidos',
         'El backend valida extensión y magic bytes del archivo. Límite '
         'de 50 MB por defecto (configurable por MAX_UPLOAD_MB).'),
        ('Control de acceso por roles (RBAC)',
         'Endpoints protegidos con @session_required y @role_required. '
         'admin_general (nivel 10) y admin_proyectos (nivel 11) con acceso diferenciado.'),
    ]

    for titulo, desc in seg:
        story.append(Paragraph(f'<b>• {titulo}:</b>', S('bullet')))
        story.append(Paragraph(desc, ParagraphStyle(
            '_sd', fontName='Helvetica', fontSize=10, leading=14,
            textColor=TEXT_MED, leftIndent=16, spaceAfter=7
        )))

    # ═══════════════════════════════════════════════════════════════════════════
    # 11. ACTUALIZACIÓN DEL SISTEMA
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('11. Procedimiento de Actualización'))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'El proceso de actualización se realiza mediante:',
        S('body')
    ))

    upd_steps = [
        'Push de cambios al repositorio Git',
        'Ejecución de <b>"Pull and redeploy"</b> desde Portainer',
    ]
    for b in upd_steps:
        story.append(Paragraph(f'• {b}', S('bullet')))

    story.append(code_block([
        '# Rollback de emergencia — desde Portainer:',
        '# Stacks → geoportal → Editor',
        '# Cambiar "Repository reference" al commit anterior',
        '# → "Update the stack"',
        '',
        '# Backup de base de datos (ejecutar en CT PostgreSQL):',
        'pg_dump "postgresql://geoportal_user:PASS@localhost:5432/geoportal_db" \\',
        '    -Fc -f /backups/geoportal_$(date +%Y%m%d_%H%M).dump',
        '',
        '# Backup del volumen Docker (ejecutar en VM Docker):',
        'docker run --rm \\',
        '    -v geoportal_geoportal_data:/data \\',
        '    -v /backups:/backup \\',
        '    alpine tar czf /backup/geoportal_data_$(date +%Y%m%d).tar.gz /data',
    ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 12. REFERENCIA RÁPIDA
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(YellowHeader('12. Referencia Rápida'))
    story.append(Spacer(1, 6))

    story.append(Paragraph('<b>Puertos y comunicaciones:</b>', S('subhead')))
    ports = [
        ['Origen', 'Destino', 'Puerto', 'Protocolo', 'Propósito'],
        ['Internet',              'Cloudflare',          '443',                 'HTTPS',      'Tráfico público'],
        ['Cloudflare',            'CT Nginx',            '443',                 'HTTPS',      'Tunnel Cloudflare'],
        ['CT Nginx',              'VM Docker',           'FRONTEND_DOCKER_PORT','HTTP',       'Proxy al frontend'],
        ['geoportal_frontend',    'geoportal_backend',   '8000',               'HTTP interno','API REST'],
        ['geoportal_backend',     'CT PostgreSQL',       '5432',               'PostgreSQL', 'Base de datos'],
        ['Admin (red interna)',   'VM Docker',           '9000',               'HTTP',       'Panel Portainer'],
    ]
    story.append(nav_table(ports, [3.5*cm, 3.5*cm, 3.2*cm, 2.5*cm, CONTENT_W - 12.7*cm]))

    story.append(Spacer(1, 14))
    story.append(Paragraph('<b>Archivos de configuración:</b>', S('subhead')))
    files = [
        ['Archivo', 'Ubicación', 'Propósito'],
        ['backend.Dockerfile',  'Raíz del repositorio',                    'Imagen Docker backend Python/Gunicorn'],
        ['frontend.Dockerfile', 'Raíz del repositorio',                    'Imagen Docker frontend Nginx'],
        ['nginx.conf',          'Raíz del repositorio',                    'Nginx interno (proxy /api/ → backend)'],
        ['docker-compose.yml',  'Raíz del repositorio',                    'Orquestación de servicios'],
        ['geoportal.conf',      '/etc/nginx/sites-available/ (CT Nginx)',   'Proxy inverso externo con TLS'],
        ['config.yml',          '/etc/cloudflared/ (CT Nginx)',             'Configuración Cloudflare Tunnel'],
    ]
    story.append(nav_table(files, [4.0*cm, 5.5*cm, CONTENT_W - 9.5*cm]))

    story.append(Spacer(1, 24))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GRAY_LINE, spaceAfter=12))
    story.append(Paragraph(
        'Manual elaborado a partir de la Guía de Despliegue y Arquitectura Institucional '
        '— Geoportal Municipal (Abril 2026)',
        S('footer_note')
    ))
    story.append(Paragraph(
        'I. Municipalidad de Algarrobo — Unidad de Informática — Mayo 2026',
        S('footer_inst')
    ))

    return story


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    doc   = AlgarroboDoc(OUTPUT_PATH)
    story = build_story()
    doc.build(story)
    print(f'PDF generado: {OUTPUT_PATH}')
