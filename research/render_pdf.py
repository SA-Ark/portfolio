#!/usr/bin/env python3
"""Render the BlueRobins competition research markdown as a print-ready PDF."""
import re, sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether, HRFlowable)

SRC, OUT = sys.argv[1], sys.argv[2]

L = "/usr/share/fonts/truetype/liberation/"
D = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DJ",   L + "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("DJ-B", L + "LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DJ-I", L + "LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("DJ-BI",L + "LiberationSans-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("DJM",  D + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DJ", normal="DJ", bold="DJ-B", italic="DJ-I", boldItalic="DJ-BI")

INK   = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5b6472")
RULE  = colors.HexColor("#d6dae0")
BAND  = colors.HexColor("#0f3057")
LABEL = colors.HexColor("#eef1f5")
ZEBRA = colors.HexColor("#f8f9fb")
RED   = colors.HexColor("#a4161a")
AMBER = colors.HexColor("#8a5a00")
BLUE  = colors.HexColor("#1d4ed8")

def S(name, **kw):
    kw.setdefault("fontName", "DJ"); kw.setdefault("textColor", INK)
    kw.setdefault("alignment", TA_LEFT)
    return ParagraphStyle(name, **kw)

st = {
 "title":  S("title",  fontName="DJ-B", fontSize=21, leading=26, spaceAfter=4,  textColor=BAND),
 "subtit": S("subtit", fontSize=10.5, leading=15, textColor=MUTED, spaceAfter=2),
 "band":   S("band",   fontName="DJ-B", fontSize=15, leading=19, spaceBefore=16, spaceAfter=7,
             textColor=colors.white, backColor=BAND, borderPadding=(7,9,8,9)),
 "h2":     S("h2",     fontName="DJ-B", fontSize=13, leading=17, spaceBefore=15, spaceAfter=6, textColor=BAND),
 "h3":     S("h3",     fontName="DJ-B", fontSize=11, leading=15, spaceBefore=13, spaceAfter=5, textColor=INK),
 "body":   S("body",   fontSize=8.9, leading=12.6, spaceAfter=6),
 "quote":  S("quote",  fontSize=8.6, leading=12.4, spaceAfter=6, leftIndent=11,
             borderPadding=(5,7,6,8), backColor=colors.HexColor("#f2f5f9"), textColor=colors.HexColor("#2b3440")),
 "li":     S("li",     fontSize=8.9, leading=12.4, spaceAfter=3, leftIndent=13, bulletIndent=3),
 "cellL":  S("cellL",  fontName="DJ-B", fontSize=8.1, leading=11.2, textColor=colors.HexColor("#333b47")),
 "cell":   S("cell",   fontSize=8.1, leading=11.4),
 "cellH":  S("cellH",  fontName="DJ-B", fontSize=8.1, leading=11.2, textColor=colors.white),
}

EMOJI = {
 "\U0001F6A9": ('FLAG',      RED),
 "⚠":     ('!',         AMBER),
 "❌":     ('CUT',       RED),
 "\U0001F534": ('URGENT',    RED),
 "\U0001F535": ('CONFIRMED', BLUE),
 "⏰":     ('SOON',      RED),
 "⏳":     ('CLOSED',    AMBER),
 "\U0001F6AB": ('BLOCKED',   RED),
}

REDUNDANT = {
 "CUT":  re.compile(r"\bCUT\b", re.I),
 "FLAG": re.compile(r"\bflag(ged)?\b", re.I),
 "!":    re.compile(r"\bflag(ged)?\b", re.I),
}

def inline(t):
    t = t.replace("️", "")
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for ch, (tag, col) in EMOJI.items():
        if ch not in t:
            continue
        # drop the marker when the surrounding text already says the same thing
        if REDUNDANT.get(tag) and REDUNDANT[tag].search(t):
            t = t.replace(ch, "")
        else:
            t = t.replace(ch, '<font color="#%s"><b>[%s]</b></font> ' % (col.hexval()[2:], tag))
    t = re.sub(r"`([^`]+)`", r'<font name="DJM" size="7.6">\1</font>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t, flags=re.S)
    t = re.sub(r"(?<![\*\w])\*([^*\n]+?)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"(?<!\w)_([^_\n]+?)_(?!\w)", r"<i>\1</i>", t)
    # markdown links, then bare urls
    t = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
               r'<link href="\2" color="#1d4ed8">\1</link>', t)
    t = re.sub(r"(?<!href=\")(?<!>)(https?://[^\s<)|]+)",
               r'<link href="\1" color="#1d4ed8">\1</link>', t)
    return t

def P(t, style="body"):
    return Paragraph(inline(t), st[style])

def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]

def widths(header, ncols, avail):
    h = " ".join(header).lower()
    if ncols == 2:
        return [1.42*inch, avail - 1.42*inch]
    if ncols == 3 and "count" in h:
        return [2.05*inch, 0.62*inch, avail - 2.67*inch]
    if ncols == 3:
        return [1.45*inch, avail - 3.35*inch, 0.9*inch]
    return [avail/ncols]*ncols

def build_table(rows, avail):
    header, body = rows[0], rows[1:]
    ncols = len(header)
    # "Field | Detail" tables: header is decorative, render as label/value grid
    fieldstyle = ncols == 2 and header[0].strip("*").lower() == "field"
    data, cmds = [], []
    start = 0
    if not fieldstyle:
        data.append([Paragraph(inline(c), st["cellH"]) for c in header])
        cmds += [("BACKGROUND", (0,0), (-1,0), BAND)]
        start = 1
    for i, r in enumerate(body):
        r = (r + [""]*ncols)[:ncols]
        cells = []
        for j, c in enumerate(r):
            cells.append(Paragraph(inline(c), st["cellL"] if (j == 0 and ncols == 2) else st["cell"]))
        data.append(cells)
        if start and i % 2 == 1:
            cmds.append(("BACKGROUND", (0, i+start), (-1, i+start), ZEBRA))
    if ncols == 2:
        cmds.append(("BACKGROUND", (0, start), (0, -1), LABEL))
    cmds += [
        ("GRID", (0,0), (-1,-1), 0.4, RULE),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4),  ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]
    t = Table(data, colWidths=widths(header, ncols, avail), repeatRows=start, hAlign="LEFT")
    t.setStyle(TableStyle(cmds))
    return t

def parse(md, avail):
    flow, lines, i = [], md.split("\n"), 0
    first_h1 = True
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("|") and i+1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i+1]):
            rows = [split_row(ln)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i])); i += 1
            flow.append(Spacer(1, 3)); flow.append(build_table(rows, avail)); flow.append(Spacer(1, 8))
            continue
        if re.match(r"^\s*(---|___|\*\*\*)\s*$", ln):
            flow.append(Spacer(1, 5))
            flow.append(HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=7))
            i += 1; continue
        m = re.match(r"^(#{1,3})\s+(.*)$", ln)
        if m:
            lvl, txt = len(m.group(1)), m.group(2)
            if lvl == 1 and first_h1:
                first_h1 = False
                flow.append(P(txt, "title")); i += 1; continue
            flow.append(P(txt, {1:"band", 2:"h2", 3:"h3"}[lvl]))
            if lvl == 1:
                flow.append(Spacer(1, 7))
            i += 1; continue
        if ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip()); i += 1
            flow.append(P(" ".join(buf), "quote")); flow.append(Spacer(1, 4)); continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", ln)
        if m:
            indent = len(m.group(1)) // 2
            marker, txt = m.group(2), m.group(3)
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(\s*)([-*]|\d+\.)\s+|^\s*[#|>]|^\s*---", lines[i]):
                txt += " " + lines[i].strip(); i += 1
            bullet = "•" if marker in ("-", "*") else marker
            s = ParagraphStyle("x", parent=st["li"],
                               leftIndent=13 + indent*12, bulletIndent=3 + indent*12)
            flow.append(Paragraph(inline(txt), s, bulletText=bullet))
            continue
        if not ln.strip():
            i += 1; continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^\s*[#|>]|^\s*([-*]|\d+\.)\s|^\s*---", lines[i]):
            buf.append(lines[i].strip()); i += 1
        flow.append(P(" ".join(buf)))
    return flow

TITLE = "BlueRobins Competitions Page — Verified Candidate List"

def furniture(canv, doc):
    canv.saveState()
    canv.setFont("DJ", 7.2); canv.setFillColor(MUTED)
    canv.drawString(doc.leftMargin, letter[1] - 0.46*inch, TITLE)
    canv.drawRightString(letter[0] - doc.rightMargin, letter[1] - 0.46*inch, "Compiled 18 September 2026")
    canv.setStrokeColor(RULE); canv.setLineWidth(0.5)
    canv.line(doc.leftMargin, letter[1] - 0.55*inch, letter[0] - doc.rightMargin, letter[1] - 0.55*inch)
    canv.line(doc.leftMargin, 0.58*inch, letter[0] - doc.rightMargin, 0.58*inch)
    canv.drawString(doc.leftMargin, 0.42*inch, "Internal research — not for publication as written")
    canv.drawRightString(letter[0] - doc.rightMargin, 0.42*inch, "Page %d" % canv.getPageNumber())
    canv.restoreState()

doc = BaseDocTemplate(OUT, pagesize=letter,
                      leftMargin=0.62*inch, rightMargin=0.62*inch,
                      topMargin=0.72*inch, bottomMargin=0.72*inch,
                      title=TITLE, author="BlueRobins research",
                      subject="Verified competition candidate list for the Competitions page")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=furniture)])
doc.build(parse(open(SRC).read(), doc.width))
print("wrote", OUT)
