# -*- coding: utf-8 -*-
r"""
make_public_deck.py —— 从带演讲备注的教学版生成"公开版"（去备注），并把备注导出为 markdown

用法:
    $env:PYTHONIOENCODING="utf-8"
    uv run --with python-pptx python D:\Plan\AI_learning_ZCode\_review_v154\make_public_deck.py

产出:
  1) Lean4_The_Map_v15.4_public.pptx  —— 逐页删除 notesSlide 关系，正文/版式零改动
  2) Lean4_The_Map_v15.4_notes.md     —— 36 条备注全文（页码 + 标题 + 备注正文）
"""
import os
import sys
import zipfile
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.normpath(os.path.join(_HERE, ".."))
D = _REPO
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v16.0"
STEM = "Lean4_The_Map_" + VERSION
SRC = os.path.join(D, "build", STEM + ".pptx")
OUT_PPTX = os.path.join(D, "deck", STEM + ".pptx")
OUT_MD = os.path.join(D, "build", STEM + "_notes.md")

os.makedirs(os.path.join(D, "build"), exist_ok=True)

prs = Presentation(SRC)


def slide_title(slide):
    """取页面标题：位置最靠上且有文字的形状文本。"""
    best, best_top = None, None
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        t = sh.text_frame.text.strip()
        if not t:
            continue
        top = sh.top if sh.top is not None else 10 ** 9
        if best_top is None or top < best_top:
            best, best_top = t, top
    return (best or "").split("\n")[0]


# ---- 1. 先把备注全文导出来（删之前） ----
md = [
    "# Lean4_The_Map_v15.4 —— 演讲备注全文（36 页）",
    "",
    "> 本文件由 `make_public_deck.py` 从 `Lean4_The_Map_v15.4.pptx` 自动导出。",
    "> 格式为讲者备注三段式：`【时间｜定位】` / `主旨` / `要点` / `坑`。",
    "> **内部备课材料，未纳入公开仓库。**",
    "",
]
for i, s in enumerate(prs.slides, 1):
    note = s.notes_slide.notes_text_frame.text.strip() if s.has_notes_slide else ""
    md.append(f"## Slide {i} — {slide_title(s)}")
    md.append("")
    md.append("```")
    md.append(note if note else "(无备注)")
    md.append("```")
    md.append("")

with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

# ---- 2. 逐页删除 notesSlide 关系 ----
dropped = 0
for s in prs.slides:
    for rId, rel in list(s.part.rels.items()):
        if rel.reltype == RT.NOTES_SLIDE:
            s.part.drop_rel(rId)
            dropped += 1

prs.save(OUT_PPTX)

# ---- 3. 校验 ----
check = Presentation(OUT_PPTX)
left = sum(1 for s in check.slides if s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip())
paras_src = sum(1 for s in Presentation(SRC).slides for sh in s.shapes
                if sh.has_text_frame for p in sh.text_frame.paragraphs if p.text.strip())
paras_out = sum(1 for s in check.slides for sh in s.shapes
                if sh.has_text_frame for p in sh.text_frame.paragraphs if p.text.strip())

with zipfile.ZipFile(OUT_PPTX) as z:
    note_parts = [n for n in z.namelist() if "notesSlide" in n and n.endswith(".xml")]

print(f"drop_rel notesSlide : {dropped}")
print(f"public pptx         : {OUT_PPTX}")
print(f"  slides            : {len(check.slides)}")
print(f"  paragraphs        : {paras_out}  (源 {paras_src}  ->  {'一致' if paras_out == paras_src else '不一致!!'})")
print(f"  残留非空备注页     : {left}   (应为 0)")
print(f"  zip 内 notesSlide xml 片段: {len(note_parts)}")
print(f"notes markdown      : {OUT_MD}")
print(f"  bytes             : {os.path.getsize(OUT_MD)}")
