import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)
from reportlab.pdfgen import canvas

BASE_DIR = r"c:\Users\Nasrallah\Downloads\chat-812c8388-89f0-4c7c-88f6-7e872379485d"
PDF_PATH = os.path.join(BASE_DIR, "WebApp_Architecture_and_UserGuide.pdf")
IMG_ARCH = os.path.join(BASE_DIR, "webapp_architecture_diagram.png")
IMG_FLOW = os.path.join(BASE_DIR, "webapp_userflow_diagram.png")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Top banner line
        self.setStrokeColor(colors.HexColor("#0284C7"))
        self.setLineWidth(1.5)
        self.line(40, letter[1] - 35, letter[0] - 40, letter[1] - 35)

        # Header text
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(40, letter[1] - 28, "FIRE RISK SIMULATION WEB APPLICATION — SYSTEM ARCHITECTURE & USER MANUAL")

        # Bottom footer line
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(1)
        self.line(40, 42, letter[0] - 40, 42)

        # Footer text & page number
        self.setFont("Helvetica", 8)
        self.drawString(40, 30, "WEB APP ARCHITECTURE SPECIFICATION | PLOTLY.JS + CLIENT ENGINE + GEMINI API")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 40, 30, page_str)
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=19,
        leading=23,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0369A1'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.6,
        leading=12.2,
        textColor=colors.HexColor('#334155'),
        spaceAfter=5
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.2,
        textColor=colors.HexColor('#1E293B')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("FIRE RISK SIMULATOR: WEB APP ARCHITECTURE & USER GUIDE", title_style))
    story.append(Paragraph("System Blueprint, Computer-Style Schematics, Prediction Pipeline & Operational Flow", subtitle_style))

    meta_data = [
        [
            Paragraph("<b>Platform:</b> Interactive Web Application", table_cell_style),
            Paragraph("<b>Engine:</b> Plotly.js + Reactive Bus", table_cell_style),
            Paragraph("<b>Reading Time:</b> ~2-3 Minutes", table_cell_style),
            Paragraph("<b>Standard:</b> NASA 5x4 Risk Matrix", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[130, 145, 125, 132])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F9FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BAE6FD')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # Section 1: Problématique
    story.append(Paragraph("1. PROBLÉMATIQUE (WHAT PROBLEMS DOES THIS WEB APP SOLVE?)", h1_style))
    prob_text = (
        "Analyzing high-speed telemetry and calculating multi-dimensional safety risk in critical operations faces four major web engineering challenges:<br/>"
        "<b>• High-Frequency Telemetry Overload:</b> Rendering 2,000 to 6,000 live telemetry points across multiple subplots causes conventional DOM-based web apps to lag or crash. "
        "The web app solves this through an in-memory cached buffer and hardware-accelerated WebGL/SVG graphics running at 60 FPS.<br/>"
        "<b>• Cognitive Overload for Human Operators:</b> Looking at raw numbers (880 psi, 22.9A, 38°F) makes it impossible for an operator to gauge overall danger instantly. "
        "The web app translates multi-sensor raw streams into the standardized <b>NASA 5x4 Risk Matrix</b> with clear color-coded zones (GREEN to RED).<br/>"
        "<b>• Static vs. Interactive Time-Travel:</b> Static PDF reports cannot show dynamic progression. The web app introduces a <b>time-scrubbing slider</b> "
        "allowing operators to replay, slow down, and zoom into critical incident seconds (such as the 90-second explosion window).<br/>"
        "<b>• Lack of Real-Time Explanations:</b> An alarm buzzer alone creates panic. The web app bridges mathematical detection with <b>AI contextual reasoning (Gemini API)</b> "
        "to deliver natural language root-cause diagnosis and actionable mitigation procedures directly inside the user interface."
    )
    story.append(Paragraph(prob_text, body_style))
    story.append(Spacer(1, 6))

    # Section 2: Computer Architecture Style Schematic
    story.append(Paragraph("2. WEB APPLICATION ARCHITECTURE (COMPUTER HARDWARE ABSTRACTION)", h1_style))
    arch_intro = (
        "The web application is architected analogous to a modern computing system, featuring dedicated buses, processing ALUs, memory registers, and presentation controllers:"
    )
    story.append(Paragraph(arch_intro, body_style))

    if os.path.exists(IMG_ARCH):
        story.append(Image(IMG_ARCH, width=7.2*inch, height=4.0*inch))
        story.append(Spacer(1, 4))

    arch_desc = (
        "<b>Architectural Components Breakdown:</b><br/>"
        "<b>1. Client UI & Controls (I/O Unit):</b> Manages user inputs, tab routing, timeline slider scrubbing (0 to 143 hours), and hover overlays.<br/>"
        "<b>2. Render & Graphics ALU (GPU Equivalent):</b> High-performance Plotly.js engine rendering synchronized subplots and 5x4 heatmap matrices.<br/>"
        "<b>3. Alert & Sound HUD (Interrupt Controller):</b> Triggers visual flash banners, toast alerts, and T-minus counters when RPN exceeds critical limits (RPN &gt; 15).<br/>"
        "<b>4. In-Memory Cache (RAM / L1 Store):</b> Holds the full 2k-6k telemetry JSON payload in browser memory for instant O(1) random-access scrubbing without server latency.<br/>"
        "<b>5. Web Worker Prediction ALU (Math Coprocessor):</b> Executes derivatives (dP/dt) and machine learning inference off the UI main thread to prevent frame drops.<br/>"
        "<b>6. External API Gateway (Network Bus):</b> Interfaces with backend streaming endpoints (FastAPI) and intelligent generative safety agents (Google Gemini API)."
    )
    story.append(Paragraph(arch_desc, body_style))

    story.append(PageBreak())

    # Section 3: Prediction Mechanism & APIs
    story.append(Paragraph("3. PREDICTION IN THE WEB APP: HOW IT WORKS & AVAILABLE APIs", h1_style))
    pred_intro = (
        "Prediction inside the web application operates on a <b>two-tier hybrid model</b> combining fast client-side statistical inference with intelligent cloud AI reasoning:"
    )
    story.append(Paragraph(pred_intro, body_style))

    if os.path.exists(IMG_FLOW):
        story.append(Image(IMG_FLOW, width=7.2*inch, height=2.8*inch))
        story.append(Spacer(1, 6))

    story.append(Paragraph("A. How the Client-Side Prediction Algorithm Works", h2_style))
    pred_details = (
        "<b>• Sliding-Window Derivative Core:</b> As the user scrubs the slider or live streaming plays, a 30-second sliding window computes "
        "the first derivative of pressure (dP/dt) and current transients (dI/dt). If a sudden pressure surge coincides with an electrical anomaly, "
        "the system upgrades the Likelihood score from Level 1 (Improbable) to Level 4 (Probable) before nominal safety thresholds are breached.<br/>"
        "<b>• Time-Series Vector Projection:</b> A lightweight client-side model (ONNX Web / TensorFlow.js running in a Web Worker) projects sensor curves "
        "90 seconds into the future. If projected pressure touches 1,008 psi, the application sounds an early warning alarm.<br/>"
        "<b>• Dynamic RPN Recalculation:</b> Risk Priority Number (RPN = Severity x Likelihood) updates reactively at 60 FPS, shifting UI elements from GREEN to RED."
    )
    story.append(Paragraph(pred_details, body_style))

    story.append(Paragraph("B. Does an External API Exist? How Can We Integrate One?", h2_style))
    api_details = (
        "<b>• Are there ready-made public fire prediction APIs?</b> No. NASA and aerospace agencies do not expose a public real-time fire detection API. "
        "NASA provides raw datasets and open mission logs (via <i>data.nasa.gov</i>). Therefore, the prediction engine must be implemented as a custom module.<br/>"
        "<b>• Custom Microservice Option (FastAPI / WebSockets):</b> For production systems, raw sensor streams are pushed to a Python FastAPI backend "
        "running PyTorch/ONNX inference, which streams predictions back to the web application over low-latency WebSockets.<br/>"
        "<b>• Generative Safety Agent via Google Gemini API:</b> The web app can integrate the <b>Gemini API</b> as a real-time safety advisor. "
        "When an RPN anomaly is detected, the web app posts the sensor snapshot to Gemini. Gemini analyzes the telemetry context, queries pre-loaded "
        "engineering defect playbooks, and returns an instant natural-language explanation (e.g., <i>'Teflon insulation short-circuit in O2 Tank 2 detected—isolate AC Bus 2 immediately'</i>)."
    )
    story.append(Paragraph(api_details, body_style))

    story.append(Spacer(1, 6))

    # Section 4: User Journey
    story.append(Paragraph("4. USER JOURNEY: HOW A USER OPERATES THE WEB APPLICATION", h1_style))
    user_steps = [
        ["User Action", "Web App Reactive Output", "Operational Objective"],
        [
            "1. Tab Selection",
            "Instantly switches views between Timeline, 5x4 Matrix, Fire Types, Real Telemetry, and Sources.",
            "Choose perspective: holistic mission graph, risk grid, or verified NASA MSC-02680 raw table."
        ],
        [
            "2. Timeline Scrubbing",
            "Dragging the bottom slider updates all 4 synchronized subplots in real time.",
            "Travel to any point from MET 0:00 to 142:54. Observe baseline pressure and sudden drop-offs."
        ],
        [
            "3. Interactive Inspection",
            "Hovering cursor over any data point reveals rich multi-metric tooltips.",
            "Inspect exact PSI, cabin oxygen %, severity, likelihood, RPN, and contextual flight controller notes."
        ],
        [
            "4. Incident Replay",
            "Slider reaches MET 55:54:53 (red vertical indicator).",
            "Explosion event triggered: RPN jumps to 20 (RED), O2 pressure crashes to 0 psi, alarm HUD activates."
        ],
        [
            "5. AI Diagnostics View",
            "Clicking on anomaly alert invokes root-cause explanation module.",
            "Operator reads natural language analysis of pre-flight defects and recommended mitigation actions."
        ]
    ]

    t = Table([[Paragraph(c, table_header_style if r==0 else table_cell_style) for c in row] for r, row in enumerate(user_steps)],
              colWidths=[110, 220, 202])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#F0FDF4')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FEFCE8')),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#FEF2F2')),
        ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#EFF6FF')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t)

    story.append(Spacer(1, 8))

    # Section 5: Web App Tech Stack
    story.append(Paragraph("5. WEB APPLICATION TECHNOLOGY SPECIFICATION", h1_style))
    stack_data = [
        [Paragraph("<b>Component</b>", table_header_style), Paragraph("<b>Technology</b>", table_header_style), Paragraph("<b>Execution Environment</b>", table_header_style)],
        [Paragraph("UI Presentation", table_cell_style), Paragraph("HTML5 / CSS3 / Dark Aerospace Theme", table_cell_style), Paragraph("Client Browser (Responsive Desktop & Tablet)", table_cell_style)],
        [Paragraph("Data Visualization", table_cell_style), Paragraph("Plotly.js (WebGL / SVG Subplots)", table_cell_style), Paragraph("Client Browser GPU / Canvas (60 FPS)", table_cell_style)],
        [Paragraph("State & In-Memory Store", table_cell_style), Paragraph("JSON In-Memory Buffer + LocalStorage", table_cell_style), Paragraph("Client RAM (Zero network latency on scrub)", table_cell_style)],
        [Paragraph("Client Prediction ALU", table_cell_style), Paragraph("Web Workers + Derivative Math Core", table_cell_style), Paragraph("Client Background Thread (Non-blocking)", table_cell_style)],
        [Paragraph("AI Reasoning Agent", table_cell_style), Paragraph("Google Gemini API (Interactions API)", table_cell_style), Paragraph("Cloud API Service (Contextual Explanations)", table_cell_style)],
        [Paragraph("Backend Server (Optional)", table_cell_style), Paragraph("Python 3.12 / FastAPI / WebSockets", table_cell_style), Paragraph("Server / Edge Container for real-time live ingest", table_cell_style)]
    ]
    st_table = Table(stack_data, colWidths=[110, 180, 242])
    st_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0369A1')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(st_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
