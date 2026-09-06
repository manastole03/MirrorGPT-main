#!/usr/bin/env python3
"""Build the capstone proposal by filling the supplied Word template."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = Path("/Users/manastole/Downloads/CSE598-capstone-proposal-template.docx")
OUTPUT = ROOT / "deliverables" / "Manas_Tole_CSE598_Capstone_Proposal.docx"
SCREENSHOT = ROOT / "assets" / "ui_baseline_report.png"
BLUE = RGBColor(0x4F, 0x81, 0xBD)


def set_font(run, name="Arial", size=9.5, bold=None, color=None):
    run.font.name = name
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color:
        run.font.color.rgb = color


def clear_body(document):
    body = document._element.body
    section_properties = body.sectPr
    for child in list(body):
        if child is not section_properties:
            body.remove(child)


def configure_styles(document):
    normal = document.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    normal.font.size = Pt(9.5)
    normal.paragraph_format.space_after = Pt(3.5)
    normal.paragraph_format.line_spacing = 1.0

    body = document.styles["Body Text"]
    body.font.name = "Arial"
    body.font.size = Pt(9.5)
    body.paragraph_format.space_before = Pt(0)
    body.paragraph_format.space_after = Pt(3.5)
    body.paragraph_format.line_spacing = 1.0

    h1 = document.styles["Heading 1"]
    h1.font.name = "Arial"
    h1.font.size = Pt(16)
    h1.font.bold = True
    h1.font.color.rgb = BLUE
    h1.paragraph_format.space_before = Pt(0)
    h1.paragraph_format.space_after = Pt(3)

    h2 = document.styles["Heading 2"]
    h2.font.name = "Arial"
    h2.font.size = Pt(11.5)
    h2.font.bold = True
    h2.font.color.rgb = BLUE
    h2.paragraph_format.space_before = Pt(6)
    h2.paragraph_format.space_after = Pt(2)
    h2.paragraph_format.keep_with_next = True


def add_body(document, text, keep=False):
    p = document.add_paragraph(style="Body Text")
    p.paragraph_format.keep_together = keep
    p.add_run(text)
    return p


def add_labeled_body(document, parts):
    p = document.add_paragraph(style="Body Text")
    for label, text in parts:
        if label:
            r = p.add_run(label)
            r.bold = True
        p.add_run(text)
    return p


def shade_paragraph(paragraph, fill="F2F4F7"):
    ppr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def set_cell_width(cell, width_twips):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(width_twips))
    tc_w.set(qn("w:type"), "dxa")


def configure_table_geometry(table, widths):
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths)))
    tbl_w.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            set_cell_width(cell, width)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_basic_info(document):
    document.add_heading("Basic Information", level=2)
    rows = [
        ("Field", "Response"),
        ("Student name", "Manas Tole"),
        ("Project title", "MirrorGPT Lite: A Grounded Personal-Profile Agent"),
        ("Repository / notebook link", "PUBLIC GITHUB URL REQUIRED BEFORE SUBMISSION"),
        ("Configuration location", "README.md (no API key or environment variables required)"),
    ]
    table = document.add_table(rows=len(rows), cols=2)
    table.style = "Normal Table"
    configure_table_geometry(table, [3100, 6260])
    for index, (left, right) in enumerate(rows):
        for cell, value in zip(table.rows[index].cells, (left, right)):
            cell.text = value
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1.5)
            p.paragraph_format.space_before = Pt(1.5)
            for run in p.runs:
                set_font(run, size=9.2, bold=(index == 0))
        if index == 0:
            tr_pr = table.rows[index]._tr.get_or_add_trPr()
            header = OxmlElement("w:tblHeader")
            header.set(qn("w:val"), "true")
            tr_pr.append(header)
            for cell in table.rows[index].cells:
                shd = OxmlElement("w:shd")
                shd.set(qn("w:fill"), "EAF1F8")
                cell._tc.get_or_add_tcPr().append(shd)


def add_title(document):
    title = document.add_paragraph(style="Heading 1")
    title.add_run("Capstone Project Proposal")
    subtitle = document.add_paragraph(style="Body Text")
    subtitle.paragraph_format.space_after = Pt(4)
    run = subtitle.add_run("MirrorGPT Lite • Individual runnable baseline • CSE 598")
    set_font(run, size=9.5, bold=True, color=RGBColor(0x55, 0x55, 0x55))


def build():
    document = Document(TEMPLATE)
    clear_body(document)
    configure_styles(document)
    document.core_properties.author = "Manas Tole"
    document.core_properties.last_modified_by = "Manas Tole"
    document.core_properties.title = "CSE 598 Capstone Project Proposal - MirrorGPT Lite"
    document.core_properties.subject = "Individual capstone proposal and runnable baseline"
    add_title(document)
    add_basic_info(document)

    document.add_heading("Section 1. Problem Definition", level=2)
    add_body(
        document,
        "The system answers natural-language questions as the owner of a supplied personal profile while remaining grounded in that profile. The intended user is a person building a transparent digital representative. Input is a UTF-8 profile plus one question; output is JSON containing the question, a first-person answer, and supporting evidence. Success means an answer is supported by the profile or the system correctly abstains. An unsupported claim, missed answerable fact, or non-runnable setup is failure.",
    )

    document.add_heading("Section 2. Motivation and Project Scope", level=2)
    add_body(
        document,
        "Personal agents can save users from repeatedly answering factual questions, but hallucination and privacy errors make them risky. An agentic approach is appropriate because a later system can explicitly retrieve, answer, verify evidence, and decide when to abstain. This semester covers text profiles, grounded question answering, evidence display, conversation context, and repeatable evaluation. Voice/video cloning, autonomous external actions, production authentication, and training a foundation model are out of scope.",
    )

    document.add_heading("Section 3. Runnable Baseline", level=2)
    add_body(
        document,
        "The runnable baseline is a deterministic Python 3 rule-and-retrieval system with no external libraries or APIs. It reads the profile and question, applies an education rule or expanded keyword retrieval, returns a first-person answer with evidence, and abstains when nothing matches. A local web UI calls the same baseline through a JSON API. This establishes a reproducible floor for task completion, groundedness, and abstention. Files: baseline.py, app.py, web/, examples/test1.txt, tests/, and outputs/test1.json.",
    )

    document.add_heading("Section 4. Test Case and Baseline Output", level=2)
    test_case = add_labeled_body(document, [
        ("Sample input: ", "“Where did you go to college?”  "),
        ("Expected: ", "identify profile institutions, answer in first person, and cite evidence.  "),
        ("Actual: ", "the UI named the University of Washington and The University of Texas at Austin and displayed both evidence lines."),
    ])
    test_case.paragraph_format.keep_with_next = True

    picture = document.add_paragraph()
    picture.alignment = WD_ALIGN_PARAGRAPH.CENTER
    picture.paragraph_format.space_after = Pt(1)
    picture.paragraph_format.keep_with_next = True
    run = picture.add_run()
    inline = run.add_picture(str(SCREENSHOT), width=Inches(4.75))
    doc_pr = inline._inline.docPr
    doc_pr.set("descr", "MirrorGPT Lite web interface showing a successful grounded answer with two supporting evidence lines")
    caption = document.add_paragraph(style="Body Text")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.space_after = Pt(3)
    cap_run = caption.add_run("Figure 1. Working local UI with actual grounded baseline output.")
    set_font(cap_run, size=8, bold=True, color=RGBColor(0x55, 0x55, 0x55))
    add_body(
        document,
        "What worked: the answer is reproducible, first-person, evidence-backed, and accessible through both UI and CLI. What did not: the rule lists institutions but does not distinguish completed degrees from the incomplete PhD year, illustrating shallow semantics.",
    )

    document.add_heading("Section 5. Reproducibility and Run Instructions", level=2)
    add_body(document, "Use Python 3.9+ from the repository root; no package installation, API key, environment variable, or network access is required. Full setup, CLI instructions, inputs, and outputs are in README.md. Start the UI with:")
    command = document.add_paragraph(style="Body Text")
    command.paragraph_format.left_indent = Inches(0.12)
    command.paragraph_format.right_indent = Inches(0.12)
    command.paragraph_format.space_before = Pt(1.5)
    command.paragraph_format.space_after = Pt(3)
    shade_paragraph(command)
    r = command.add_run("python3 app.py")
    set_font(r, name="Courier New", size=7.7)
    add_body(document, "Open http://127.0.0.1:8765. The CLI test writes outputs/test1.json; verify all three tests with: python3 -m unittest discover -s tests -v.")

    document.add_heading("Section 6. Initial Evaluation Plan", level=2)
    add_body(
        document,
        "I will build a 40-question set balanced between answerable and unanswerable questions, with manually labeled answers and evidence. Baseline and improved systems will be compared on answer correctness, evidence precision, abstention precision/recall, unsupported-claim rate, median latency, and per-query API cost. Paired per-question results will show whether the agentic workflow improves accuracy and groundedness rather than only fluency.",
    )

    document.add_heading("Section 7. Limitations and Next Steps", level=2)
    add_body(
        document,
        "The baseline relies on brittle rules and lexical overlap, handles paraphrases and multi-hop questions poorly, has no dialogue memory, and uses a specialized education rule. Next I will add semantic retrieval, an answer-and-citation generator, a verifier/abstention step, conversation state, and privacy filters. Main risks are evaluation-label quality, API cost, and keeping personal data private; a deterministic offline fallback will remain available.",
    )

    # Keep the reference section geometry unchanged and remove accidental blank final paragraphs.
    for section in document.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
