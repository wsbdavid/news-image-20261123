#!/usr/bin/env python3
"""Sum up 23 November 2026's world news in one image.

Entry for make.fun bounty "Sum up 23 November's world news in one image"
(https://make.fun/bounty/news-image-20261123) — $100, 50 places paid.

Writes one 1024x1024 PNG to /output/entry.png (or ./output/entry.png when
/output is not writable). No network access. Fully deterministic: the same
stories, fonts and layout on every run, so two runs write identical bytes.

Run:  python3 main.py
Needs: Python 3.13, Pillow. Fonts: DejaVu (bundled with most Linux images);
falls back to Pillow's built-in bitmap font if DejaVu is unavailable.

Stories were checked against wire/agency reports published 23 Nov 2026
(Xinhua, SCMP, Arab News/AP, Economic Times, Dawn, Inshorts). Figures are
the lowest reported tolls where outlets disagreed; nothing is invented.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
BG = (253, 252, 247)          # paper
INK = (18, 18, 18)
RULE = (18, 18, 18)
ACCENT = (158, 27, 27)        # deep red masthead accent
MUTED = (90, 90, 90)
LEAD_BG = (244, 238, 226)     # warm tint for the lead story

DATE_LINE = "MONDAY 23 NOVEMBER 2026  •  22 STORIES  •  7 REGIONS"

LEAD = {
    "kicker": "CLIMATE  •  ANTALYA, TÜRKİYE",
    "headline": "Climate talks end with no deal",
    "summary": (
        "COP31 closed after almost 48 hours of overtime with no overarching "
        "deal. The EU and about 130 countries rejected a text with no "
        "fossil-fuel phase-out."
    ),
}

# (region kicker, headline, one-line summary) — 16 grid stories.
GRID = [
    ("UNITED STATES",
     "Democrats clinch 258-seat House majority",
     "Largest House majority since 1992."),
    ("UKRAINE",
     "Russian strikes kill 11 around Kyiv",
     "Dymer attack kills six; a boy, 7, pulled alive."),
    ("INDONESIA",
     "Three dead, 34 missing in factory fire",
     "Blaze at a candy factory in Banten."),
    ("MIDDLE EAST",
     "Iran says it downed a US drone over Hormuz",
     "Tehran claims an MQ-9 Reaper shot down."),
    ("UNITED STATES",
     "Delta delays top 1,000 flights at Atlanta",
     "Fault hits flight systems before Thanksgiving."),
    ("SOUTH KOREA",
     "Education minister resigns over exam chaos",
     "Quits over cheating controls for the entrance exam."),
    ("UKRAINE  •  LIBYA",
     "Ukrainian drone hits Russian corvette",
     "The Merkury is hit off Libya."),
    ("YEMEN",
     "Strikes and drone attack kill five",
     "Five dead, 18 hurt across Yemen."),
    ("MEXICO",
     "FBI most-wanted drug kingpin captured",
     "Arrested in a deadly firefight."),
    ("INDIA",
     "Nepal PM welcomed in New Delhi",
     "First bilateral visit since taking office."),
    ("SOUTH SUDAN",
     "Attack leaves 24 civilians dead",
     "SPLA-IO forces blamed for the assault."),
    ("AFRICA  •  HEALTH",
     "Fighting disrupts Congo Ebola response",
     "WHO warns clashes hamper containment."),
    ("BUSINESS",
     "US probes Nvidia chip sales to China",
     "Bessent asks “where the buck stops”."),
    ("CANADA",
     "Carney jokes about Trump at comedy dinner",
     "PM pokes at US relations with comedians."),
    ("UNITED STATES",
     "Three dead in shooting at baby shower",
     "Nine also hurt in a California concert shooting."),
    ("UNITED KINGDOM",
     "UK digs new reservoirs to fight drought",
     "£800m reservoir under construction."),
]

# Short items for the bottom strip — 5 more stories, one line each.
BRIEFS = [
    "India and the EU are likely to sign a free-trade deal on 16 December.",
    "North Korea's Kim says his country seeks security, not supremacy.",
    "Liverpool thrash 10-man Man Utd in Pochettino's first match.",
    "Israel investigates West Bank fires blamed on settlers.",
    "US Army plans emergency disposal of bomb-making chemicals in Iowa.",
]


def load_font(bold=False, size=16):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(draw, text, font, max_w):
    """Wrap text to fit max_w pixels; returns a list of lines."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, font, max_w, max_lines):
    """Wrap and truncate with an ellipsis to at most max_lines lines."""
    lines = wrap(draw, text, font, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and draw.textlength(lines[-1] + " …", font=font) > max_w:
        lines[-1] = lines[-1][:-1]
    lines[-1] = lines[-1].rstrip() + " …"
    return lines


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([4, 4, W - 5, H - 5], outline=INK, width=2)

    f_title = load_font(bold=True, size=64)
    f_date = load_font(bold=False, size=19)
    f_kicker = load_font(bold=True, size=15)
    f_lead_head = load_font(bold=True, size=40)
    f_lead_sum = load_font(bold=False, size=20)
    f_head = load_font(bold=True, size=19)
    f_sum = load_font(bold=False, size=15)
    f_brief = load_font(bold=False, size=15)
    f_foot = load_font(bold=False, size=13)

    # ---- Masthead -------------------------------------------------------
    y = 22
    title = "THE WORLD"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, y), title, font=f_title, fill=INK)
    y += 74
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=3)
    y += 8
    dw = d.textlength(DATE_LINE, font=f_date)
    d.text(((W - dw) / 2, y), DATE_LINE, font=f_date, fill=ACCENT)
    y += 30
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)

    # ---- Lead story -----------------------------------------------------
    y += 12
    lead_h = 148
    d.rectangle([MARGIN, y, W - MARGIN, y + lead_h], fill=LEAD_BG)
    d.rectangle([MARGIN, y, W - MARGIN, y + lead_h], outline=INK, width=1)
    lx, lw = MARGIN + 16, W - 2 * MARGIN - 32
    ly = y + 10
    d.text((lx, ly), LEAD["kicker"], font=f_kicker, fill=ACCENT)
    ly += 24
    for line in fit_lines(d, LEAD["headline"], f_lead_head, lw, 1):
        d.text((lx, ly), line, font=f_lead_head, fill=INK)
        ly += 46
    for line in fit_lines(d, LEAD["summary"], f_lead_sum, lw, 2):
        d.text((lx, ly), line, font=f_lead_sum, fill=INK)
        ly += 26
    y += lead_h + 14

    # ---- Grid: 2 columns x 8 rows --------------------------------------
    col_w = (W - 2 * MARGIN - 16) // 2
    card_h = 62
    gap = 5
    for i, (kicker, head, summ) in enumerate(GRID):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (col_w + 16)
        cy = y + row * (card_h + gap)
        d.line([(x, cy + 2), (x + col_w, cy + 2)], fill=(200, 196, 186), width=1)
        d.text((x, cy + 6), kicker, font=f_kicker, fill=ACCENT)
        hy = cy + 25
        for line in fit_lines(d, head, f_head, col_w, 1):
            d.text((x, hy), line, font=f_head, fill=INK)
            hy += 23
        for line in fit_lines(d, summ, f_sum, col_w, 1):
            d.text((x, hy), line, font=f_sum, fill=MUTED)

    y = y + 8 * (card_h + gap) + 2

    # ---- The day in brief ----------------------------------------------
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=2)
    y += 8
    d.text((MARGIN, y), "THE DAY IN BRIEF", font=f_kicker, fill=ACCENT)
    y += 22
    for item in BRIEFS:
        d.text((MARGIN, y), "•  " + item, font=f_brief, fill=INK)
        y += 21

    # ---- Footer ---------------------------------------------------------
    fy = H - 30
    d.line([(MARGIN, fy), (W - MARGIN, fy)], fill=RULE, width=1)
    foot = "Stories checked against wire and agency reports published 23 Nov 2026  •  One page, no photos"
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, fy + 6), foot, font=f_foot, fill=MUTED)

    out_dir = "/output" if os.access("/output", os.W_OK) else "output"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print(out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
