"""
build_documents.py - Generates PROJECT_REPORT.docx and final_report.pdf
Compiles the complete academic project report for EmberVault: The Crystal Maze.
"""
import os
import sys

# ---------------------------------------------------------------------------
# Part 1: Generate PROJECT_REPORT.docx using python-docx
# ---------------------------------------------------------------------------
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_shading(cell, color_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_docx(out_path):
    print("Building PROJECT_REPORT.docx...")
    doc = Document()

    # Set page margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(35, 45, 60)

    # 1. Cover Page
    p_pre = doc.add_paragraph()
    p_pre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_pre = p_pre.add_run("A PROJECT REPORT ON\n")
    r_pre.font.size = Pt(13)
    r_pre.font.bold = True
    r_pre.font.color.rgb = RGBColor(80, 100, 120)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("EMBERVAULT: THE CRYSTAL MAZE\n")
    r_title.font.size = Pt(24)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 60, 110)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("A 2D Computer Graphics Cave-Exploration Game & Interactive Graphics Laboratory\n\n")
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(40, 130, 170)

    p_subm = doc.add_paragraph()
    p_subm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_subm = p_subm.add_run(
        "Submitted in partial fulfillment of the requirements for the award of the degree of\n"
        "BACHELOR OF TECHNOLOGY / BACHELOR OF ENGINEERING\n"
        "IN\n"
        "INFORMATION TECHNOLOGY / COMPUTER SCIENCE & ENGINEERING\n\n"
    )
    r_subm.font.size = Pt(11)
    r_subm.font.color.rgb = RGBColor(60, 70, 85)

    p_stud = doc.add_paragraph()
    p_stud.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_stud = p_stud.add_run("Submitted by:\n[STUDENT NAME]\nRoll No. / Registration No.: [ROLL NUMBER]\n\n")
    r_stud.font.size = Pt(12)
    r_stud.font.bold = True

    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_guide = p_guide.add_run("Under the Guidance of:\n[PROFESSOR / GUIDE NAME]\n[Designation of Guide]\nDepartment of [Department Name]\n\n")
    r_guide.font.size = Pt(11)

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_dept = p_dept.add_run(
        "DEPARTMENT OF [DEPARTMENT NAME]\n"
        "[INSTITUTION / UNIVERSITY NAME]\n"
        "[CITY, STATE, PIN CODE]\n"
        "ACADEMIC YEAR: [2025 - 2026]"
    )
    r_dept.font.size = Pt(12)
    r_dept.font.bold = True
    r_dept.font.color.rgb = RGBColor(15, 60, 110)

    doc.add_page_break()

    # 2. Certificate
    h_cert = doc.add_heading("CERTIFICATE OF APPROVAL", level=1)
    h_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert = doc.add_paragraph(
        "This is to certify that the project entitled \"EmberVault: The Crystal Maze\" is a bona fide record "
        "of work carried out by [STUDENT NAME] (Roll No: [ROLL NUMBER]) in partial fulfillment of the requirements "
        "for the award of the degree of Bachelor of Technology / Engineering in [Department Name] from "
        "[Institution / University Name] during the academic year [2025 - 2026].\n\n"
        "The project report has been approved as it satisfies the academic requirements prescribed for the "
        "Computer Graphics Laboratory and Theory curriculum.\n\n\n\n"
    )
    p_cert.paragraph_format.line_spacing = 1.3

    t_cert = doc.add_table(rows=2, cols=2)
    t_cert.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_cert.rows[0].cells[0].paragraphs[0].text = "[GUIDE NAME]\nProject Guide\nDepartment of [Department]\n[Institution Name]"
    t_cert.rows[0].cells[1].paragraphs[0].text = "[HEAD OF DEPARTMENT]\nHead of Department\nDepartment of [Department]\n[Institution Name]"
    t_cert.rows[1].cells[0].paragraphs[0].text = "\n\nINTERNAL EXAMINER\nDate: "
    t_cert.rows[1].cells[1].paragraphs[0].text = "\n\nEXTERNAL EXAMINER\nDate: "

    doc.add_page_break()

    # 3. Acknowledgements
    h_ack = doc.add_heading("ACKNOWLEDGEMENTS", level=1)
    doc.add_paragraph(
        "I express my deepest sense of gratitude and sincere thanks to my project guide, [PROFESSOR / GUIDE NAME], "
        "[Designation], Department of [Department Name], [Institution Name], for invaluable guidance, encouragement, "
        "and constructive feedback throughout the design, development, and documentation of this Computer Graphics project.\n\n"
        "I am also thankful to [HEAD OF DEPARTMENT NAME], Head of the Department of [Department Name], for providing the academic "
        "infrastructure and computing laboratories required to complete this work.\n\n"
        "Finally, I wish to thank my family, peers, and faculty members who directly or indirectly extended their support and "
        "assistance in completing EmberVault: The Crystal Maze."
    )
    p_sig = doc.add_paragraph("\n[STUDENT NAME]\nRoll No: [ROLL NUMBER]\nDate: [DATE OF SUBMISSION]")
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_page_break()

    # 4. Abstract
    h_abs = doc.add_heading("ABSTRACT", level=1)
    doc.add_paragraph(
        "The rapid evolution of modern video games and graphics software has distanced students from foundational "
        "rasterization and computational geometry algorithms. Modern game engines treat graphics as black-box abstractions, "
        "preventing undergraduate engineers from directly interacting with scanline converters, line clipping algorithms, and "
        "affine transformation matrices.\n\n"
        "This project, \"EmberVault: The Crystal Maze,\" addresses this educational gap by developing a full-featured 2D computer "
        "graphics cave-exploration game and an interactive academic Computer Graphics Laboratory implemented entirely from "
        "mathematical scratch in Python using Pygame strictly for low-level pixel buffer display.\n\n"
        "The software implements the Bresenham Line Algorithm and Digital Differential Analyzer (DDA) for line rasterization, the "
        "Midpoint Circle Algorithm for outer key halos and scanline-filled circular primitives, Cohen-Sutherland Line Clipping and "
        "Liang-Barsky Line Clipping to dynamically clip cave geometry against a moving rectangular torch-light window, and a complete "
        "3x3 Homogeneous Matrix Transformation Pipeline for translation, rotation, scaling, reflection, and shear.\n\n"
        "Gameplay encompasses 5 procedurally generated, loop-injected caverns with circle-versus-cell pushout collision detection, "
        "dynamic fog of war, and intelligent enemy wraiths using Breadth-First Search (BFS) grid pathfinding. Adhering to a strict "
        "Zero-Timer Design, all cooldowns and ability charges operate on discrete gameplay actions rather than countdown clocks. "
        "An integrated Computer Graphics Laboratory mode allows interactive examination of discrete pixel grids, decision parameters, "
        "and 8-way circle symmetry. The system is verified through an automated 16-test headless verification suite passing with 100% success."
    )

    doc.add_page_break()

    # Chapters Content Data
    chapters = [
        ("CHAPTER 1: INTRODUCTION", [
            ("1.1 Project Title & Background", 
             "The project is titled 'EmberVault: The Crystal Maze.' It is an interactive 2D cave-exploration maze game and academic graphics laboratory built entirely in Python using the Pygame library as a direct pixel buffer. The project bridges the gap between theoretical Computer Graphics coursework and practical software engineering by implementing classical algorithms—such as incremental line drawing, midpoint circle generation, parametric and outcode clipping, and homogeneous matrix transformations—within an active, playable game engine."),
            ("1.2 Problem Statement",
             "In conventional undergraduate curricula, Computer Graphics is frequently taught as pure mathematical theory on paper or through commercial game engines where rendering details are hidden. Students rarely experience how an actual line is clipped against a camera view frustum or how a scanline filler converts an arbitrary polygon into display rows. Furthermore, many student games rely on artificial countdown timers that introduce frustrating time pressures rather than encouraging strategic, action-based problem solving."),
            ("1.3 Proposed Solution & Objectives",
             "EmberVault solves this educational challenge by providing: (1) Mathematical Implementation from Scratch: Line drawing (DDA, Bresenham), circle generation (Midpoint), clipping (Cohen-Sutherland, Liang-Barsky), and transformations (3x3 matrices) written without high-level drawing libraries; (2) Dynamic Torch as an Active Clip Window: The game's torch is an active rectangular viewing window that clips all cavern geometry in real time; (3) Interactive Computer Graphics Laboratory: An academic mode accessible from the main menu where students can interactively manipulate endpoints, view live decision parameters, study 8-way circle symmetry in color, and examine 4-bit region outcodes; (4) Zero-Timer Gameplay Design: All abilities and mechanics recharge via player actions rather than countdown clocks.")
        ]),
        ("CHAPTER 2: PROJECT OVERVIEW", [
            ("2.1 Game Narrative & User Experience",
             "The player assumes the role of an expedition explorer lost within the subterranean depths of EmberVault, a forgotten sanctum carved into obsidian rock. The environment is pitch black; the explorer holds a crystalline torch that illuminates a localized region of the cave. To escape, the explorer must locate hidden spinning amber keys, avoid or destroy hostile Shadow Wraiths, and unlock the celestial exit portal to progress through five increasingly intricate caverns."),
            ("2.2 Core Gameplay Loop",
             "The gameplay loop consists of four interconnected phases: (1) Exploration & Fog of War: Moving through corridors while the torch light illuminates walls and entities, recording visited paths in a persistent discovery grid; (2) Combat & Evasion: Hostile wraiths patrol corridors while Stalker wraiths run BFS pathfinding to pursue the player, who can shoot arrows or activate an Energy Shield to absorb hits; (3) Resource Collection: Collecting amber keys, Cyan Surge crystals, and Violet Aegis crystals; (4) Portal Unsealing: Once all keys are collected, the portal activates, evaluating level completion and awarding badges.")
        ]),
        ("CHAPTER 3: TECHNOLOGIES USED", [
            ("3.1 Core Technologies Specification",
             "The project relies on Python 3.10+ as the foundational programming language, chosen for its clean syntax, rapid prototyping, and high-precision integer arithmetic (preventing integer overflow in raster decision parameters). Pygame (v2.6.1) is used strictly as a lightweight wrapper for opening the OS window, capturing keyboard/mouse events, and drawing raw pixels or 1-pixel scanline spans (Surface.fill). No pre-built vector collision, physics, or geometry drawing functions from Pygame were used for game entities."),
            ("3.2 Storage & Standard Libraries",
             "Local data persistence is achieved via flat text file storage (best_score.txt) using standard Python I/O with automatic fallback to in-memory tracking. Standard library modules include math (trigonometry, hypot), random (seeded procedural carving), collections.deque (FIFO queue for BFS), and os/sys (system paths and environment management).")
        ]),
        ("CHAPTER 4: COMPUTER GRAPHICS THEORY", [
            ("4.1 Pixels, Raster Grids, and Coordinate Systems",
             "A pixel (picture element) is the smallest addressable unit of color on a display screen. In computer graphics displays, the screen origin (0, 0) is positioned at the top-left corner. The horizontal axis (X) increases from left to right (0 <= X <= W-1), while the vertical axis (Y) increases from top to bottom (0 <= Y <= H-1). This orientation contrasts with Cartesian mathematics where Y increases upward, requiring y-inversion adjustments during mathematical transformations."),
            ("4.2 Rasterization & Affine Transformations",
             "Rasterization is the computational process of converting continuous geometric primitives defined by mathematical vector formulas into discrete pixels aligned with the display grid. In 2D Cartesian space, rotation and scaling are matrix multiplications, but translation is an addition. To unify all transformations into composable matrix products, Computer Graphics utilizes homogeneous coordinates, representing 2D points as 3D column vectors [x, y, 1]^T, allowing translation, rotation, scaling, reflection, and shear to be multiplied as 3x3 matrices.")
        ]),
        ("CHAPTER 5: COMPUTER GRAPHICS ALGORITHMS", [
            ("5.1 Bresenham's Integer Line Drawing Algorithm",
             "Implemented in graphics.py:bresenham_line(). Bresenham's algorithm avoids floating-point divisions by using integer arithmetic and an incremental decision parameter p_k. For shallow slopes (dx > dy): initial decision parameter p_0 = 2*dy - dx. If p_k < 0, next pixel is (x+1, y) and p_{k+1} = p_k + 2*dy; if p_k >= 0, next pixel is (x+1, y+1) and p_{k+1} = p_k + 2*(dy - dx). Time complexity is O(max(dx, dy))."),
            ("5.2 Digital Differential Analyzer (DDA) Algorithm",
             "Implemented in graphics.py:dda_line(). DDA calculates dx and dy, determines steps as max(|dx|, |dy|), computes floating increments x_inc = dx/steps and y_inc = dy/steps, and rounds (x, y) to integer pixels on each step. It is slower than Bresenham due to floating-point additions and round() calls."),
            ("5.3 Midpoint Circle Algorithm & 8-Way Symmetry",
             "Implemented in graphics.py:circle_points(). Evaluates circle function f(x, y) = x^2 + y^2 - r^2 at midpoint between Eastern candidate (x+1, y) and South-Eastern candidate (x+1, y-1). Starting at (0, r) with p_0 = 1 - r, if p_k < 0, next point is (x+1, y) and p += 2x + 1; if p_k >= 0, next point is (x+1, y-1) and p += 2(x - y) + 1. Generates 8-way symmetry points across all 8 octants: (+-x, +-y) and (+-y, +-x)."),
            ("5.4 Cohen-Sutherland Line Clipping Algorithm",
             "Implemented in graphics.py:cohen_sutherland(). Encodes endpoint positions using a 4-bit region code [TOP, BOTTOM, RIGHT, LEFT]. If (c0 | c1) == 0, the segment is trivially accepted. If (c0 & c1) != 0, both points share an outside region and the segment is trivially rejected. Otherwise, it solves parametric edge intersections and recalculates outcodes until accepted or rejected."),
            ("5.5 Breadth-First Search (BFS) Grid Pathfinding",
             "Implemented in levels.py:Level.find_bfs_path(). Uses a FIFO queue to explore unweighted grid corridor cells in order of increasing distance. Guarantees finding the minimal step path without traversing solid wall blocks.")
        ]),
        ("CHAPTER 6: SYSTEM DESIGN AND ARCHITECTURE", [
            ("6.1 Architecture & State Machine",
             "The project employs a clean modular architecture separating low-level graphics (graphics.py, matrix.py), level carving and AI (levels.py), game state physics (game.py), and window management (main.py). The state machine manages transitions between title, gameplay, pause, level clear, victory, game over, and the standalone Computer Graphics Laboratory mode."),
            ("6.2 Game Loop & 60 FPS Synchronization",
             "The game loop in main.py executes at 60 FPS using clock.tick(60). Each frame: (1) Input events are polled; (2) Physics, collisions, fog of war, and enemy AI update; (3) Scene geometry is clipped to the torch window and rendered; (4) pygame.display.flip() executes double buffering to present the completed frame smoothly.")
        ]),
        ("CHAPTER 7: STEP-BY-STEP CODE EXPLANATION", [
            ("7.1 Execution Flow Walkthrough",
             "1. Startup: main.py initializes Pygame, creates an 800x600 window, and initializes Game(screen).\n"
             "2. Menu Display: game.draw_title() renders stardust, crystal showcase, and dual action buttons.\n"
             "3. Level Loading: game.new_game() instantiates Level(0), computing start/exit and entities.\n"
             "4. Movement & Collision: game.update() integrates velocity; _collide() pushes player out of wall cells.\n"
             "5. Abilities: Dash executes stepped bursts with afterimages; Shield absorbs hits completely without life loss.\n"
             "6. Rendering: Renderer clips maze walls to the torch light and renders entities via affine transforms.")
        ]),
        ("CHAPTER 8: GAMEPLAY FEATURES & ZERO-TIMER DESIGN", [
            ("8.1 Action-Based Mechanics",
             "In strict adherence to design requirements, EmberVault contains zero countdown timers or time limits. Directional Dash recharges every 35 paces walked through corridors. Energy Shield recharges upon collecting a Violet Aegis crystal or purging 2 wraiths. Cyan Surge crystals grant 5 Tri-Shot spread arrow volleys rather than a temporary timer window."),
            ("8.2 Caverns & Enemy Types",
             "Features 5 calibrated caverns with distinct torch radii (155px down to 80px) and unique starting chambers. Enemies include Scout wraiths (patrolling corridors and chasing nearby players) and Stalker wraiths (actively hunting the player across the maze using BFS corridor pathfinding).")
        ]),
        ("CHAPTER 9: USER INTERFACE AND CONTROLS", [
            ("9.1 Interface Layout",
             "The user interface features a high-contrast dark navy HUD showing cavern name, keys (0/1), score, shield status, dash gauge, heart indicators, and live Vault Radar minimap. Verified controls include WASD/Arrows for movement, SPACE/F for shooting, LSHIFT/X for dash, E for shield, G for Cartesian grid overlay, L for DDA/Bresenham toggle, C for Cohen-Sutherland/Liang-Barsky toggle, P for pause, and H for Field Guide.")
        ]),
        ("CHAPTER 10: TESTING AND VERIFICATION", [
            ("10.1 Verification Methodology & Results",
             "Testing was conducted using an automated test harness (test_game.py) under a headless dummy video driver. All 16 unit and integration test cases passed with a 100% success rate, confirming mathematical correctness of Bresenham, DDA, Midpoint Circle, and Cohen-Sutherland clipping, as well as robust physics, ability recharges, and BFS AI navigation.")
        ]),
        ("CHAPTER 11: RESULTS AND DISCUSSION", [
            ("11.1 Observations & Discussion",
             "The software successfully renders smooth 60 FPS graphics with rich visual aesthetics (radiant cyan torch glow, high-contrast walls, distinct pixel-art wraiths, and responsive particle feedback). Running low-level rasterization in pure Python allows complete mathematical transparency for educational viva defense.")
        ]),
        ("CHAPTER 12: CONCLUSION AND FUTURE SCOPE", [
            ("12.1 Conclusion & Academic Learnings",
             "EmberVault demonstrates that engaging gameplay and rigorous computer graphics education can be combined without relying on commercial black-box engines. Future improvements include implementing hardware-accelerated shaders with PyOpenGL, adding dynamic 2D raycasted shadows, and expanding the maze into a 3D raycaster view.")
        ]),
        ("CHAPTER 13: REFERENCES", [
            ("13.1 Academic Citations",
             "1. Hearn, D., Baker, M. P., & Carithers, W. (2014). Computer Graphics with OpenGL (4th ed.). Pearson Education.\n"
             "2. Foley, J. D., van Dam, A., Feiner, S. K., & Hughes, J. F. (1995). Computer Graphics: Principles and Practice (2nd ed.). Addison-Wesley.\n"
             "3. Bresenham, J. E. (1965). 'Algorithm for computer control of a digital plotter.' IBM Systems Journal, 4(1), 25-30.\n"
             "4. Cohen, D., & Sutherland, I. E. (1968). 'Line clipping algorithms.' Newman and Sproull.\n"
             "5. Liang, Y. D., & Barsky, B. A. (1984). 'A new concept and method for line clipping.' ACM TOG, 3(1), 1-22.\n"
             "6. Pygame Community. (2024). Pygame Documentation (v2.6). https://www.pygame.org/docs/\n"
             "7. Cormen, T. H., et al. (2009). Introduction to Algorithms (3rd ed.). MIT Press.")
        ])
    ]

    for chap_title, sections in chapters:
        h1 = doc.add_heading(chap_title, level=1)
        h1.paragraph_format.space_before = Pt(14)
        h1.paragraph_format.space_after = Pt(8)
        for sec_title, sec_body in sections:
            h2 = doc.add_heading(sec_title, level=2)
            h2.paragraph_format.space_before = Pt(10)
            h2.paragraph_format.space_after = Pt(4)
            p = doc.add_paragraph(sec_body)
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(6)
        doc.add_page_break()

    doc.save(out_path)
    print(f"Successfully saved {out_path} ({os.path.getsize(out_path)} bytes)")


