import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = r"c:\Users\Nasrallah\Downloads\chat-812c8388-89f0-4c7c-88f6-7e872379485d"
PDF_PATH = os.path.join(BASE_DIR, "Apollo13_FireRisk_Architecture_Plan.pdf")
IMG_ARCH = os.path.join(BASE_DIR, "architecture_diagram.png")
IMG_PIPE = os.path.join(BASE_DIR, "prediction_pipeline_diagram.png")

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
        self.drawString(40, letter[1] - 28, "NASA APOLLO 13 FIRE RISK SIMULATION — ARCHITECTURE & PREDICTION DESIGN")

        # Bottom footer line
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(1)
        self.line(40, 42, letter[0] - 40, 42)

        # Footer text & page number
        self.setFont("Helvetica", 8)
        self.drawString(40, 30, "CONFIDENTIAL & SYSTEM ENGINEERING SPECIFICATION | NASA-STD-8719.13 & NPR 8715.3C")
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

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#0369A1'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#0C4A6E')
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
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

    # 1. Document Title & Header Meta
    story.append(Paragraph("APOLLO 13 FIRE RISK SYSTEM ARCHITECTURE", title_style))
    story.append(Paragraph("Application Blueprint, Computer Architecture Schematic, Prediction Engine & User Operational Flow", subtitle_style))

    # Meta Table (Quick facts: Reading time ~2-3 min)
    meta_data = [
        [
            Paragraph("<b>Reading Time:</b> ~2-3 Minutes", table_cell_style),
            Paragraph("<b>Target Domain:</b> Spacecraft Telemetry & Safety", table_cell_style),
            Paragraph("<b>Benchmark:</b> Apollo 13 (MSC-02680)", table_cell_style),
            Paragraph("<b>Standard:</b> NASA 5x4 Matrix", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[130, 150, 130, 122])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F9FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BAE6FD')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 2. Problématique (Problem Statement)
    story.append(Paragraph("1. PROBLÉMATIQUE (THE CORE PROBLEM ADDRESSED)", h1_style))
    prob_text = (
        "In critical aerospace environments like Apollo 13, fire hazards within pressurized cryogenic and enriched oxygen "
        "enclosures (Service Module Bay 4) exhibit <b>explosive acceleration</b>. The historical Apollo 13 failure sequence demonstrates "
        "three fatal engineering shortcomings in classic warning systems:<br/>"
        "<b>• Reactive vs. Predictive Thresholds:</b> Traditional alarms only triggered when absolute pressure crossed safety limits (1008 psia). "
        "By that point, the fire was already uncontrollable and containment failure occurred in under 90 seconds.<br/>"
        "<b>• Blindness to Combined Derivative Signatures:</b> Early symptoms—such as an 11.1A to 22.9A current spike during fan stirring and a 1.2V "
        "voltage transient on AC Bus 2—were treated as isolated anomalies rather than an active combustion ignition.<br/>"
        "<b>• Lack of Dynamic Risk Matrix Quantization:</b> Flight controllers lacked a real-time risk scoring engine (NASA 5x4 Severity x Likelihood) "
        "that instantly updates Mission Elapsed Time (MET) risk status from GREEN to RED before physical destruction."
    )
    story.append(Paragraph(prob_text, body_style))
    story.append(Spacer(1, 6))

    # 3. System Architecture Schematic (Computer Hardware Abstraction)
    story.append(Paragraph("2. SYSTEM ARCHITECTURE SCHEMATIC (COMPUTER HARDWARE ABSTRACTION)", h1_style))
    arch_intro = (
        "Modeled directly after classical computer architecture, the application isolates ingestion, compute, logic, "
        "and presentation across a high-speed telemetry system bus:"
    )
    story.append(Paragraph(arch_intro, body_style))

    if os.path.exists(IMG_ARCH):
        story.append(Image(IMG_ARCH, width=7.2*inch, height=4.0*inch))
        story.append(Spacer(1, 4))

    # Architecture Explanation Box
    arch_desc = (
        "<b>Component Highlights:</b><br/>"
        "<b>1. Telemetry I/O Unit:</b> High-frequency FIFO buffer ingesting sensor telemetry (2,000 to 6,000 data points).<br/>"
        "<b>2. Neural Prediction ALU:</b> Computes physical rate-of-change (dP/dt, dT/dt) and executes time-series anomaly inference.<br/>"
        "<b>3. NASA Risk Matrix Core:</b> Evaluates Severity (1-4) x Likelihood (1-5) based on NPR 8715.3C / NASA-STD-8719.13.<br/>"
        "<b>4. State Registers & DB:</b> Holds live MET clock, cryogenic tank state vectors, and historical event signatures.<br/>"
        "<b>5. Prediction API Gateway:</b> Exposes REST/gRPC endpoints and connects intelligent contextual agents (Gemini API).<br/>"
        "<b>6. Flight Deck HUD:</b> Real-time Plotly interactive control dashboard with predictive T-minus alarms."
    )
    story.append(Paragraph(arch_desc, body_style))

    story.append(PageBreak())

    # 4. How Prediction Works & API Breakdown
    story.append(Paragraph("3. PREDICTION MECHANISM: HOW IT WORKS & AVAILABLE APIs", h1_style))
    pred_text = (
        "Predicting fire risk in a spacecraft is not merely waiting for threshold breach—it is detecting the <b>thermodynamic "
        "and electrical signature of combustion initiation</b> 60 to 120 seconds before pressure vessel rupture."
    )
    story.append(Paragraph(pred_text, body_style))

    if os.path.exists(IMG_PIPE):
        story.append(Image(IMG_PIPE, width=7.2*inch, height=2.9*inch))
        story.append(Spacer(1, 6))

    # Detailed Prediction Mechanism
    story.append(Paragraph("A. Mathematical & ML Prediction Engine", h2_style))
    ml_desc = (
        "<b>• Gradient & Derivative Estimators:</b> The system monitors first and second order derivatives (dP/dt, d²P/dt², dI/dt). "
        "A sudden slope increase while heating elements are idle signals exothermic combustion.<br/>"
        "<b>• Time-Series Forecaster (LSTM / GRU / TFT):</b> A lightweight recurrent model takes a sliding 30-second telemetry window "
        "and forecasts pressure and temperature 90 seconds into the future. If forecasted values cross critical thresholds, an alert fires.<br/>"
        "<b>• Autoencoder Anomaly Scoring:</b> An unsupervised neural network trained on nominal telemetry flags electrical bus drops "
        "and sensor glitched behavior with an Anomaly Score (0.0 to 1.0), triggering Likelihood level promotions."
    )
    story.append(Paragraph(ml_desc, body_style))

    story.append(Paragraph("B. Does an External API Exist? Can We Use Gemini API?", h2_style))
    api_desc = (
        "<b>• Are there pre-made public APIs?</b> NASA does not host a real-time predictive fire-detection API. NASA provides historical "
        "telemetry archives and research APIs (e.g., <i>data.nasa.gov</i>, NASA Technical Reports Server NTRS), but the real-time inference engine "
        "must run as a custom microservice.<br/>"
        "<b>• Custom Microservice (FastAPI / gRPC):</b> Host the ONNX-optimized LSTM and derivative pipeline as a dedicated, low-latency API "
        "processing 100+ telemetry frames per second.<br/>"
        "<b>• AI Reasoning Integration via Gemini API:</b> Gemini can be integrated as the <b>Senior Flight Safety Advisor Agent</b> via the "
        "Interactions API. When the local neural ALU detects a risk spike (RPN > 15), it dispatches the telemetry vector to Gemini. "
        "The model analyzes historical anomaly playbooks (e.g., Apollo 13 Review Board D-01 through D-04) and returns human-readable "
        "root-cause diagnostics and recommended mitigation steps in natural language to flight controllers."
    )
    story.append(Paragraph(api_desc, body_style))

    story.append(Spacer(1, 6))

    # 5. User Journey & Operational Experience
    story.append(Paragraph("4. USER JOURNEY: HOW FLIGHT CONTROLLERS USE THE APPLICATION", h1_style))
    user_steps = [
        ["Phase", "User Action (Flight Controller / EECOM)", "System Response & Visual Output"],
        [
            "Phase 1:\nPre-Stir Inspection",
            "Flight controller checks Cryo Tank 2 status before issuing stir command.",
            "HUD displays GREEN (RPN 4). Matrix indicates Low Risk. Sensor trends show nominal 880 psi."
        ],
        [
            "Phase 2:\nAnomaly & Prediction\n(MET 55:53:20)",
            "Fans engaged. Voltage transient and current spike occur. Controller receives early warning.",
            "Prediction ALU flags dP/dt surge. Risk flips to ORANGE -> RED (RPN 20). HUD sounds T-minus 90s countdown."
        ],
        [
            "Phase 3:\nAutomated Mitigation\n& Lifeboat Protocol",
            "Controller confirms emergency containment isolation or automatic interlock cuts power.",
            "Gemini Agent recommends immediate electrical bus separation. Full event snapshot saved to telemetry blackbox."
        ]
    ]

    t = Table([[Paragraph(c, table_header_style if r==0 else table_cell_style) for c in row] for r, row in enumerate(user_steps)],
              colWidths=[100, 210, 222])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#FEF2F2')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#EFF6FF')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)

    story.append(Spacer(1, 10))

    # 6. Technical Stack Summary
    story.append(Paragraph("5. IMPLEMENTATION STACK SUMMARY", h1_style))
    stack_data = [
        [Paragraph("<b>Layer</b>", table_header_style), Paragraph("<b>Technology</b>", table_header_style), Paragraph("<b>Role in System</b>", table_header_style)],
        [Paragraph("Frontend UI", table_cell_style), Paragraph("HTML5, Plotly.js, WebSockets", table_cell_style), Paragraph("Interactive 4-pane telemetry HUD, slider replay, risk matrix", table_cell_style)],
        [Paragraph("Core Backend", table_cell_style), Paragraph("Python 3.12, FastAPI, NumPy", table_cell_style), Paragraph("Telemetry stream processing, FIFO buffer, bus routing", table_cell_style)],
        [Paragraph("ML / Inference", table_cell_style), Paragraph("PyTorch / ONNX / Scikit-Learn", table_cell_style), Paragraph("Sliding window LSTM forecaster, gradient derivative scoring", table_cell_style)],
        [Paragraph("AI Safety Agent", table_cell_style), Paragraph("Google Gemini API (Interactions)", table_cell_style), Paragraph("Automated root cause explanation and mitigation advisory", table_cell_style)],
        [Paragraph("Data Standard", table_cell_style), Paragraph("JSON / NASA MSC-02680 Format", table_cell_style), Paragraph("High fidelity 2,000 to 6,000 data point simulation stream", table_cell_style)]
    ]
    st_table = Table(stack_data, colWidths=[110, 160, 262])
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
