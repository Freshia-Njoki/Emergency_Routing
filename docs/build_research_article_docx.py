"""Build the journal-formatted Word manuscript (RAG-article layout).

Times New Roman, 1.5 line spacing, A4, justified body, APA-style captions.
Overwrites docs/Macharia_GRU_Emergency_Routing_Article.docx
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Inches, Pt, RGBColor, Emu

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs" / "research_article_final.md"
OUT = ROOT / "docs" / "Macharia_GRU_Emergency_Routing_Article.docx"
FIG_DIR = ROOT / "docs" / "article_figures"
SIM_FIG = ROOT / "results" / "simulation" / "figures"

FONT = "Times New Roman"


def set_run_font(run, size=12, bold=False, italic=False, color=None):
    run.font.name = FONT
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def set_paragraph_format(p, *, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6,
                         space_before=0, first_line=None, line=1.5):
    pf = p.paragraph_format
    pf.alignment = align
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line
    if first_line is not None:
        pf.first_line_indent = Cm(first_line)


def add_formatted_runs(paragraph, text, size=12, bold=False):
    """Render *italic* and **bold** markdown in a paragraph."""
    parts = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            set_run_font(run, size=size, bold=True)
        elif part.startswith("*") and part.endswith("*"):
            run = paragraph.add_run(part[1:-1])
            set_run_font(run, size=size, italic=True, bold=bold)
        else:
            run = paragraph.add_run(part)
            set_run_font(run, size=size, bold=bold)


def shade_cell(cell, hex_color="1E2761"):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def set_cell_border(cell):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "666666")
        tcBorders.append(el)
    tcPr.append(tcBorders)


def add_table(doc, headers, rows, caption):
    cap = doc.add_paragraph()
    set_paragraph_format(cap, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=4, line=1.15)
    run = cap.add_run(caption)
    set_run_font(run, size=11, bold=True, italic=True)

    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.autofit = True
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2, line=1.0)
        run = p.add_run(h)
        set_run_font(run, size=9, bold=True, color=RGBColor(255, 255, 255))
        shade_cell(hdr[i], "1E2761")
        set_cell_border(hdr[i])
    for r_i, row in enumerate(rows):
        cells = table.rows[r_i + 1].cells
        bg = "F4F6FB" if r_i % 2 == 0 else "FFFFFF"
        for c_i, val in enumerate(row):
            cells[c_i].text = ""
            p = cells[c_i].paragraphs[0]
            align = WD_ALIGN_PARAGRAPH.LEFT if c_i == 0 else WD_ALIGN_PARAGRAPH.CENTER
            set_paragraph_format(p, align=align, space_after=1, line=1.0)
            run = p.add_run(val)
            set_run_font(run, size=9)
            shade_cell(cells[c_i], bg)
            set_cell_border(cells[c_i])
    return table


def add_picture_with_caption(doc, path, caption, width=6.2):
    p = doc.add_paragraph()
    set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=2, line=1.0)
    p.add_run().add_picture(str(path), width=Inches(width))
    cap = doc.add_paragraph()
    set_paragraph_format(cap, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10, line=1.15)
    run = cap.add_run(caption)
    set_run_font(run, size=11, italic=True)


def generate_conceptual_framework(path: Path):
    fig, ax = plt.subplots(figsize=(10.6, 6.2))
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    def box(x, y, w, h, title, body, fc="#E8EEF9", ec="#1E2761"):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                           linewidth=1.4, facecolor=fc, edgecolor=ec)
        ax.add_patch(p)
        ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="top",
                fontsize=9, fontweight="bold", color="#1E2761", fontname="DejaVu Serif")
        ax.text(x + w / 2, y + h / 2 - 0.12, body, ha="center", va="center",
                fontsize=8, color="#222222", fontname="DejaVu Serif", wrap=True)

    box(0.25, 2.15, 2.55, 2.5, "Independent variables (X)",
        "GRU depth & width\nTD-A* heuristic\nThreshold δ\nDataset", fc="#DCE6F8")
    box(3.35, 1.85, 3.9, 3.1, "Mediating artefact",
        "1  GRU 60 min → 30 min speeds\n2  Time-dependent A*\n3  Remaining-time controller\n"
        "Dispatcher retains authority", fc="#F7F1DC")
    box(7.8, 2.15, 2.55, 2.5, "Dependent variables (Y)",
        "Journey time\nGap to oracle\nLatency (ms)\nReplans / trip", fc="#DCEFE4")
    box(1.7, 0.25, 7.2, 1.25, "Moderators (act on all three components)",
        "Congestion regime   ·   Time of day   ·   Path length   ·   Sensor coverage (held at 100% on the 900-run graph)",
        fc="#F4E6E6")

    ax.annotate("", xy=(3.30, 3.4), xytext=(2.85, 3.4),
                arrowprops=dict(arrowstyle="-|>", color="#1E2761", lw=1.6))
    ax.annotate("", xy=(7.75, 3.4), xytext=(7.30, 3.4),
                arrowprops=dict(arrowstyle="-|>", color="#1E2761", lw=1.6))
    ax.annotate("", xy=(5.3, 1.85), xytext=(5.3, 1.55),
                arrowprops=dict(arrowstyle="-|>", color="#7A3030", lw=1.3))

    ax.set_title("Figure 1. Conceptual framework of the study",
                 fontsize=11, fontname="DejaVu Serif", pad=8, color="#1E2761")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def generate_latency_figure(path: Path):
    labels = ["TD-A* search", "GRU inference", "Combined wait", "Dispatch cap"]
    values = [0.37, 39.3, 40.0, 1000.0]
    colors = ["#4C78A8", "#F58518", "#54A24B", "#B0B0B0"]
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.62)
    ax.set_xlabel("Milliseconds (log scale)", fontsize=10)
    ax.set_xscale("log")
    ax.set_xlim(0.2, 1600)
    ax.axvline(1000, color="#C44E52", ls="--", lw=1.1)
    for bar, val in zip(bars, values[::-1]):
        ax.text(val * 1.08, bar.get_y() + bar.get_height() / 2,
                f"{val:g} ms", va="center", fontsize=9)
    ax.set_title("Computational wait against the 1,000 ms dispatch cap", fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def parse_md(text: str):
    lines = text.splitlines()
    title = lines[0][2:].strip()
    # author block until Abstract
    i = 1
    authors = []
    while i < len(lines) and not lines[i].startswith("## Abstract"):
        if lines[i].strip():
            authors.append(lines[i].strip())
        i += 1
    i += 1  # skip ## Abstract
    abstract_lines = []
    while i < len(lines) and not lines[i].startswith("**Keywords:**"):
        if lines[i].strip():
            abstract_lines.append(lines[i].strip())
        i += 1
    keywords = lines[i].replace("**Keywords:**", "").strip()
    i += 1
    body = lines[i:]
    return title, authors, " ".join(abstract_lines), keywords, body


def parse_table_block(lines, start):
    """Return headers, rows, next_index for a markdown table starting at start."""
    rows = []
    j = start
    while j < len(lines) and lines[j].strip().startswith("|"):
        raw = [c.strip() for c in lines[j].strip().strip("|").split("|")]
        if not all(set(c) <= set("-: ") and c for c in raw):
            rows.append(raw)
        j += 1
    headers, data = rows[0], rows[1:]
    return headers, data, j


def build():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig1 = FIG_DIR / "figure1_conceptual_framework.png"
    fig6 = FIG_DIR / "figure6_latency.png"
    generate_conceptual_framework(fig1)
    generate_latency_figure(fig6)

    figure_files = {
        1: fig1,
        3: SIM_FIG / "fig3_delta_sensitivity.png",
        4: SIM_FIG / "fig1_travel_time_comparison.png",
        5: SIM_FIG / "fig2_reduction_by_scenario.png",
        6: fig6,
    }

    md = MD.read_text(encoding="utf-8")
    title, authors, abstract, keywords, body = parse_md(md)

    doc = Document()
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)

    # Title
    p = doc.add_paragraph()
    set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12, line=1.15)
    run = p.add_run(title)
    set_run_font(run, size=16, bold=True)

    # Authors / affiliations / emails (RAG layout)
    for line in authors:
        p = doc.add_paragraph()
        set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2, line=1.15)
        size = 11 if line.startswith("¹") or line.startswith("²") or line.startswith("*") else 12
        bold = not (line.startswith("¹") or line.startswith("²") or line.startswith("*"))
        add_formatted_runs(p, line, size=size, bold=bold)

    # Abstract heading
    p = doc.add_paragraph()
    set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=14, space_after=4, line=1.15)
    run = p.add_run("Abstract")
    set_run_font(run, size=12, bold=True)

    p = doc.add_paragraph()
    set_paragraph_format(p, space_after=8, first_line=0)
    add_formatted_runs(p, abstract, size=12)

    p = doc.add_paragraph()
    set_paragraph_format(p, space_after=12, line=1.15)
    run = p.add_run("Keywords: ")
    set_run_font(run, size=12, bold=True, italic=True)
    run = p.add_run(keywords)
    set_run_font(run, size=12, italic=True)

    i = 0
    pending_table_caption = None
    pending_figure = None  # (number, caption)

    while i < len(body):
        line = body[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("|") and pending_table_caption:
            headers, rows, nxt = parse_table_block(body, i)
            add_table(doc, headers, rows, pending_table_caption)
            pending_table_caption = None
            i = nxt
            continue

        if stripped.startswith("## "):
            p = doc.add_paragraph()
            set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=14, space_after=6, line=1.15)
            run = p.add_run(stripped[3:])
            set_run_font(run, size=13, bold=True)
            i += 1
            continue

        if stripped.startswith("### "):
            p = doc.add_paragraph()
            set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=4, line=1.15)
            run = p.add_run(stripped[4:])
            set_run_font(run, size=12, bold=True)
            i += 1
            continue

        if stripped.startswith("**Table "):
            pending_table_caption = stripped.replace("**", "").strip()
            i += 1
            continue

        if stripped.startswith("**Figure "):
            cap = stripped.replace("**", "").strip()
            m = re.match(r"Figure (\d+)\.", cap)
            num = int(m.group(1)) if m else None
            fpath = figure_files.get(num)
            if fpath and fpath.exists():
                add_picture_with_caption(doc, fpath, cap, width=6.1 if num != 1 else 6.3)
            else:
                p = doc.add_paragraph()
                set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=8, line=1.15)
                run = p.add_run(cap)
                set_run_font(run, size=11, italic=True)
            i += 1
            continue

        if stripped.startswith("*Note.*"):
            p = doc.add_paragraph()
            set_paragraph_format(p, space_after=8, line=1.15)
            add_formatted_runs(p, stripped, size=10)
            i += 1
            continue

        # Reference entries (after References heading): hanging indent
        # Detect by being in references: we use a simple heuristic — line starts with author surname pattern
        # Handled once we have seen "## References"
        p = doc.add_paragraph()
        # hanging indent for reference list items (no heading markers)
        is_ref = bool(re.match(r"^[A-Z].+\(\d{4}", stripped))
        if is_ref:
            set_paragraph_format(p, space_after=4, line=1.15)
            p.paragraph_format.left_indent = Cm(1.27)
            p.paragraph_format.first_line_indent = Cm(-1.27)
            add_formatted_runs(p, stripped, size=11)
        else:
            set_paragraph_format(p, space_after=8, first_line=0.75)
            add_formatted_runs(p, stripped, size=12)
        i += 1

    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