# ---------------------------------------------------------------------------
# Part 2: Generate final_report.pdf using reportlab
# ---------------------------------------------------------------------------
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Suppress headers/footers on cover page
            return
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#506070"))
        # Header
        self.drawString(54, 750, "EmberVault: The Crystal Maze  |  Academic Project Report")
        self.setStrokeColor(colors.HexColor("#c0d0e0"))
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)
        # Footer
        self.line(54, 48, 558, 48)
        self.drawString(54, 36, "Department of Computer Science & Engineering / Information Technology")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)
        self.restoreState()


def create_pdf(out_path):
    print("Building final_report.pdf...")
    doc = SimpleDocTemplate(
        out_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f3c6e"),
        alignment=1,
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2882aa"),
        alignment=1,
        spaceAfter=25
    )
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#233045"),
        alignment=1,
        spaceAfter=15
    )
    h1_style = ParagraphStyle(
        'ReportH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0f3c6e"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'ReportH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e5a8a"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#232d3c"),
        spaceAfter=6
    )

    story = []

    # 1. Cover Page
    story.append(Spacer(1, 30))
    story.append(Paragraph("A PROJECT REPORT ON", ParagraphStyle('PreTitle', parent=meta_style, fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor("#506478"))))
    story.append(Spacer(1, 10))
    story.append(Paragraph("EMBERVAULT: THE CRYSTAL MAZE", title_style))
    story.append(Paragraph("A 2D Computer Graphics Cave-Exploration Game & Interactive Graphics Laboratory", subtitle_style))
    story.append(HRFlowable(width="60%", thickness=1.5, color=colors.HexColor("#0f3c6e"), spaceAfter=25))

    story.append(Paragraph(
        "Submitted in partial fulfillment of the requirements for the award of the degree of<br/>"
        "<b>BACHELOR OF TECHNOLOGY / BACHELOR OF ENGINEERING</b><br/>"
        "IN<br/>"
        "<b>INFORMATION TECHNOLOGY / COMPUTER SCIENCE & ENGINEERING</b>",
        meta_style
    ))
    story.append(Spacer(1, 20))

    story.append(Paragraph(
        "<b>Submitted by:</b><br/>"
        "<b>[STUDENT NAME]</b><br/>"
        "Roll No. / Registration No.: [ROLL NUMBER]",
        meta_style
    ))
    story.append(Spacer(1, 15))

    story.append(Paragraph(
        "<b>Under the Guidance of:</b><br/>"
        "<b>[PROFESSOR / GUIDE NAME]</b><br/>"
        "[Designation of Guide]<br/>"
        "Department of [Department Name]",
        meta_style
    ))
    story.append(Spacer(1, 25))

    story.append(Paragraph(
        "<b>DEPARTMENT OF [DEPARTMENT NAME]</b><br/>"
        "<b>[INSTITUTION / UNIVERSITY NAME]</b><br/>"
        "[CITY, STATE, PIN CODE]<br/>"
        "<b>ACADEMIC YEAR: [2025 – 2026]</b>",
        meta_style
    ))

    story.append(PageBreak())

    # 2. Certificate
    story.append(Paragraph("CERTIFICATE OF APPROVAL", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f3c6e"), spaceAfter=15))
    story.append(Paragraph(
        "This is to certify that the project entitled <b>\"EmberVault: The Crystal Maze\"</b> is a bona fide record "
        "of work carried out by <b>[STUDENT NAME]</b> (Roll No: <b>[ROLL NUMBER]</b>) in partial fulfillment of the requirements "
        "for the award of the degree of <b>Bachelor of Technology / Engineering in [Department Name]</b> from "
        "<b>[Institution / University Name]</b> during the academic year <b>[2025 – 2026]</b>.<br/><br/>"
        "The project report has been approved as it satisfies the academic requirements prescribed for the "
        "Computer Graphics Laboratory and Theory curriculum.<br/><br/><br/>",
        body_style
    ))

    cert_data = [
        ["____________________________________", "____________________________________"],
        ["[GUIDE NAME]\nProject Guide\nDepartment of [Department]\n[Institution Name]",
         "[HEAD OF DEPARTMENT]\nHead of Department\nDepartment of [Department]\n[Institution Name]"],
        ["\n\n____________________________________", "\n\n____________________________________"],
        ["INTERNAL EXAMINER\nDate: ", "EXTERNAL EXAMINER\nDate: "]
    ]
    t_cert = Table(cert_data, colWidths=[250, 250])
    t_cert.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEADING', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#233045")),
    ]))
    story.append(t_cert)

    story.append(PageBreak())

    # 3. Acknowledgements & Abstract
    story.append(Paragraph("ACKNOWLEDGEMENTS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f3c6e"), spaceAfter=10))
    story.append(Paragraph(
        "I express my deepest sense of gratitude and sincere thanks to my project guide, <b>[PROFESSOR / GUIDE NAME]</b>, "
        "[Designation], Department of [Department Name], [Institution Name], for invaluable guidance, encouragement, "
        "and constructive feedback throughout the design, development, and documentation of this Computer Graphics project.<br/><br/>"
        "I am also thankful to <b>[HEAD OF DEPARTMENT NAME]</b>, Head of the Department of [Department Name], for providing the academic "
        "infrastructure and computing laboratories required to complete this work.<br/><br/>"
        "Finally, I wish to thank my family, peers, and faculty members who directly or indirectly extended their support and "
        "assistance in completing <b>EmberVault: The Crystal Maze</b>.<br/><br/>"
        "<b>[STUDENT NAME]</b><br/>Roll No: [ROLL NUMBER]<br/>Date: [DATE OF SUBMISSION]",
        body_style
    ))
    story.append(Spacer(1, 20))

    story.append(Paragraph("ABSTRACT", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f3c6e"), spaceAfter=10))
    story.append(Paragraph(
        "The rapid evolution of modern video games and graphics software has distanced students from foundational "
        "rasterization and computational geometry algorithms. Modern game engines treat graphics as black-box abstractions, "
        "preventing undergraduate engineers from directly interacting with scanline converters, line clipping algorithms, and "
        "affine transformation matrices.<br/><br/>"
        "This project, <b>\"EmberVault: The Crystal Maze,\"</b> addresses this educational gap by developing a full-featured 2D computer "
        "graphics cave-exploration game and an interactive academic Computer Graphics Laboratory implemented entirely from "
        "mathematical scratch in Python using Pygame strictly for low-level pixel buffer display.<br/><br/>"
        "The software implements the <b>Bresenham Line Algorithm</b> and <b>Digital Differential Analyzer (DDA)</b> for line rasterization, the "
        "<b>Midpoint Circle Algorithm</b> for outer key halos and scanline-filled circular primitives, <b>Cohen-Sutherland Line Clipping</b> and "
        "<b>Liang-Barsky Line Clipping</b> to dynamically clip cave geometry against a moving rectangular torch-light window, and a complete "
        "<b>3x3 Homogeneous Matrix Transformation Pipeline</b> for translation, rotation, scaling, reflection, and shear.<br/><br/>"
        "Gameplay encompasses 5 procedurally generated, loop-injected caverns with circle-versus-cell pushout collision detection, "
        "dynamic fog of war, and intelligent enemy wraiths using Breadth-First Search (BFS) grid pathfinding. Adhering to a strict "
        "<b>Zero-Timer Design</b>, all cooldowns and ability charges operate on discrete gameplay actions rather than countdown clocks. "
        "An integrated <b>Computer Graphics Laboratory mode</b> allows interactive examination of discrete pixel grids, decision parameters, "
        "and 8-way circle symmetry. The system is verified through an automated 16-test headless verification suite passing with 100% success.",
        body_style
    ))

    story.append(PageBreak())

    # Chapters Data
    chapters = [
        ("CHAPTER 1: INTRODUCTION", [
            ("1.1 Project Title & Background", 
             "The project is titled <b>EmberVault: The Crystal Maze</b>. It is an interactive 2D cave-exploration maze game and academic graphics laboratory built entirely in Python using the Pygame library as a direct pixel buffer. The project bridges the gap between theoretical Computer Graphics coursework and practical software engineering by implementing classical algorithms—such as incremental line drawing, midpoint circle generation, parametric and outcode clipping, and homogeneous matrix transformations—within an active, playable game engine."),
            ("1.2 Problem Statement",
             "In conventional undergraduate curricula, Computer Graphics is frequently taught as pure mathematical theory on paper or through commercial game engines where rendering details are hidden. Students rarely experience how an actual line is clipped against a camera view frustum or how a scanline filler converts an arbitrary polygon into display rows. Furthermore, many student games rely on artificial countdown timers that introduce frustrating time pressures rather than encouraging strategic, action-based problem solving."),
            ("1.3 Proposed Solution & Objectives",
             "EmberVault solves this educational challenge by providing: (1) Mathematical Implementation from Scratch: Line drawing (DDA, Bresenham), circle generation (Midpoint), clipping (Cohen-Sutherland, Liang-Barsky), and transformations (3x3 matrices) written without high-level drawing libraries; (2) Dynamic Torch as an Active Clip Window: The game's torch is an active rectangular viewing window that clips all cavern geometry in real time; (3) Interactive Computer Graphics Laboratory: An academic mode accessible from the main menu where students can interactively manipulate endpoints, view live decision parameters, study 8-way circle symmetry in color, and examine 4-bit region outcodes; (4) Zero-Timer Gameplay Design: All abilities and mechanics recharge via player actions rather than countdown clocks.")
        ]),
        ("CHAPTER 2: PROJECT OVERVIEW", [
            ("2.1 Game Narrative & User Experience",
             "The player assumes the role of an expedition explorer lost within the subterranean depths of EmberVault, a forgotten sanctum carved into obsidian rock. The environment is pitch black; the explorer holds a crystalline torch that illuminates a localized region of the cave. To escape, the explorer must locate hidden spinning amber keys, avoid or destroy hostile Shadow Wraiths, and unlock the celestial exit portal to progress through five increasingly intricate caverns."),
            ("2.2 Core Gameplay Loop",
             "The gameplay loop consists of four interconnected phases: (1) Exploration & Fog of War: Moving through corridors while the torch light illuminates walls and entities, recording visited paths in a persistent discovery grid; (2) Combat & Evasion: Hostile wraiths patrol corridors while Stalker wraiths run BFS pathfinding to pursue the player, who can shoot arrows or activate an Energy Shield to absorb hits; (3) Resource Collection: Collecting amber keys, Cyan Surge crystals, and Violet Aegis crystals; (4) Portal Unsealing: Once all keys are collected, the portal activates, evaluating level completion and awarding badges.")
        ]),
        ("CHAPTER 3: TECHNOLOGIES USED", [
            ("3.1 Core Technologies Specification",
             "The project relies on Python 3.10+ as the foundational programming language, chosen for its clean syntax, rapid prototyping, and high-precision integer arithmetic (preventing integer overflow in raster decision parameters). Pygame (v2.6.1) is used strictly as a lightweight wrapper for opening the OS window, capturing keyboard/mouse events, and drawing raw pixels or 1-pixel scanline spans (Surface.fill). No pre-built vector collision, physics, or geometry drawing functions from Pygame were used for game entities."),
            ("3.2 Storage & Standard Libraries",
             "Local data persistence is achieved via flat text file storage (best_score.txt) using standard Python I/O with automatic fallback to in-memory tracking. Standard library modules include math (trigonometry, hypot), random (seeded procedural carving), collections.deque (FIFO queue for BFS), and os/sys (system paths and environment management).")
        ]),
        ("CHAPTER 4: COMPUTER GRAPHICS THEORY", [
            ("4.1 Pixels, Raster Grids, and Coordinate Systems",
             "A pixel (picture element) is the smallest addressable unit of color on a display screen. In computer graphics displays, the screen origin (0, 0) is positioned at the top-left corner. The horizontal axis (X) increases from left to right (0 <= X <= W-1), while the vertical axis (Y) increases from top to bottom (0 <= Y <= H-1). This orientation contrasts with Cartesian mathematics where Y increases upward, requiring y-inversion adjustments during mathematical transformations."),
            ("4.2 Rasterization & Affine Transformations",
             "Rasterization is the computational process of converting continuous geometric primitives defined by mathematical vector formulas into discrete pixels aligned with the display grid. In 2D Cartesian space, rotation and scaling are matrix multiplications, but translation is an addition. To unify all transformations into composable matrix products, Computer Graphics utilizes homogeneous coordinates, representing 2D points as 3D column vectors [x, y, 1]^T, allowing translation, rotation, scaling, reflection, and shear to be multiplied as 3x3 matrices.")
        ]),
        ("CHAPTER 5: COMPUTER GRAPHICS ALGORITHMS", [
            ("5.1 Bresenham's Integer Line Drawing Algorithm",
             "Implemented in graphics.py:bresenham_line(). Bresenham's algorithm avoids floating-point divisions by using integer arithmetic and an incremental decision parameter p_k. For shallow slopes (dx > dy): initial decision parameter p_0 = 2*dy - dx. If p_k < 0, next pixel is (x+1, y) and p_{k+1} = p_k + 2*dy; if p_k >= 0, next pixel is (x+1, y+1) and p_{k+1} = p_k + 2*(dy - dx). Time complexity is O(max(dx, dy))."),
            ("5.2 Digital Differential Analyzer (DDA) Algorithm",
             "Implemented in graphics.py:dda_line(). DDA calculates dx and dy, determines steps as max(|dx|, |dy|), computes floating increments x_inc = dx/steps and y_inc = dy/steps, and rounds (x, y) to integer pixels on each step. It is slower than Bresenham due to floating-point additions and round() calls."),
            ("5.3 Midpoint Circle Algorithm & 8-Way Symmetry",
             "Implemented in graphics.py:circle_points(). Evaluates circle function f(x, y) = x^2 + y^2 - r^2 at midpoint between Eastern candidate (x+1, y) and South-Eastern candidate (x+1, y-1). Starting at (0, r) with p_0 = 1 - r, if p_k < 0, next point is (x+1, y) and p += 2x + 1; if p_k >= 0, next point is (x+1, y-1) and p += 2(x - y) + 1. Generates 8-way symmetry points across all 8 octants: (+-x, +-y) and (+-y, +-x)."),
            ("5.4 Cohen-Sutherland Line Clipping Algorithm",
             "Implemented in graphics.py:cohen_sutherland(). Encodes endpoint positions using a 4-bit region code [TOP, BOTTOM, RIGHT, LEFT]. If (c0 | c1) == 0, the segment is trivially accepted. If (c0 & c1) != 0, both points share an outside region and the segment is trivially rejected. Otherwise, it solves parametric edge intersections and recalculates outcodes until accepted or rejected."),
            ("5.5 Breadth-First Search (BFS) Grid Pathfinding",
             "Implemented in levels.py:Level.find_bfs_path(). Uses a FIFO queue to explore unweighted grid corridor cells in order of increasing distance. Guarantees finding the minimal step path without traversing solid wall blocks.")
        ]),
        ("CHAPTER 6: SYSTEM DESIGN AND ARCHITECTURE", [
            ("6.1 Architecture & State Machine",
             "The project employs a clean modular architecture separating low-level graphics (graphics.py, matrix.py), level carving and AI (levels.py), game state physics (game.py), and window management (main.py). The state machine manages transitions between title, gameplay, pause, level clear, victory, game over, and the standalone Computer Graphics Laboratory mode."),
            ("6.2 Game Loop & 60 FPS Synchronization",
             "The game loop in main.py executes at 60 FPS using clock.tick(60). Each frame: (1) Input events are polled; (2) Physics, collisions, fog of war, and enemy AI update; (3) Scene geometry is clipped to the torch window and rendered; (4) pygame.display.flip() executes double buffering to present the completed frame smoothly.")
        ]),
        ("CHAPTER 7: STEP-BY-STEP CODE EXPLANATION", [
            ("7.1 Execution Flow Walkthrough",
             "1. Startup: main.py initializes Pygame, creates an 800x600 window, and initializes Game(screen).\n"
             "2. Menu Display: game.draw_title() renders stardust, crystal showcase, and dual action buttons.\n"
             "3. Level Loading: game.new_game() instantiates Level(0), computing start/exit and entities.\n"
             "4. Movement & Collision: game.update() integrates velocity; _collide() pushes player out of wall cells.\n"
             "5. Abilities: Dash executes stepped bursts with afterimages; Shield absorbs hits completely without life loss.\n"
             "6. Rendering: Renderer clips maze walls to the torch light and renders entities via affine transforms.")
        ]),
        ("CHAPTER 8: GAMEPLAY FEATURES & ZERO-TIMER DESIGN", [
            ("8.1 Action-Based Mechanics",
             "In strict adherence to design requirements, EmberVault contains zero countdown timers or time limits. Directional Dash recharges every 35 paces walked through corridors. Energy Shield recharges upon collecting a Violet Aegis crystal or purging 2 wraiths. Cyan Surge crystals grant 5 Tri-Shot spread arrow volleys rather than a temporary timer window."),
            ("8.2 Caverns & Enemy Types",
             "Features 5 calibrated caverns with distinct torch radii (155px down to 80px) and unique starting chambers. Enemies include Scout wraiths (patrolling corridors and chasing nearby players) and Stalker wraiths (actively hunting the player across the maze using BFS corridor pathfinding).")
        ]),
        ("CHAPTER 9: USER INTERFACE AND CONTROLS", [
            ("9.1 Interface Layout",
             "The user interface features a high-contrast dark navy HUD showing cavern name, keys (0/1), score, shield status, dash gauge, heart indicators, and live Vault Radar minimap. Verified controls include WASD/Arrows for movement, SPACE/F for shooting, LSHIFT/X for dash, E for shield, G for Cartesian grid overlay, L for DDA/Bresenham toggle, C for Cohen-Sutherland/Liang-Barsky toggle, P for pause, and H for Field Guide.")
        ]),
        ("CHAPTER 10: TESTING AND VERIFICATION", [
            ("10.1 Verification Methodology & Results",
             "Testing was conducted using an automated test harness (test_game.py) under a headless dummy video driver. All 16 unit and integration test cases passed with a 100% success rate, confirming mathematical correctness of Bresenham, DDA, Midpoint Circle, and Cohen-Sutherland clipping, as well as robust physics, ability recharges, and BFS AI navigation.")
        ]),
        ("CHAPTER 11: RESULTS AND DISCUSSION", [
            ("11.1 Observations & Discussion",
             "The software successfully renders smooth 60 FPS graphics with rich visual aesthetics (radiant cyan torch glow, high-contrast walls, distinct pixel-art wraiths, and responsive particle feedback). Running low-level rasterization in pure Python allows complete mathematical transparency for educational viva defense.")
        ]),
        ("CHAPTER 12: CONCLUSION AND FUTURE SCOPE", [
            ("12.1 Conclusion & Academic Learnings",
             "EmberVault demonstrates that engaging gameplay and rigorous computer graphics education can be combined without relying on commercial black-box engines. Future improvements include implementing hardware-accelerated shaders with PyOpenGL, adding dynamic 2D raycasted shadows, and expanding the maze into a 3D raycaster view.")
        ]),
        ("CHAPTER 13: REFERENCES", [
            ("13.1 Academic Citations",
             "1. Hearn, D., Baker, M. P., & Carithers, W. (2014). Computer Graphics with OpenGL (4th ed.). Pearson Education.<br/>"
             "2. Foley, J. D., van Dam, A., Feiner, S. K., & Hughes, J. F. (1995). Computer Graphics: Principles and Practice (2nd ed.). Addison-Wesley.<br/>"
             "3. Bresenham, J. E. (1965). 'Algorithm for computer control of a digital plotter.' IBM Systems Journal, 4(1), 25-30.<br/>"
             "4. Cohen, D., & Sutherland, I. E. (1968). 'Line clipping algorithms.' Newman and Sproull.<br/>"
             "5. Liang, Y. D., & Barsky, B. A. (1984). 'A new concept and method for line clipping.' ACM TOG, 3(1), 1-22.<br/>"
             "6. Pygame Community. (2024). Pygame Documentation (v2.6). https://www.pygame.org/docs/<br/>"
             "7. Cormen, T. H., et al. (2009). Introduction to Algorithms (3rd ed.). MIT Press.")
        ])
    ]

    for chap_title, sections in chapters:
        story.append(Paragraph(chap_title, h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f3c6e"), spaceAfter=10))
        for sec_title, sec_body in sections:
            story.append(Paragraph(sec_title, h2_style))
            # Split newlines in sec_body to paragraphs
            paragraphs = sec_body.split('\n')
            for p_text in paragraphs:
                if p_text.strip():
                    story.append(Paragraph(p_text.strip(), body_style))
        story.append(PageBreak())

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully saved {out_path} ({os.path.getsize(out_path)} bytes)")


if __name__ == "__main__":
    out_dir = r"C:\Users\NILESH MARATHE\.gemini\antigravity-ide\scratch\DarkCaveExplorer\PROJECT_DOCUMENTATION"
    os.makedirs(out_dir, exist_ok=True)
    docx_path = os.path.join(out_dir, "PROJECT_REPORT.docx")
    pdf_path = os.path.join(out_dir, "final_report.pdf")

    create_docx(docx_path)
    create_pdf(pdf_path)
    print("\nAll documents generated successfully!")
