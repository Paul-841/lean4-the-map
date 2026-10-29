# -*- coding: utf-8 -*-
"""Structural QA for a Lean4_The_Map deck.

Usage:
    python qa_deck.py [path/to/deck.pptx]

Checks: canvas, out-of-bounds shapes, page numbers, speaker notes,
watermark leftovers, in-deck "slide NN" references, rough text overflow,
and the per-slide time budget carried in the notes.
"""
import os
import re
import sys

from pptx import Presentation

EMU_IN = 914400
DEFAULT = r"D:\Plan\AI_learning_ZCode\Lean4_The_Map_v15.4.pptx"
PATH = sys.argv[1] if len(sys.argv) > 1 else DEFAULT

if not os.path.exists(PATH):
    print(f"deck not found: {PATH}")
    sys.exit(2)

prs = Presentation(PATH)
W, H = prs.slide_width / EMU_IN, prs.slide_height / EMU_IN
N = len(prs.slides)
print(f"file   : {PATH}")
print(f"slides : {N}   canvas: {W:.3f}x{H:.3f} in")

WATERMARKS = ("千问", "AI生成", "AI 生成", "ChatGPT", "GPT-4", "Claude", "DeepSeek", "Gemini")


def walk(shapes):
    for sh in shapes:
        if sh.shape_type == 6:
            yield from walk(sh.shapes)
        else:
            yield sh


issues = 0
notes_ok = 0
budget = 0.0
all_text = []

for idx, slide in enumerate(prs.slides, 1):
    texts = []
    for sh in walk(slide.shapes):
        try:
            x, y = sh.left / EMU_IN, sh.top / EMU_IN
            w, h = sh.width / EMU_IN, sh.height / EMU_IN
        except TypeError:
            continue
        if x < -0.05 or y < -0.05 or x + w > W + 0.05 or y + h > H + 0.05:
            print(f"  S{idx} OUT-OF-BOUNDS at ({x:.2f},{y:.2f}) {w:.2f}x{h:.2f} "
                  f"text={getattr(sh, 'text', '')[:40]!r}")
            issues += 1
        if not sh.has_text_frame:
            continue
        t = sh.text_frame.text
        if not t.strip():
            continue
        texts.append(t)
        # rough overflow estimate: does the text need more height than the box?
        # advance width per char, in em: Calibri ~0.48, Consolas 0.55 (monospace)
        EM = {"Consolas": 0.55}

        def para_width(para, fs):
            total = 0.0
            for run in para.runs:
                sz = run.font.size.pt if run.font.size else fs
                em = EM.get(run.font.name, 0.48)
                if run.font.bold:
                    em *= 1.04
                total += len(run.text) * em * sz / 72.0
            return total

        fs = 0
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                if run.font.size:
                    fs = max(fs, run.font.size.pt)
        if fs == 0:
            fs = 18
        lines = 0
        for para in sh.text_frame.paragraphs:
            pw = para_width(para, fs)
            lines += max(1, int(pw / w) + (1 if pw % w else 0))
        need = lines * fs * 1.35 / 72
        if need > h + 0.12:
            print(f"  S{idx} MAYBE-OVERFLOW fs={fs:.0f} box={w:.2f}x{h:.2f} "
                  f"need_h~{need:.2f} lines~{lines} text={t[:40]!r}")
            issues += 1
    all_text.append("\n".join(texts))

    # page number: the small text box in the bottom-right corner
    nums = []
    for sh in walk(slide.shapes):
        try:
            x, y = sh.left / EMU_IN, sh.top / EMU_IN
        except TypeError:
            continue
        if sh.has_text_frame and x > 11.5 and y > 6.8:
            t = sh.text_frame.text.strip()
            if re.fullmatch(r"\d+", t):
                nums.append(t)
    if idx == 1:
        if nums:
            print(f"  S{idx} TITLE carries a page number {nums} (expected none)")
            issues += 1
    elif nums != [str(idx)]:
        print(f"  S{idx} PAGE-NUMBER mismatch: found {nums}, expected ['{idx}']")
        issues += 1

    # speaker notes
    if slide.has_notes_slide:
        t = slide.notes_slide.notes_text_frame.text.strip()
        if t:
            notes_ok += 1
            m = re.search(r"【\s*([\d.]+)\s*min", t)
            if not m:
                print(f"  S{idx} NOTES missing a 【time】 marker")
                issues += 1
            else:
                budget += float(m.group(1))
        else:
            print(f"  S{idx} NOTES empty")
            issues += 1
    else:
        print(f"  S{idx} NO notes slide")
        issues += 1

print(f"notes : {notes_ok}/{N} slides carry non-empty notes with a time marker")
print(f"time budget: {budget:.1f} min")

wm = [(i, b) for i, t in enumerate(all_text, 1) for b in WATERMARKS if b in t]
print(f"watermark scan: {'CLEAN' if not wm else wm}")
if wm:
    issues += len(wm)

refs = []
for idx, t in enumerate(all_text, 1):
    for m in re.finditer(r"slides?\s+(\d+)(?:\s*(?:to|and)\s*(\d+))?", t):
        a = int(m.group(1))
        b = int(m.group(2) or a)
        refs.append((idx, m.group(0), a, b))
print("in-deck page references:")
for idx, txt, a, b in refs:
    bad = not (1 <= a <= N and 1 <= b <= N)
    print(f"  S{idx}: {txt!r} -> slides {a}..{b}   {'*** OUT OF RANGE ***' if bad else 'ok'}")
    if bad:
        issues += 1

print("ISSUES:", issues)
