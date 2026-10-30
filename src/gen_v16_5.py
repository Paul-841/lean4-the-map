# -*- coding: utf-8 -*-
"""Generate Lean4_The_Map_v11.pptx"""
import os as _os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from datetime import datetime
import copy

# ---------- palette ----------
INK      = RGBColor(0x1a, 0x1a, 0x1a)
BODY     = RGBColor(0x33, 0x33, 0x33)
MUTED    = RGBColor(0x88, 0x88, 0x88)
CODE_BG  = RGBColor(0xF4, 0xF4, 0xF4)
CODE_FG  = RGBColor(0x1a, 0x1a, 0x1a)
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
LINE     = RGBColor(0xDD, 0xDD, 0xDD)

A_COLOR  = RGBColor(0x25, 0x63, 0xEB)  # blue
B_COLOR  = RGBColor(0x05, 0x96, 0x69)  # green
C_COLOR  = RGBColor(0xD9, 0x77, 0x06)  # amber
D_COLOR  = RGBColor(0x7C, 0x3A, 0xED)  # purple
ACCENT   = RGBColor(0xDC, 0x26, 0x26)  # red for warnings

MONO = "Consolas"
# Consolas 没有 ⊤(U+22A4) ⊥(U+22A5) ⇒(U+21D2)，回退后会细到看不清。
# Cambria Math：Windows 7+ / Office 自带，覆盖这两个码位，跨机器放映最稳。
SYM  = "Cambria Math"
SANS = "Calibri"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

# ---------- helpers ----------
def add_slide():
    return prs.slides.add_slide(BLANK)

def textbox(slide, left, top, width, height, text, size=14, bold=False,
            color=BODY, font=SANS, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = font
    return tb

def code_block(slide, left, top, width, height, code, size=13, font=MONO):
    """Gray rounded rect + mono text.

    font= 可覆盖：Consolas 缺某些数学符号（如 ⊤ ⊥），单独换字体渲染。
    """
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                 Inches(left), Inches(top), Inches(width), Inches(height))
    box.fill.solid()
    box.fill.fore_color.rgb = CODE_BG
    box.line.color.rgb = LINE
    box.line.width = Pt(0.5)
    box.shadow.inherit = False
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.06)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)
    lines = code.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = line if line else " "
        r.font.size = Pt(size)
        r.font.name = font
        r.font.color.rgb = CODE_FG
    return box

def title_bar(slide, text, color=INK):
    # Keep the title on ONE line. Calibri bold advances ~0.48 em/char; the box
    # is 12.0 in wide. A wrapped title would spill past the rule at y=1.05.
    size = 28
    while size > 20 and len(text) * 0.48 * 1.04 * size / 72.0 > 11.8:
        size -= 1
    textbox(slide, 0.7, 0.35, 12, 0.7, text, size=size, bold=True, color=color)
    # thin underline
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  Inches(0.7), Inches(1.05), Inches(11.9), Pt(2))
    line.fill.solid(); line.fill.fore_color.rgb = color
    line.line.fill.background()
    line.shadow.inherit = False

def tag(slide, left, top, letter, color, label):
    """A small colored circle with letter + label."""
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(left), Inches(top),
                               Inches(0.45), Inches(0.45))
    c.fill.solid(); c.fill.fore_color.rgb = color
    c.line.fill.background(); c.shadow.inherit = False
    tf = c.text_frame; tf.margin_top=Pt(0); tf.margin_bottom=Pt(0)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = letter
    r.font.size = Pt(16); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = SANS
    textbox(slide, left+0.55, top+0.05, 4, 0.4, label, size=14, bold=True, color=color)

def bullet(slide, left, top, width, items, size=14, gap=0.32, height=5):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame; tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(4)
        r = p.add_run(); r.text = "•  " + it
        r.font.size = Pt(size); r.font.color.rgb = BODY; r.font.name = SANS
    return tb

def page_num(slide, n=None):
    n = len(prs.slides) if n is None else n
    textbox(slide, 12.3, 7.1, 0.8, 0.3, str(n), size=10, color=MUTED, align=PP_ALIGN.RIGHT)

def rich(slide, left, top, width, height, rows, size=12, space_after=2):
    """rows: list of lines; each line = list of run dicts
       {"t": text, "f": font, "c": color, "b": bold}"""
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, runs in enumerate(rows):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        for rd in runs:
            r = p.add_run()
            r.text = rd.get("t", "")
            r.font.size = Pt(rd.get("sz", size))
            r.font.bold = bool(rd.get("b", False))
            r.font.name = rd.get("f", SANS)
            r.font.color.rgb = rd.get("c", BODY)
    return tb

def notes(slide, text):
    """Speaker notes for this slide."""
    slide.notes_slide.notes_text_frame.text = text
    return slide

# ============================================================
# SLIDE 1 — Title
# ============================================================
s = add_slide()
notes(s, """【0.5 min｜开场】
主旨：这不是"从零学编程"，是一张地图。先看 Lean 已经会什么，再学怎么命名、怎么证。

要点：
- 一句话定位：我们都懂 PDE，Lean 对大家是新的。今天不背语法，目标是"知道每个词住在哪个房子里"。
- 最后一页是给你们的：第 33 页讲 Mathlib 到底有什么，专门给 PDE 背景的人。
- 全场时间预算：幻灯片约 36 分钟，讨论 20 分钟。

坑：开场就有人问"Lean 能不能证 2D Euler 正则性"——现在挡掉，第 33 页正面讲。今天不承诺任何东西。""")
textbox(s, 1, 2.05, 11.3, 1.1, "The Map of Lean 4", size=48, bold=True, color=INK)
textbox(s, 1, 3.20, 11.3, 0.45,
        "v16.5  ·  Research group meeting  ·  29 October 2026",
        size=18, color=MUTED)
textbox(s, 1, 3.75, 11.3, 0.45,
        "For this room: PDE is home turf, Lean is not. No computer science assumed.",
        size=15, color=BODY)
textbox(s, 1, 4.35, 11.3, 1.5,
        "First: what Lean already knows.\n"
        "Then: how to name it and build on it.\n"
        "Along the way: where each word lives (A/B/C/D).",
        size=18, color=BODY)
textbox(s, 1, 6.05, 11.3, 0.4,
        "Open Lean4_practice.lean alongside this deck. Type as we go.",
        size=13, color=A_COLOR, bold=True)
textbox(s, 1, 6.55, 11.3, 0.5,
        "We end on the gap: the analysis layer is there; the PDE layer is not.",
        size=13, color=MUTED)

# ============================================================
# SLIDE 2 — Premise
# ============================================================
s = add_slide()
notes(s, """【1 min｜前提】
主旨：数学比 Lean 大。Lean 只检查其中很小的一个片段。

要点：
- Lean 是形式语言；一个小内核只做一件事——检查"这个项的类型对不对"。
- 它不判断你的形式化是否等于你心里的数学。这句是全场的安全带，每隔几页要重申一次。
- 今天的顺序：先看 Lean 已经会什么 → 怎么给它东西命名 → 怎么写证明。

坑：一定有人会问"那我把定义写错了怎么办"。答案：它只保证类型，不保证意义。这正是我们要小心的地方。""")
title_bar(s, "The premise: mathematics is larger, Lean checks a fragment")
bullet(s, 0.7, 1.4, 6, [
    "Mathematics: ideas, definitions, examples, proofs in ordinary language.",
    "Lean 4: a formal language. A small kernel checks that a term has the stated type.",
    "Lean does NOT decide whether your formalization matches the math you meant.",
    "Start from the mathematics. Use Lean to make one piece checkable.",
], size=15)
# right side: three ideas
textbox(s, 7.2, 1.4, 5.5, 0.4, "Three ideas to keep in mind", size=16, bold=True, color=INK)
items = [
    ("Curry–Howard", "Propositions are types. Proofs are terms of those types."),
    ("Meaning triangle", "A symbol never touches its referent directly. Thought mediates."),
    ("Desirable difficulty", "Retrieval and spacing help. You will get confused on purpose."),
]
y = 2.0
for h, d in items:
    textbox(s, 7.2, y, 5.5, 0.35, h, size=14, bold=True, color=C_COLOR)
    textbox(s, 7.2, y+0.35, 5.5, 0.5, d, size=12, color=BODY)
    y += 1.0
page_num(s)

# ============================================================
# NEW SLIDE 3 — What is computation?
# ============================================================
s = add_slide()
notes(s, """【0.5 min｜计算观】
主旨：两种计算模型，同一种能力；Lean's kernel 就是一个带类型的 lambda 演算。

要点：
- Turing 那边：无限纸带 + 读写头 + 状态，每步"读一格、决定写什么、往哪走"。整台机器就这些。
- Church 那边：没有纸带、没有状态，只有变量、λ、应用三条规则。整个演算就这些。
- 1936 年两人证明这两种模型算的东西完全一样 —— 这是 Church–Turing 论题的一根支柱。

坑：别说"这就是 Church–Turing 定理"。等价性只是支柱之一，论题本身更宽。被追问就承认这一点，别硬撑。""")
title_bar(s, "What is computation? Two answers, one result")
# Left: Turing
box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(1.4), Inches(5.8), Inches(3.5))
box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0xF5,0xF5,0xF5)
box.line.color.rgb = LINE; box.shadow.inherit=False
textbox(s, 1.0, 1.55, 5.2, 0.5, "Turing (1936)", size=18, bold=True, color=INK)
textbox(s, 1.0, 2.15, 5.2, 2.5,
        "An infinite tape divided into cells.\n"
        "A read/write head moves left and right.\n"
        "At each step: read the cell, decide\n"
        "what to write, move, change state.\n\n"
        "That is the whole machine.",
        size=13, color=BODY)
# Right: Lambda
box2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.4), Inches(5.8), Inches(3.5))
box2.fill.solid(); box2.fill.fore_color.rgb = RGBColor(0xF5,0xF5,0xF5)
box2.line.color.rgb = LINE; box2.shadow.inherit=False
textbox(s, 7.2, 1.55, 5.2, 0.5, "Church (1936)", size=18, bold=True, color=INK)
textbox(s, 7.2, 2.15, 5.2, 2.5,
        "No tape, no states. Everything is a function.\n"
        "Three rules only:\n"
        "  x        a variable\n"
        "  λx. e    a function (input x, body e)\n"
        "  f a      apply f to a\n\n"
        "That is the whole calculus.",
        size=13, color=BODY, font=MONO)
textbox(s, 0.7, 5.2, 12, 1.0,
        "They proved these two models have the same power. "
        "This equivalence is a pillar of the Church-Turing thesis. Lean's kernel is a typed lambda calculus.",
        size=14, bold=True, color=A_COLOR)
page_num(s)

# ============================================================
# NEW SLIDE 4 — What is a proof?
# ============================================================
s = add_slide()
notes(s, """【0.5 min｜证明】
主旨：从 Hilbert 纲领到机器检查；Gödel 没有杀死这件事。

要点：
- Hilbert (1900)：把数学写成公理 + 固定推理规则，那么证明就是机械的，不需要直觉。
- Gödel (1931)：任何强到能表达算术的系统都无法在内部证明自己一致。但这不是说单条证明不能被机器逐步检查。
- 活下来的是这个：一条证明可以被写成让机器检查每一步的样子。Lean 干的就是这件事。

坑：Gödel 第二不完备不要展开，点到为止。这页不是重点，是背景板。""")
title_bar(s, "What is a proof? From Hilbert to machine-checking")
bullet(s, 0.7, 1.4, 12, [
    "Hilbert (1900): write all mathematics as axioms + fixed inference rules. Then a proof is mechanical — no intuition needed.",
    "Gödel (1931): no system strong enough for arithmetic can prove its own consistency. But this does NOT kill the project — it says you cannot do it from inside.",
    "What survives: a single proof can still be written so a machine checks every step. That is what Lean does.",
], size=15)
textbox(s, 0.7, 4.0, 12, 0.5, "What is a proof, concretely?", size=16, bold=True, color=INK)
bullet(s, 0.7, 4.5, 12, [
    "Start from axioms. Apply inference rules one at a time.",
    "The most basic rule: modus ponens — if you have P→Q and P, you may conclude Q.",
    "Every step is mechanical. A machine can verify that no step was skipped.",
], size=14, height=2.5)
page_num(s)

# ============================================================
# SLIDE 5 — Curry-Howard part 1: Why P→Q IS a function
# ============================================================
s = add_slide()
notes(s, """【1.5 min｜Curry-Howard (1)】
主旨：先讲"什么对应什么"，再讲规则。命题 = 类型，证明 = 项，所以 P→Q 是函数类型，而 modus ponens 就是函数应用。

要点：
- 三步按顺序念，别跳：① P 是命题，在 Lean 里命题就是一个类型（Prop 是类型宇宙最底层）；② P 的证明是这个类型的一个项（term）；③ 所以 P→Q 是函数类型，它的"证明"就是那个类型的项——一个函数：输入 P 的证明，输出 Q 的证明。
- 第 ③ 步念完再上代码：theorem modus_ponens (P Q : Prop) : (P → Q) → P → Q。
- intro f p 相当于"设 f 是 P→Q，设 p 是 P"；exact f p 就是把 f 作用到 p 上。
- 有人问"Prop 到底是什么"：它是类型宇宙最底层，第 25 页宇宙阶梯会正式讲；现在只需要"命题就是类型"这个方向。

坑：
- 别一上来就说"P→Q 是函数"——听众还不知道 P 是个类型、证明是个项，这句话没有落脚点，只会变成背句子。顺序错了这页就废了。
- "term / 项"是全 deck 第一次出现，正式定义在第 15 页（A type classifies a term）；这里先亮出来，后面再正式讲。
- 这页接受度最高，慢一点讲。""")
title_bar(s, "Curry-Howard (1): propositions are types, proofs are terms", color=D_COLOR)
# 先建立"什么对应什么"，再讲规则：命题 = 类型，证明 = 项。
rich(s, 0.7, 1.22, 12, 1.15, [
    [{"t": "1.  A proposition P", "c": BODY, "b": True},
     {"t": "   is   ", "c": MUTED},
     {"t": "a type", "c": D_COLOR, "b": True},
     {"t": "   (Prop is the bottom level of Lean's universe)", "c": MUTED}],
    [{"t": "2.  A proof of P", "c": BODY, "b": True},
     {"t": "   is   ", "c": MUTED},
     {"t": "a term", "c": D_COLOR, "b": True},
     {"t": "   of that type", "c": MUTED}],
    [{"t": "3.  So ", "c": BODY, "b": True},
     {"t": "P → Q", "f": MONO, "c": D_COLOR, "b": True},
     {"t": "   is   ", "c": MUTED},
     {"t": "the function type", "c": D_COLOR, "b": True},
     {"t": ", and its proof is a ", "c": BODY},
     {"t": "function", "c": D_COLOR, "b": True},
     {"t": ": takes a proof of P, returns a proof of Q", "c": BODY}],
], size=15, space_after=5)
code_block(s, 0.7, 2.55, 11.9, 1.75,
'''-- Logic: "P implies Q" means you can build Q from P.
-- Program: a function P → Q does exactly that.

theorem modus_ponens (P Q : Prop) : (P → Q) → P → Q := by
  intro f p  -- assume f : P → Q, p : P
  exact f p  -- apply the method to the proof''', size=13)
textbox(s, 0.7, 4.55, 12, 1.5,
        "Modus ponens (logic): from P→Q and P, conclude Q.\n"
        "Function application (program): from f : P→Q and p : P, get f p : Q.\n"
        "Same rule. Same shape. Lean sees them as ONE thing.",
        size=14, color=BODY)
page_num(s)

# ============================================================
# SLIDE 6 — Curry-Howard part 2: every connective is a type
# ============================================================
s = add_slide()
notes(s, """【1 min｜Curry-Howard (2)】
主旨：逻辑 / 类型 / 范畴，同一张表的三种叫法。

要点：
- 顺着表念：P∧Q ↔ P×Q ↔ product；P∨Q ↔ P⊕Q；P→Q ↔ exponential；¬P 就是 P→False。
- 这是第 5 页那条对应的完整版：一行一个联结词，左边逻辑记号，中间 Lean 真实写法，右边范畴语言。
- 重点停在 P↔Q 这一行：Lean 里是 Iff P Q，它是一个 structure，装两个函数（mp 和 mpr），不是一个等式。
- 最后一行的补充说明要念出来：Iff 是装着两个函数的 structure，Eq x y 是等式类型，两者不同。
- 箭头约定（有人问就照表念）：左列 Logic 是逻辑书的记号（蕴含一个箭头 →）；中间 Type theory 列写的是 Lean 的真实写法，Lean 只有一种箭头 →——在 Lean 里"函数类型"和"蕴含"本来就是同一个东西（Curry–Howard）。别的类型论文献里会看到双箭头 ⇒（U+21D2），那是用来把 A→B 的两种读法分开的；Lean 里没有 ⇒ 这个记号，照抄直接 parse error（已实测）。
- ⊤ / ⊥ 这两格是逻辑记号（真值 / 假值），别当成 Lean 语法：Lean 写的是 True / False。纯 core 的 Lean 4.35 连 ⊤ ⊥ 这两个 token 都没有；Mathlib 里才有，而且是 rfl 可证的别名（⊤ = True、⊥ = False）。

坑：懂范畴论的人很可能来挑"P↔Q 的 hom-set"这个说法。别硬顶：坦白说这一列只是 rough dictionary，而且精确讲是 Hom(P,Q) × Hom(Q,P)。同时别把这个类比升级成"iso-ish"——那是错的。""")
title_bar(s, "Curry-Howard (2): logic / type / category — one table", color=D_COLOR)
# 4-column header
textbox(s, 0.7, 1.25, 2.8, 0.35, "Logic", size=13, bold=True, color=D_COLOR)
textbox(s, 3.6, 1.25, 2.8, 0.35, "Type theory", size=13, bold=True, color=C_COLOR)
textbox(s, 6.5, 1.25, 2.8, 0.35, "Category theory", size=13, bold=True, color=A_COLOR)
textbox(s, 9.4, 1.25, 3.2, 0.35, "Why", size=13, bold=True, color=BODY)
rows = [
    ("P ∧ Q",       "P × Q",      "product",        "need BOTH proofs"),
    ("P ∨ Q",       "P ⊕ Q",      "coproduct",      "need EITHER proof"),
    ("P → Q",       "P → Q",      "exponential",    "function: P→Q"),
    ("¬P",          "P → False",  "function to empty","P implies False"),
    ("P ↔ Q",       "Iff P Q",     "hom-set",        "both directions"),
    ("∀ x, P(x)",   "Π x, P x",   "dependent prod", "function: x→proof"),
    ("∃ x, P(x)",   "Σ x, P x",   "dependent sum",  "pair: x + proof"),
    ("x = y",       "Eq x y",     "identity type",  "proof of equality"),
    ("⊤",           "Unit/True",  "terminal obj",   "one trivial proof"),
    ("⊥",           "Empty/False","initial obj",    "no proof at all"),
]
y = 1.65
# Consolas 缺 ⊤ / ⊥，回退成细衬线后 11pt 下几乎不可见 —— 这两格单独换字体。
SYM_CELLS = {"\u22a4", "\u22a5"}
for logic, type_, cat, why in rows:
    code_block(s, 0.7, y, 2.8, 0.35, logic, size=11,
               font=SYM if logic in SYM_CELLS else MONO)
    code_block(s, 3.6, y, 2.8, 0.35, type_, size=11)
    textbox(s, 6.5, y+0.02, 2.8, 0.35, cat, size=11, color=A_COLOR)
    textbox(s, 9.4, y+0.02, 3.2, 0.35, why, size=11, color=BODY)
    y += 0.46
textbox(s, 0.7, 6.28, 11.4, 0.42,
        "Three names for one thing. ¬P = P→False. P↔Q = Iff (a structure holding two functions). x=y = Eq x y.",
        size=11, bold=True, color=D_COLOR)
# ⇒ (U+21D2) 不在 Calibri 里（会回退成细衬线），单独用 SYM 字体渲染。
rich(s, 0.7, 6.74, 11.4, 0.55, [[
    {"t": "Notation: logic books write implication with one arrow (→). Type-theory texts also use a double arrow (", "c": MUTED},
    {"t": "⇒", "f": SYM, "c": MUTED},
    {"t": ") to tell the two readings of A→B apart. Lean has only → — the function type and the implication are the same thing.", "c": MUTED},
]], size=10)
page_num(s)

# ============================================================
# NEW SLIDE 6b — Why ∀ is a function and ∃ is a pair
# ============================================================
s = add_slide()
notes(s, """【2 min｜Curry-Howard (2b)】
主旨：∀ 是函数，∃ 是对。这是对数学家最有用的对应，值得多停。

要点：
- 左边：(n : Nat) → 0 + n = n。输入 n，输出一个证明。这就是 Π / 函数。
- 右边：refine ⟨2, ?_⟩。我交出见证 2 和它的证明 —— 是"一对东西"。这就是 Σ / pair。
- ?_ 的意思是"给我留个洞"，下一行 rfl 把它填上。⟨ , ⟩ 是匿名构造子，两个字段分别是见证和证明。

坑：∃ 的匿名构造子最容易看成魔法。让他们数清楚：第一个字段是数 2，第二个字段是证明 4 = 2*2。""")
title_bar(s, "Curry-Howard (2b): why ∀ is a function, ∃ is a pair", color=D_COLOR)
# Left: FORALL
textbox(s, 0.7, 1.3, 5.8, 0.4, "∀ x, P(x)  — give me x, I return a proof", size=14, bold=True, color=C_COLOR)
code_block(s, 0.7, 1.8, 5.8, 3.0,
'''-- "for all n, 0+n = n" means:
-- give me any n, I give you a proof

example : (n : Nat) → 0 + n = n := by
  intro n
  induction n with
  | zero => rfl
  | succ k ih => rw [Nat.add_succ, ih]

-- ↑ this IS a function.
-- ↑ n is the input, the body returns the proof.''', size=11)
# Right: EXISTS
textbox(s, 6.9, 1.3, 5.8, 0.4, "∃ x, P(x)  — I hand you x AND a proof", size=14, bold=True, color=C_COLOR)
code_block(s, 6.9, 1.8, 5.8, 3.0,
'''-- "there exists k such that 4 = 2*k"
-- means: I give you k=2, AND a proof

example : ∃ k : Nat, 4 = 2 * k := by
  refine ⟨2, ?_⟩
  rfl

-- ↑ refine ⟨2, ?_⟩: give the pair, leave me a hole
-- ↑ ⟨2, rfl⟩ is a PAIR:
--   first field  = 2  (the witness)
--   second field = proof that 4=2*2''', size=11)
textbox(s, 0.7, 5.0, 12, 1.5,
        "P(x) varies with x: P(0) = \"0=0\" (has proof), P(1) = \"1=0\" (no proof).\n"
        "Π x, P(x)  = a function that gives a proof for EVERY x.  Σ x, P(x)  = one specific x + its proof.\n"
        "∀ = Π = function.  ∃ = Σ = pair.  Lean writes ∀ as (x : α) → P x, ∃ as ⟨witness, proof⟩.",
        size=12, bold=True, color=D_COLOR)
page_num(s)

# ============================================================
# SLIDE 7 — Curry-Howard part 3: the punchline
# ============================================================
s = add_slide()
notes(s, """【1 min｜Curry-Howard (3)】
主旨：证明 = 程序，检查 = 编译。

要点：
- 写一个定理 = 写一个函数，它的类型恰好是那条定理。
- 检查一个证明 = 类型检查器在验证那个函数。
- 化简一个证明 = 运行那个程序。rfl 就是在问"两边能不能算成同一个东西"。

坑：rfl 只对"定义相等"有效，不是所有等式都能 rfl。别让他们以为 rfl 是万能的。""")
title_bar(s, "Curry-Howard (3): proof = program, checked = compiled", color=D_COLOR)
bullet(s, 0.7, 1.4, 12, [
    "Proving a theorem  =  writing a function whose type is the theorem statement.",
    "Checking a proof   =  the type checker verifying that function.",
    "Simplifying a proof =  running / evaluating the program.",
], size=16)
code_block(s, 0.7, 3.5, 11.9, 2.8,
'''example : 2 + 2 = 4 := by
  rfl
--   ↑ this is a proof.
--   It is also a term of type (2 + 2 = 4).
--   rfl checks that 2+2 and 4 reduce to the same thing.
--   That is β/iota reduction doing its job.''', size=13)
textbox(s, 0.7, 6.5, 12, 0.5,
        "Lean's kernel does one thing: check types. It has no idea it is also checking proofs.",
        size=13, bold=True, color=D_COLOR)
page_num(s)

# ============================================================
# NEW SLIDE — What IS a type? Four rules, not a set
# ============================================================
s = add_slide()
notes(s, """【1 min｜什么是类型】
主旨：类型不是集合，是四条规则。这是全 deck 最反直觉、也最该慢慢讲的一页。

要点：
- 四条规则逐条念：Formation（什么时候是一个类型）、Introduction（怎么造）、Elimination（怎么用）、Computation（引入了怎么用会算出什么）。
- 强调"这是定义，不是类比"：不存在"所有函数的集合"这种东西。
- 拿函数类型 A → B 走一遍四规则。
- 落点句（照读页面底部那行）：每个类型都被四条规则钉住，但四格里的内容不一样 —— inductive 用构造子和递归子（下一页展开），Empty 零构造子，所以根本没有引入规则。

坑：数学背景强的人会自动把"类型 = 集合"套进来。这一页整个任务就是拆掉这个直觉，讲慢一点，别赶。""")
title_bar(s, "What IS a type? Four rules — not a set", color=C_COLOR)
textbox(s, 0.7, 1.3, 12, 0.5,
        "A type is NOT a collection of elements. It is COMPLETELY DEFINED by four rules. Example: the function type A → B.",
        size=14, color=BODY)
rules = [
    ("1. Formation",  "If A : Type and B : Type, then A → B : Type.",
     "When is this a valid type?"),
    ("2. Introduction", "If x : A gives t : B, then (fun x => t) : A → B.",
     "How do you BUILD a term? (lambda / constructor)"),
    ("3. Elimination", "If f : A → B and a : A, then f a : B.",
     "How do you USE a term? (application / match)"),
    ("4. Computation", "(fun x => t) a  reduces to  t[a/x].",
     "What happens when intro meets elim? (beta reduction)"),
]
y = 2.0
for name, rule, why in rules:
    textbox(s, 0.7, y, 2.5, 0.4, name, size=14, bold=True, color=C_COLOR)
    code_block(s, 3.3, y, 6.5, 0.4, rule, size=12)
    textbox(s, 10.0, y+0.02, 3.0, 0.4, why, size=11, color=BODY)
    y += 0.75
textbox(s, 0.7, 5.3, 12, 1.0,
        "No analogy. No 'set of functions'. Every type is defined by four rules — "
        "formation, introduction, elimination, computation. Same four slots every time, "
        "different content: inductives use constructors and recursors (next slide); "
        "Empty has zero constructors, so no introduction rule at all.",
        size=13, bold=True, color=C_COLOR)
page_num(s)

# ============================================================
# NEW SLIDE — The four rules, in Lean
# ============================================================
s = add_slide()
notes(s, """【1 min｜四规则在 Lean】
主旨：inductive 一个关键字，就把四条规则全部钉住。

要点：
- 对应表：Formation = 你写 inductive；Introduction = 构造子；Elimination = match / recursor；Computation = 内核自动归约，rfl 用来检查它。
- 落点句（照读）：一条声明钉住四条规则 —— 关键字给 FORMATION，你写 INTRODUCTION，Lean 生成 ELIMINATION 和 COMPUTATION。
- 所以 inductive 是 Lean 里最有用的关键字。

坑：这里有个历史坑：上一版这句话写的是"Lean 生成另外三条"，和上面"两条"自相矛盾。现在是"两条（消分子 + 计算规则）"。若被问 formation 从哪来——来自关键字本身，不是生成的。""")
title_bar(s, "The four rules, in Lean", color=C_COLOR)
rows = [
    ("Formation",   "you write  inductive / def / structure",  "you declare: this is a type now"),
    ("Introduction","constructors:  Nat.zero, Nat.succ, Or.inl", "these are the ONLY ways to make a term"),
    ("Elimination", "match / recursor:  Nat.rec, Or.casesOn",    "this is the ONLY way to USE a term"),
    ("Computation", "kernel reduces automatically;  rfl  checks it", "intro meets elim → simplification"),
]
y = 1.5
for name, lean, meaning in rows:
    textbox(s, 0.7, y, 2.2, 0.4, name, size=14, bold=True, color=C_COLOR)
    code_block(s, 3.0, y, 6.0, 0.4, lean, size=11)
    textbox(s, 9.2, y+0.02, 3.5, 0.4, meaning, size=11, color=BODY)
    y += 0.7
textbox(s, 0.7, 4.5, 12, 2.5,
        "When you write  inductive Nat where  | zero  | succ\n"
        "you give the INTRODUCTION rules. Lean auto-generates the ELIMINATOR (Nat.rec) and COMPUTATION rules.\n"
        "This is why inductive is the single most powerful keyword in Lean:\n"
        "one declaration pins down all four rules — the keyword gives FORMATION,\n"
        "you write INTRODUCTION, Lean generates ELIMINATION and COMPUTATION.\n\n"
        "Precision: introduction & computation are per-constructor; formation & elimination are per-type (one recursor).\n"
        "The rules for Type u itself — variables, conversion, universes — are the same four rules one level up. You never declare those.",
        size=11, color=BODY)
page_num(s)

# ============================================================
# NEW SLIDE — The glue: syntax symbols (before the four homes)
# ============================================================
s = add_slide()
notes(s, """【1 min｜语法符号】
主旨：这些符号不属于任何一个"家"，但你天天见。

要点：
- 四种括号：() 分组与应用、{} 隐式参数、[] instance 参数、⟨a,b⟩ 匿名构造子（就是上一页那个 pair）。
- 其余：: 是 has type、:= 是 defined as、→ 箭头、_ 占位符、| 分支、· 聚焦当前目标、# 命令。
- 唯一需要多说一句的是 ⟨ , ⟩ —— 它和上一页的 ∃ 是同一件事。

坑：[] 是 instance 参数、Lean 会自动搜索，最容易吓到人。一句话带过就行。""")
title_bar(s, "The glue: syntax symbols — not a home, but you see them everywhere", color=INK)
textbox(s, 0.7, 1.25, 12, 0.4,
        "Before the four homes: these symbols themselves are not terms — but expressions built from them DO have types.",
        size=13, color=BODY)
# Four kinds of brackets
textbox(s, 0.7, 1.75, 3, 0.35, "Four bracket types:", size=13, bold=True, color=INK)
brackets = [
    ("( e )",     "grouping, function application:  f (x+1)"),
    ("{x : α}",   "implicit arg — caller omits, Lean infers"),
    ("[inst : C]","instance arg — Lean searches automatically"),
    ("⟨a, b⟩",    "anonymous constructor — build a pair/struct value"),
]
y = 2.15
for sym, meaning in brackets:
    code_block(s, 0.7, y, 2.2, 0.35, sym, size=12)
    textbox(s, 3.1, y+0.02, 9.5, 0.35, meaning, size=12, color=BODY)
    y += 0.42
# Other glue
textbox(s, 0.7, 4.0, 3, 0.35, "Other glue:", size=13, bold=True, color=INK)
other = [
    (":",     "has type:  n : Nat   (left of : is a term, right is its type)"),
    (":=",    "defined as:  def x := 5   (the body equals the name)"),
    ("→",     "arrow:  Nat → Nat   (also written as function type)"),
    ("_",     "placeholder: Lean figures it out for you"),
    ("|",     "case separator: inductive constructors, match arms"),
    ("·",     "focus block: in by-mode, start proving the current goal"),
    ("#",     "command: #check, #eval — ask Lean a question"),
]
y = 4.4
for sym, meaning in other:
    code_block(s, 0.7, y, 1.5, 0.35, sym, size=12)
    textbox(s, 2.4, y+0.02, 10, 0.35, meaning, size=12, color=BODY)
    y += 0.38
page_num(s)

# ============================================================
# SLIDE — The four homes map
# ============================================================
s = add_slide()
notes(s, """【1 min｜四个家】
主旨：每个词都住在一个房子里。这大概是今天最有用的一张图。

要点：
- A 环境（问 Lean 的房间）：#check、#eval、import、open、namespace。
- B 声明（往房间里加东西）：def、inductive、structure、theorem。
- C 项 / 类型（表达式本身）：2、fun n => n+1、Color.red、match。
- D 证明策略（帮你造出一个 C 的工具）：by intro n; rw [h]; rfl。
- 给他们的实用建议：以后卡住，先问"我这句话在哪个房子里"。

坑：不要在这一页展开范畴论版本（slide 6 已经给过表了）。""")
title_bar(s, "Every word lives in one of four homes")
homes = [
    ("A", A_COLOR, "Environment", "You ask Lean about the room.\n#check, #eval, import, open, namespace."),
    ("B", B_COLOR, "Declaration", "You add something new to the room.\ndef, inductive, structure, theorem."),
    ("C", C_COLOR, "Term / Type", "An expression itself.\n2, fun n => n+1, Color.red, match ..."),
    ("D", D_COLOR, "Proof strategy", "A tactic that helps build a C term.\nby intro n; rw [h]; rfl."),
]
positions = [(0.7, 1.5), (6.9, 1.5), (0.7, 4.2), (6.9, 4.2)]
for (letter, col, name, desc), (x, y) in zip(homes, positions):
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                             Inches(x), Inches(y), Inches(5.7), Inches(2.4))
    box.fill.solid(); box.fill.fore_color.rgb = WHITE
    box.line.color.rgb = col; box.line.width = Pt(2); box.shadow.inherit=False
    c = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x+0.2), Inches(y+0.2), Inches(0.6), Inches(0.6))
    c.fill.solid(); c.fill.fore_color.rgb = col; c.line.fill.background(); c.shadow.inherit=False
    tf=c.text_frame; p=tf.paragraphs[0]; p.alignment=PP_ALIGN.CENTER
    r=p.add_run(); r.text=letter; r.font.size=Pt(22); r.font.bold=True; r.font.color.rgb=WHITE
    textbox(s, x+1.0, y+0.25, 4.5, 0.5, name, size=20, bold=True, color=col)
    textbox(s, x+0.25, y+1.0, 5.2, 1.2, desc, size=13, color=BODY)
page_num(s)

# ============================================================
# SLIDE 9 — How to read this deck
# ============================================================
s = add_slide()
notes(s, """【0.5 min｜怎么读这个 deck】
主旨：先看屏幕，名字以后再记。

要点：
- 三步：看（#check）→ 建（def / inductive）→ 证（tactic 造证明）。
- 提醒 PDE 背景的人：第 33 页（最后一页）是给你们的。
- 强调不用记语法，今天要的是地图不是清单。

坑：slide 2 上那套教育学术语（meaning triangle / desirable difficulty）对数学家很突兀，别在这儿展开，一句话带过或者干脆不提。""")
title_bar(s, "How to read this deck: look at the screen first, get names later")
steps = [
    ("1", "See", "Open Lean. It already knows numbers, booleans, strings. #check them."),
    ("2", "Build", "Give things names with def. Build new types with inductive."),
    ("3", "Prove", "A proof is just a term of a proposition type. Tactics help build it."),
]
y = 1.5
for num, h, d in steps:
    c = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8), Inches(y), Inches(0.5), Inches(0.5))
    c.fill.solid(); c.fill.fore_color.rgb = INK; c.line.fill.background(); c.shadow.inherit=False
    tf=c.text_frame; p=tf.paragraphs[0]; p.alignment=PP_ALIGN.CENTER
    r=p.add_run(); r.text=num; r.font.size=Pt(16); r.font.bold=True; r.font.color.rgb=WHITE
    textbox(s, 1.5, y+0.02, 2, 0.45, h, size=18, bold=True, color=INK)
    textbox(s, 3.3, y+0.05, 9, 0.5, d, size=14, color=BODY)
    y += 1.25
textbox(s, 0.8, 5.05, 11.7, 0.7,
        "Coming from PDE? Slide 33 — the last one — tells you where Mathlib actually stands for analysis.",
        size=14, bold=True, color=C_COLOR)
textbox(s, 0.8, 5.95, 11.7, 0.7,
        "You do not need any computer science to follow the arc. Everything today happens on one screen, "
        "and every line you see compiles.",
        size=13, color=MUTED)
page_num(s)

# ============================================================
# SLIDE 10 — Open Lean, room is already full
# ============================================================
s = add_slide()
notes(s, """【1.5 min｜打开 Lean】
主旨：房间已经满了 —— 这些东西 Lean 自带，你一个都没声明过。这是全场最有"魔法感"的一页，多留时间。

要点：
- 现场敲 #check 2 / true / "hello" / [1,2,3] / (2,true)，让他们盯着右边的 infoview。
- 重点观察：2 不是"一个整数"，它是一个类型为 Nat 的项。
- Type 1 这种先别管，只记住一句话：类型自己也有类型。

坑：提前让他们把 VS Code 右边的 infoview 面板拉开，否则这页毫无效果。""")
title_bar(s, "Open Lean. The room is already full.", color=INK)
textbox(s, 0.7, 1.25, 12, 0.5,
        "Lean already knows all of these. You did not declare any of them. Type them and watch the right panel.",
        size=14, color=BODY)
code_block(s, 0.7, 1.9, 7.5, 3.8,
'''#check 2            -- Nat
#check true         -- Bool
#check "hello"      -- String
#check [1, 2, 3]    -- List Nat
#check (2, true)    -- Nat × Bool
#check Nat          -- Type
#check Type         -- Type 1''', size=15)
bullet(s, 8.6, 1.9, 4.2, [
    "#check asks: what type is this?",
    "The panel on the right (infoview) answers.",
    "2 is not 'an integer'. It is a term of type Nat.",
    "Nat itself has a type: Type.",
    "Type itself has a type: Type 1.",
], size=13)
textbox(s, 8.6, 5.5, 4.2, 1.2,
        "Do not memorize Type 1 yet.\nJust notice: types themselves have types.",
        size=13, bold=True, color=A_COLOR)
page_num(s)

# ============================================================
# SLIDE 11 — A type classifies a term
# ============================================================
s = add_slide()
notes(s, """【1 min｜类型给项分类】
主旨：读 ":" 时，左边是项，右边是它的类型。

要点：
- (2 : Nat)、(true : Bool)、(fun n => n+1 : Nat → Nat)。
- Prop 装的是命题，Prop 的项就是证明。类型分两类：装数据的（Nat/Bool）和装命题的（Prop）。
- 承上启下的那句要念：定理陈述是一个类型，证明是那个类型的项。

坑：(2 + 2 = 4) 是 Prop 不是一个数据项，第一次看到会困惑 —— 主动指出来。""")
title_bar(s, "A type classifies a term", color=INK)
textbox(s, 0.7, 1.3, 12, 0.5,
        "Read \":\" as has type. Left of : is a term. Right of : is what kind of term it is.",
        size=14, color=BODY)
code_block(s, 0.7, 1.9, 7.5, 2.8,
'''#check (2 : Nat)
#check (true : Bool)
#check (fun n => n + 1 : Nat → Nat)
#check (2 + 2 = 4)   -- this is a Prop''', size=15)
bullet(s, 8.6, 1.9, 4.2, [
    "Nat, Bool carry data you can compute with.",
    "Prop carries propositions.",
    "A term of type P ∧ Q is a proof of P ∧ Q.",
    "Most proofs cannot be taken apart to compute data.",
], size=13)
textbox(s, 0.7, 5.0, 12, 1.5,
        "Why this comes first: a theorem statement IS a type. A proof IS a term of that type. "
        "Everything later hangs off this one sentence.",
        size=14, bold=True, color=C_COLOR)
page_num(s)

# ============================================================
# SLIDE 12 — A · Ask Lean four questions
# ============================================================
s = add_slide()
notes(s, """【1 min｜A 家：四个问题】
主旨：四个只读命令，用来向房间提问。

要点：
- #check 问类型、#eval 跑一下并打印值、#reduce 化到底、#print 看定义怎么写的。
- 它们只读，不在房间里创造任何东西。
- 对 PDE 的人可以这样翻译：#eval ≈ 跑一遍，#reduce ≈ 化简到底。

坑：不要在他们面前 #print 一个大定义，会刷屏而且打断节奏。""")
title_bar(s, "A · Environment · Ask Lean four questions", color=A_COLOR)
code_block(s, 0.7, 1.4, 6.5, 4.5,
'''#check (2 + 2)       -- Nat
#eval  (2 + 2)       -- 4
#reduce (1 + 2)      -- 3
-- #print Nat.add    -- see definition''', size=15)
# right: explain each
explain = [
    ("#check", "What type is this expression?"),
    ("#eval", "Run it and print the value."),
    ("#reduce", "Fully simplify, show the result."),
    ("#print", "Show how something is defined."),
]
y = 1.5
for cmd, desc in explain:
    textbox(s, 7.6, y, 2.0, 0.4, cmd, size=15, bold=True, color=A_COLOR, font=MONO)
    textbox(s, 9.6, y, 3.2, 0.5, desc, size=13, color=BODY)
    y += 0.9
textbox(s, 0.7, 6.1, 12, 0.8,
        "These four commands only READ the environment. They never create anything.",
        size=13, color=MUTED)
page_num(s)

# ============================================================
# SLIDE 8 — A · Organize names
# ============================================================
s = add_slide()
notes(s, """【1 min｜A 家：组织名字】
主旨：Lean 的库把一切都放在文件夹里，所以你必须学会指路。

要点：
- import（把别的文件里的名字拉进来）、namespace（给名字一个地址，用 end 关闭）、open（临时跳过地址）、section / variable（临时假设，结束即失效）。
- 强调 import 那一行是可选的：没装 Mathlib，把这行删掉，本页其他所有东西照样工作。
- namespace Lesson / def two / end Lesson / #check Lesson.two —— 这四行是核心。

坑：这是上一轮补的坑：组里有人没装 Mathlib，别让他们卡在这一行。现场先确认一下谁装了。""")
title_bar(s, "A · Environment · Organize names", color=A_COLOR)
code_block(s, 0.7, 1.4, 6.5, 3.6,
'''-- OPTIONAL: this one line needs Mathlib installed.
-- Delete it and everything else below still works.
import Mathlib.Tactic   -- bring outside names in

namespace Lesson         -- give names an address
def two : Nat := 2
end Lesson

#check Lesson.two

-- scoped open: only affects the next line
open Lesson in
#check two''', size=12)
bullet(s, 7.6, 1.5, 5.0, [
    "import: make names from other files available.",
    "namespace: a folder for names, closed by end.",
    "open: skip the folder prefix.",
    "section / variable: temporary assumptions, vanish at end.",
], size=14)
textbox(s, 0.7, 5.25, 12, 1.3,
        "You rarely write these by hand in a day. You need them because Lean's standard library puts everything in folders.\n"
        "The import line is the only thing on this slide that needs Mathlib. Plain Lean (Init) is enough for everything else in this deck.",
        size=13, color=MUTED)
page_num(s)

# ============================================================
# SLIDE 9 — B · Name a term (def/theorem/example)
# ============================================================
s = add_slide()
notes(s, """【1.5 min｜B 家：命名】
主旨：给项和证明安名字。四个词的区别就是它们活多久。

要点：
- def = 给一个值起名字；example = 检查一下但不保存；theorem / lemma = 存下来可复用；axiom = 只声明名字和类型、不给定义。
- 现场敲 def two / def double / #eval double two，顺带指出 theorem two_plus_two 和 example 写的是同一个东西。
- axiom 用红框说清楚：它是"作弊"，今天不碰，也不需要。

坑：这页第 1 行就自己声明了全局的 two，#eval double two 在本页就能跑 —— 不依赖前一页；前一页那个 two 装在 namespace Lesson 里，是另一个名字（Lesson.two）。这页自足，单独讲也成立。""")
title_bar(s, "B · Declarations · Name a term, step by step", color=B_COLOR)
code_block(s, 0.7, 1.35, 7.8, 5.2,
'''-- Step 1: give a value a name
def two : Nat := 2

-- Step 2: a function (input -> output)
def double (n : Nat) : Nat := n + n

-- Step 3: use them
#eval double two     -- 4

-- Step 4: a proposition is a type. rfl proves it.
example : 2 + 2 = 4 := rfl

-- Step 5: name the theorem (same as example, but reusable)
theorem two_plus_two : 2 + 2 = 4 := rfl''', size=13)
bullet(s, 8.8, 1.5, 3.8, [
    "def: name a value.",
    "example: check, do not store.",
    "theorem / lemma: name a proof.",
    "axiom: not shown on purpose.",
], size=13)
textbox(s, 8.8, 3.8, 3.8, 2.5,
        "axiom means: declare a name and a type,\n"
        "but give no definition.\n"
        "Skip it for now. It is how you\n"
        "\"cheat\" — you do not need to\n"
        "cheat yet.",
        size=12, color=ACCENT)
page_num(s)

# ============================================================
# SLIDE 10 — Built-in vs you-made (CRITICAL)
# ============================================================
s = add_slide()
notes(s, """【1.5 min｜两个桶】
主旨：内核给你三个 type-former（Sort / Pi / Quot）；第 4 种机制 inductive 是声明，不是 type-former。你造的一切都是 inductive。

要点：
- 左桶：Sort（Prop/Type/Type 1…）、→ 与 ∀（Pi 类型）、Quot（商）。硬编码，你永远声明不了它们。
- 一定要念页面上的对冲句：这是机制图，不是封闭清单 —— 归约和递归也住在这里。
- 右桶：inductive 是真正加类型的唯一机制。而且 Nat、Bool、List 本身就是 inductive，只是住在 Init 里、开机自动加载。
- 落点（照读页面下方的面板）：这不是两种语言，只有一种加类型的办法，就是 inductive。structure、class、abbrev 全是 inductive 换皮，见 22–24 页。Mathlib 里的 Measure、Lp、分布、Sobolev 空间全是这么造出来的 —— 学 Lean 不是学一门新数学，是学一个能撑起 8,624 个文件的关键字。

坑：不要说"内核只有这三个原语"。屏上写的是三个 type-former（值级的类型构造子）；inductive 是第 4 种内核机制，但它是声明（declaration）、不是 type-former，所以它归右栏。有对冲句在页面上，照读就行。""")
title_bar(s, "Two buckets: what Lean gives you, what you build", color=B_COLOR)
# left bucket
box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(1.4), Inches(5.8), Inches(3.25))
box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0xEF,0xF6,0xFF)
box.line.color.rgb = A_COLOR; box.line.width=Pt(1.5); box.shadow.inherit=False
textbox(s, 1.0, 1.55, 5.2, 0.5, "Kernel: three type-formers", size=18, bold=True, color=A_COLOR)
rich(s, 1.0, 2.15, 5.2, 2.4, [
    [{"t": "The kernel has exactly three type-formers:", "c": BODY}],
    [{"t": ""}],
    [{"t": "  Sort   (Prop, Type, Type 1 ...)", "f": MONO, "c": INK}],
    [{"t": "  → / ∀  (Pi type)", "f": MONO, "c": INK}],
    [{"t": "  Quot   (quotient)", "f": MONO, "c": INK}],
    [{"t": ""}],
    [{"t": "These are hard-coded. You never declare them.", "c": BODY}],
    [{"t": "inductive", "f": MONO, "c": B_COLOR, "b": True},
     {"t": " is not one of these three (see right).", "c": BODY}],
    [{"t": "This is a mechanism map, not a closed inventory —", "c": BODY}],
    [{"t": "reduction and recursion also live here.", "c": BODY}],
], size=12, space_after=1)
# right bucket
box2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.4), Inches(5.8), Inches(3.25))
box2.fill.solid(); box2.fill.fore_color.rgb = RGBColor(0xEC,0xFD,0xF5)
box2.line.color.rgb = B_COLOR; box2.line.width=Pt(1.5); box2.shadow.inherit=False
textbox(s, 7.2, 1.55, 5.2, 0.5, "You build with inductive", size=18, bold=True, color=B_COLOR)
rich(s, 7.2, 2.15, 5.2, 2.4, [
    [{"t": "inductive", "f": MONO, "c": B_COLOR, "b": True}, {"t": "  →  the main mechanism", "c": BODY}],
    [{"t": "  Your Color, MyNat, Point ...", "f": MONO, "c": INK}],
    [{"t": "  AND Nat, Bool, List!", "f": MONO, "c": INK}],
    [{"t": "  (they live in the Init library, auto-loaded at startup, but they", "c": BODY}],
    [{"t": "   are written exactly like your Color; String is a structure —", "c": BODY}],
    [{"t": "   see below)", "c": BODY}],
    [{"t": ""}],
    [{"t": "structure", "f": MONO, "c": B_COLOR, "b": True}, {"t": "  →  inductive, one constructor", "c": BODY}],
    [{"t": "class", "f": MONO, "c": B_COLOR, "b": True}, {"t": "      →  structure + searchable", "c": BODY}],
    [{"t": "abbrev", "f": MONO, "c": B_COLOR, "b": True}, {"t": "     →  just a name, not a type", "c": BODY}],
], size=12, space_after=1)
panel = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(4.9), Inches(11.9), Inches(1.85))
panel.fill.solid(); panel.fill.fore_color.rgb = RGBColor(0xFA,0xFA,0xFA)
panel.line.color.rgb = LINE; panel.line.width=Pt(1); panel.shadow.inherit=False
textbox(s, 1.0, 5.05, 11.3, 0.4, "Why this matters for this room", size=16, bold=True, color=B_COLOR)
rich(s, 1.0, 5.52, 11.3, 1.1, [
    [{"t": "These are not two languages. There is exactly ONE way to add a type, and it is ", "c": BODY},
     {"t": "inductive", "f": MONO, "c": B_COLOR, "b": True},
     {"t": " — structure, class and abbrev are all inductive in disguise (slides 22 to 24).", "c": BODY}],
    [{"t": "Every type in Mathlib — Measure, Lp, Distribution, the Sobolev space — was built that way. "
           "Learning Lean is not learning a new branch of mathematics; it is learning one keyword that happens to scale to 8,624 files.", "c": BODY}],
], size=13, space_after=4)
page_num(s)

# ============================================================
# SLIDE 11 — inductive: finite choices
# ============================================================
s = add_slide()
notes(s, """【1 min｜inductive：有限选择】
主旨：枚举类型 = 一组不带数据的构造子。

要点：
- 现场写 inductive Color where | red | green | blue，然后 #check Color.red。
- match 必须覆盖全部三个构造子，漏一个 Lean 会直接报错 —— 这是编译器替人干活的第一例。
- #eval isWarm Color.red 收尾。

坑：他们八成会说"这不就是 C 语言的 enum"——是的，一模一样，直接承认，别绕。""")
title_bar(s, "B · inductive · finite choices (an enum)", color=B_COLOR)
code_block(s, 0.7, 1.35, 6.0, 2.3,
'''inductive Color where
  | red
  | green
  | blue''', size=15)
textbox(s, 0.7, 3.8, 6, 0.4, "Now ask what you made:", size=13, bold=True, color=BODY)
code_block(s, 0.7, 4.2, 6.0, 1.3,
'''#check Color.red   -- Color
#check Color       -- Type''', size=14)
# right: use it
textbox(s, 7.1, 1.35, 5.5, 0.4, "Use it — pattern match ALL cases:", size=13, bold=True, color=B_COLOR)
code_block(s, 7.1, 1.8, 5.5, 2.5,
'''def isWarm (c : Color) : Bool :=
  match c with
  | .red   => true
  | .green => false
  | .blue  => false''', size=13)
code_block(s, 7.1, 4.5, 5.5, 1.0,
'''#eval isWarm Color.red    -- true''', size=13)
textbox(s, 7.1, 5.7, 5.5, 1.0,
        "Note: the match covers all three.\nMiss one and Lean tells you.",
        size=12, color=ACCENT)
page_num(s)

# ============================================================
# SLIDE 12 — inductive: recursive
# ============================================================
s = add_slide()
notes(s, """【1 min｜inductive：递归】
主旨：自然数就是这么造出来的。

要点：
- MyNat.zero 和 MyNat.succ；MyNat.succ MyNat.zero 就是"一"。
- 关键句：Lean's Nat 就是这么定义的。你们刚刚重建了自然数。
- 这一页是"递归形状 = 以后归纳证明的形状"的伏笔。

坑：从这里开始他们会觉得"这东西跟我平时写的证明不像"。提前说一句：归纳证明就是跟构造子对齐。""")
title_bar(s, "B · inductive · a recursive type (this is how numbers work)", color=B_COLOR)
code_block(s, 0.7, 1.35, 6.0, 2.2,
'''inductive MyNat where
  | zero
  | succ (n : MyNat)''', size=15)
textbox(s, 0.7, 3.7, 6, 0.4, "Build values from the constructors:", size=13, bold=True)
code_block(s, 0.7, 4.1, 6.0, 2.0,
'''#check MyNat.zero           -- MyNat
#check MyNat.succ           -- MyNat → MyNat
#check MyNat.succ MyNat.zero -- MyNat ("one")

def one  := MyNat.succ MyNat.zero
def two' := MyNat.succ one''', size=13)
bullet(s, 7.1, 1.5, 5.5, [
    "zero : no input, gives one MyNat.",
    "succ : takes a MyNat, returns a bigger MyNat.",
    "Every MyNat is either zero, or succ of a smaller one.",
    "That recursion is exactly what induction proofs follow.",
], size=14)
textbox(s, 7.1, 4.2, 5.5, 1.5,
        "Lean's built-in Nat is defined almost exactly this way.\n"
        "You just rebuilt the natural numbers.",
        size=14, bold=True, color=B_COLOR)
page_num(s)

# ============================================================
# SLIDE 13 — structure
# ============================================================
s = add_slide()
notes(s, """【1 min｜structure】
主旨：只有一个构造子的 inductive，加上字段名，就是 structure。

要点：
- Point 的两种写法：{ x := 3, y := 4 } 和 Point.mk 3 4，是同一个值。
- 投影 .x / .y 免费给。
- 强调"它不是新机制"，structure 就是写起来顺手的 inductive。

坑：最后那行"In Mathlib, Measure is a structure"只是点一下，不要展开——完整的盘点在第 33 页。""")
title_bar(s, "B · structure · one constructor, named fields", color=B_COLOR)
code_block(s, 0.7, 1.35, 6.0, 1.8,
'''structure Point where
  x : Nat
  y : Nat''', size=15)
textbox(s, 0.7, 3.3, 6, 0.4, "This is shorthand for:", size=12, color=MUTED)
code_block(s, 0.7, 3.7, 6.0, 1.3,
'''-- inductive Point where
--   | mk (x : Nat) (y : Nat) : Point
--
-- one constructor; its arguments ARE the fields''', size=13)
textbox(s, 0.7, 5.15, 6, 0.4, "Two ways to build the same value:", size=12, color=MUTED)
code_block(s, 0.7, 5.55, 6.0, 1.2,
'''def p1 : Point := { x := 3, y := 4 }
def p2 : Point := Point.mk 3 4
-- p1 and p2 are the SAME value.''', size=13)
textbox(s, 7.1, 1.35, 5.5, 0.4, "Build and read:", size=13, bold=True, color=B_COLOR)
code_block(s, 7.1, 1.8, 5.5, 1.5,
'''def p : Point := { x := 3, y := 4 }

#eval p.x    -- 3
#eval p.y    -- 4''', size=14)
textbox(s, 7.1, 3.5, 5.5, 2.3,
        "structure gives you named fields\nand .x / .y projections for free.\n\n"
        "It is not a new mechanism.\nIt is inductive with exactly one\nconstructor + a name for each field.\n\n"
        "In Mathlib, Measure is a structure.",
        size=13, color=BODY)
page_num(s)

# ============================================================
# SLIDE 14 — class / instance
# ============================================================
s = add_slide()
notes(s, """【1 min｜class / instance】
主旨：class = 一个允许 Lean 搜索的 structure。

要点：
- class 声明接口，instance 提供一个实现，Lean 看到 + 会自动去找 Add Nat。
- 一句带过：你几乎从不手写 class。
- 收尾：连 class 和 instance 都能还原成 inductive —— 全场只有一种机制。

坑：如果有人问 typeclass 里的 class 和范畴论的 class 是不是一回事——不是，别展开。""")
title_bar(s, "B · class / instance · a structure Lean can search for", color=B_COLOR)
code_block(s, 0.7, 1.4, 7.5, 2.5,
'''-- named MyAdd because Add already exists in the library
class MyAdd (α : Type) where
  myAdd : α → α → α

instance : MyAdd Nat where
  myAdd n m := n + m''', size=13)
bullet(s, 8.6, 1.5, 4.0, [
    "class: declares an interface.",
    "instance: provides one implementation.",
    "Lean searches for it automatically.",
    "The real + on Nat works the same way: it finds Add Nat.",
], size=13)
textbox(s, 0.7, 4.3, 12, 2.0,
        "You almost never write classes by hand. The point is: class and instance are not new mechanisms. "
        "class is a structure marked as searchable. instance is just a value of that structure type. "
        "Everything reduces back to inductive.",
        size=14, color=BODY)
page_num(s)

# ============================================================
# SLIDE 15 — abbrev
# ============================================================
s = add_slide()
notes(s, """【0.5 min｜abbrev】
主旨：只是别名，不是新类型。

要点：
- Pair IS Nat × Nat。它不创造新类型，只是把源码写短。
- 四个词里只有 inductive 真的加类型。

坑：这页 30 秒就够，不要拖。""")
title_bar(s, "B · abbrev · a nickname, not a new type", color=B_COLOR)
code_block(s, 0.7, 1.5, 7.0, 1.5,
'''abbrev Pair := Nat × Nat

def myPair : Pair := (3, 4)''', size=15)
bullet(s, 8.2, 1.5, 4.5, [
    "Pair IS Nat × Nat.",
    "It does not create a new type.",
    "It just makes the source shorter.",
    "Contrast: inductive really does add a new type.",
], size=14)
textbox(s, 0.7, 3.5, 12, 2.0,
        "So the hierarchy of \"making a type\" is:\n\n"
        "  inductive  →  genuinely new type, new constructors\n"
        "  structure  →  inductive with one constructor + named fields\n"
        "  class      →  structure + searchability\n"
        "  abbrev     →  not a new type at all, just a name",
        size=14, color=BODY, font=MONO)
page_num(s)

# ============================================================
# C · universe staircase (moved before Terms)
# ============================================================
s = add_slide()
notes(s, """【1 min｜宇宙阶梯】
主旨：类型自己住在一架楼梯上。

要点：
- Prop（Sort 0，装命题）→ Type（Sort 1，普通数据类型）→ Type 1（Sort 2，Type 的类型）。
- 跟 Grothendieck 的宇宙是同一个精神 —— 是类比，不是等同，说的时候带"in the same spirit as"。
- 一句化解："不存在全集的悖论，你只是往上爬。"

坑：不要说"这架楼梯就是 Grothendieck 的宇宙"。是类比。""")
title_bar(s, "C · The universe staircase", color=C_COLOR)
code_block(s, 0.7, 1.5, 7.0, 3.0,
'''#check (2 + 2 = 4)   -- Prop     (Sort 0)
#check 2              -- Nat
#check Nat            -- Type     (Sort 1)
#check Type           -- Type 1   (Sort 2)''', size=15)
bullet(s, 8.2, 1.5, 4.5, [
    "Prop: propositions. Proofs live here.",
    "Type: ordinary data types.",
    "Type 1: the type of Type.",
    "In the same spirit as Grothendieck universes.",
    "No 'set of all sets' paradox — you just climb up.",
], size=13)
textbox(s, 0.7, 5.0, 12, 1.5,
        "Before we look at terms: types themselves live on a staircase. "
        "Prop at the bottom, Type above it, Type 1 above that — forever upward.",
        size=14, bold=True, color=C_COLOR)
page_num(s)

# ============================================================
# SLIDE — C · Terms forms
# ============================================================
s = add_slide()
notes(s, """【1 min｜项的五种形态】
主旨：表达式只有这五种样子，全场再没有第六种。

要点：
- 名字（two）、应用（double two）、lambda（fun n => n+1）、构造子（Color.green）、match（describe）。
- match 必须穷尽所有构造子 —— 漏了 Lean 报错。
- 这一页可以快过，他们真正关心的是 C 和 D 怎么配合。

坑：别在这里逐行敲五个 #check，敲两个就够，把时间留给 31、32。""")
title_bar(s, "C · Terms · five forms you have already used", color=C_COLOR)
code_block(s, 0.7, 1.35, 7.5, 5.3,
'''-- 1. a name
#check two

-- 2. application (supply an input)
#check double two

-- 3. a lambda (build a function)
#check (fun n => n + 1 : Nat → Nat)

-- 4. a constructor (build a value the declared way)
#check Color.green

-- 5. a match (read by constructors)
def describe (c : Color) : String :=
  match c with
  | .red   => "warm"
  | .green => "ok"
  | .blue  => "cold"''', size=13)
bullet(s, 8.6, 1.5, 4.0, [
    "Each form has its own shape.",
    "two and double two do not look alike.",
    "match must cover every constructor.",
    "This is the vocabulary of expressions.",
], size=13)
page_num(s)

# ============================================================
# SLIDE 17 — C · let / have / projection
# ============================================================
s = add_slide()
notes(s, """【1 min｜let / have / 投影】
主旨：三个长得很像、但各管各的工具。

要点：
- let 活在 term 模式，给一个局部的值起名字。
- have 活在 proof 模式（by ... 里面），给一个局部的事实起名字。
- .1 / .2 读 pair 的字段。
- 最常见的错误就是把 let 和 have 混着用。

坑：对 PDE 背景的人，可以直接说 have 就是"记一条引理然后用"——他们一秒就懂。""")
title_bar(s, "C · Three tools that look similar but do different jobs", color=C_COLOR)
code_block(s, 0.7, 1.35, 7.5, 5.3,
'''-- let: name a local VALUE inside a term
def f : Nat :=
  let y := 6
  y + 1
-- #eval f  => 7

-- have: name a local FACT inside a proof
example : 0 = 0 := by
  have h : 0 = 0 := rfl
  exact h

-- .1: read one field of a pair
def g : Nat :=
  let p := (3, true)
  p.1''', size=13)
bullet(s, 8.6, 1.5, 4.0, [
    "let lives in term mode.",
    "have lives in proof mode (by ...).",
    ".1 / .2 read pair fields.",
    "Mixing them up is common. Notice where each is allowed.",
], size=13)
page_num(s)

# ============================================================
# SLIDE — C · → and ∀
# ============================================================
s = add_slide()
notes(s, """【1 min｜→ 和 ∀】
主旨：依赖箭头 Lean 印成 ∀，它们是同一个东西。

要点：
- 非依赖：结果类型不提到输入（Nat → Nat）。依赖：结果里出现 n（(n : Nat) → 0 + n = n）。
- Lean 把后者印成 ∀ (n : ℕ), 0 + n = n : Prop。
- 下面那行输出必须连标注一起念："(Mathlib imported)" —— 装了 Mathlib 时 ℕ 印成 ℕ，core 里印成 Nat。
- 底部那行小字在讲三个不同的箭头：=> 是 fun / match 的分支分隔符；← 只出现在 rw [← h] 这种反向重写里；↔（ASCII 写法 <->）是 Iff 这个 structure，所以它本身也是一个类型，但它产出的命题仍然住在 Prop 里。只有 → 一身两职：既是蕴含联结词，也是函数类型。

坑：上一版踩过的坑 —— 幻灯片把两个环境的输出混在一起，第一行是 core 的、第二行是 Mathlib 的，没有任何一个环境能同时产出。现在标注清楚了，照读。""")
title_bar(s, "C · → and ∀ are the same thing (Pi type)", color=C_COLOR)
code_block(s, 0.7, 1.5, 7.5, 2.8,
'''-- Non-dependent: result does NOT mention the input
#check (Nat → Nat)

-- Dependent: result DOES mention n
#check ((n : Nat) → 0 + n = n)''', size=14)
textbox(s, 0.7, 4.5, 12, 0.5,
        "Lean prints the dependent arrow as ∀ — they are the same thing:", size=14, color=BODY)
code_block(s, 0.7, 5.0, 11, 1.0,
'''-- Lean's output for #check above (Mathlib imported):
--   ℕ → ℕ : Type
--   ∀ (n : ℕ), 0 + n = n : Prop''', size=14)
textbox(s, 0.7, 6.2, 12, 0.8,
        "The lambda calculus is the math underneath: fun n => ... IS a lambda. "
        "=> is the separator inside fun / match;  ← is the rewrite-direction marker;  "
        "↔ (also written <->) is Iff — a structure, so it is a type too; only → doubles as a function type.",
        size=12, color=MUTED)
page_num(s)

# ============================================================
# SLIDE 20 — C · Constructors
# ============================================================
s = add_slide()
notes(s, """【1 min｜构造子】
主旨：一个类型的构造子，就是 Lean 允许你造它的全部方式。

要点：
- Color.red 无输入；MyNat.succ n 要一个输入；And.intro hp hq 要两个证明；⟨w,h⟩ 是见证加证明；rfl 关掉一个定义相等。
- 一句话收尾：match 是把这些构造方式一个个读回来。

坑：严格说 rfl 不是构造子，它是 Eq.refl 的缩写，页面上把它列在这儿是为了对称。不用主动挑这个刺。""")
title_bar(s, "C · A constructor is one allowed way to build a term", color=C_COLOR)
rows = [
    ("Color.red",        "no input",     "one of three choices"),
    ("MyNat.succ n",     "one input",    "build a bigger MyNat"),
    ("And.intro hp hq",  "two proofs",   "build P ∧ Q"),
    ("⟨w, h⟩",           "witness+proof","build ∃ k, P k"),
    ("rfl",              "no input",     "Eq.refl when sides match"),
]
y = 1.5
for ctor, needs, what in rows:
    code_block(s, 0.7, y, 2.8, 0.55, ctor, size=13)
    textbox(s, 3.7, y+0.05, 2.5, 0.5, needs, size=13, color=BODY)
    textbox(s, 6.3, y+0.05, 6.5, 0.5, what, size=13, color=MUTED)
    y += 0.85
textbox(s, 0.7, 6.2, 12, 0.8,
        "The constructors of a type are exactly the ways Lean lets you build it. match reads them back.",
        size=13, color=C_COLOR, bold=True)
page_num(s)

# ============================================================
# SLIDE 21 — One mechanism, three interfaces
# ============================================================
s = add_slide()
notes(s, """【1 min｜一个机制，三个界面】
主旨：同一个 inductive，你用三种方式和它打交道。

要点：
- B 声明（slide 21 已经声明过 MyNat，这里不重复声明）、C 构造与读取、D 按构造子做归纳。
- 右下角是形状示意，页面上标了 (shape only — not runnable here)；完整可运行的例子在第 32 页。

坑：别让右下角被误当成能跑的代码。指一下 (shape only) 这个标注。""")
title_bar(s, "One inductive, three ways you touch it")
# B
tag(s, 0.7, 1.5, "B", B_COLOR, "Declare (slide 21)")
code_block(s, 0.7, 2.0, 5.8, 1.5,
'''-- inductive MyNat where   (already declared on slide 21)
--   | zero
--   | succ (n : MyNat)
-- You do not re-declare it here.''', size=12)
# C
tag(s, 0.7, 3.8, "C", C_COLOR, "Build / read")
code_block(s, 0.7, 4.3, 5.8, 1.8,
'''#check MyNat.succ MyNat.zero

-- match reads one constructor at a time
-- (see describe in practice file)''', size=12)
# D
tag(s, 7.0, 1.5, "D", D_COLOR, "Prove (shape only)")
code_block(s, 7.0, 2.0, 5.6, 3.0,
'''-- (shape only — not runnable here)
-- induction n with
-- | zero   => rfl
-- | succ k ih =>
--   rw [...]  -- see slide 32 for the
--             -- fully worked example''', size=12)
textbox(s, 7.0, 5.2, 5.6, 1.5,
        "induction follows the constructors.\n"
        "zero case, then succ case with an\n"
        "induction hypothesis ih.",
        size=13, color=BODY)
page_num(s)

# ============================================================
# SLIDE 22 — D · Tactics
# ============================================================
s = add_slide()
notes(s, """【1.5 min｜D 家：tactic】
主旨：tactic 是帮你造出一个 C 项的脚手架，不是被存下来的那个证明。这是他们最容易误解的一点。

要点：
- intro n（假设 n，开始一个函数项）、exact h（把 h 交出去，类型必须匹配）、rfl（关掉定义相等）、rw [h]（用 h 改写，留下新目标）、sorry（显式留洞）。
- 关键句：tactic 不是存下来的证明。内核存的是最后那个项，tactic 是帮你写它的元程序。
- sorry 是洞，不是证明。

坑：这一页讲透，后面 32 页就顺了。多花两分钟值得。""")
title_bar(s, "D · Proof strategies · tactics help you build a C term", color=D_COLOR)
tactics = [
    ("intro n",  "Assume n. Starts a function term."),
    ("exact h",  "Hand over h. h must match the goal's type."),
    ("rfl",      "Close a definitional equality."),
    ("rw [h]",   "Rewrite with h. Leaves a new goal."),
    ("sorry",    "Leave an explicit gap. Not a proof."),
]
y = 1.5
for tac, desc in tactics:
    code_block(s, 0.7, y, 2.2, 0.55, tac, size=14)
    textbox(s, 3.1, y+0.05, 9.5, 0.5, desc, size=13, color=BODY)
    y += 0.8
textbox(s, 0.7, 6.0, 12, 1.0,
        "Tactics are not the stored proof. The kernel stores the resulting C term. "
        "Tactics are a meta-program that helps you write that term.",
        size=13, color=MUTED)
page_num(s)

# ============================================================
# SLIDE 23 — Full proof step by step
# ============================================================
s = add_slide()
notes(s, """【2 min｜一个完整证明】
主旨：一个完整证明，每一步都看得见。让他们盯着 infoview 看目标怎么变。

要点：
- 逐行念：induction n 把 n 按构造子拆开 → zero 分支 rfl → succ 分支 rw [Nat.add_succ] 再 rw [ih]，最后一步自动被 rfl 关掉。
- 顺便解释为什么改名叫 nat_zero_add：core 里已经有 Nat.zero_add，重名会报错。
- 一定要点明那条不对称：0 + n = n 必须归纳，n + 0 = n 才是 rfl。

坑：最后那条不对称必须讲，否则他们回去自己写会撞墙，而且是很难查的那种墙。""")
title_bar(s, "D · One complete proof, every step visible", color=D_COLOR)
code_block(s, 0.7, 1.35, 7.5, 5.5,
'''theorem nat_zero_add (n : Nat) : 0 + n = n := by
  -- goal: 0 + n = n
  induction n with
  | zero =>
    -- goal: 0 + 0 = 0
    rfl
  | succ k ih =>
    -- ih : 0 + k = k
    -- goal: 0 + succ k = succ k
    rw [Nat.add_succ]
    -- goal: succ (0 + k) = succ k
    rw [ih]
    -- goal: succ k = succ k (rw closes it)
-- note: core already has Nat.zero_add;
-- we rename it to avoid a name collision.''', size=12)
bullet(s, 8.6, 1.5, 4.0, [
    " induction splits on the constructors.",
    "zero case closes by rfl.",
    "succ case: two rewrites; the second closes it.",
    "Watch the infoview after each line.",
], size=13)
page_num(s)

# ============================================================
# SLIDE 33 (NEW) — Bridge: where the analysis stands in Lean today
# ============================================================
s = add_slide()
notes(s, """【2 min｜桥接：你们的分析在 Lean 里到哪一步了】
主旨：测度、分布、Sobolev 这些东西 Lean 里已经有；缺的是 PDE 这一层。这页是专门讲给 PDE 背景的人听的。

要点：
- 绿栏每一条都在这台机器上 #check 过：MeasureTheory.Measure / .integral / .Integrable、MeasureTheory.Lp、Distribution、TestFunction、SchwartzMap、BesselPotentialSpace（这就是 H^{s,p}）、MeasureTheory.eLpNorm_le_eLpNorm_fderiv（Sobolev 不等式）、Laplacian.laplacian 与 InnerProductSpace.HarmonicAt、gronwallBound / IsPicardLindelof / FourierTransform。
- 另两个备查全名：InnerProductSpace.laplacianWithin 是带开集参数的那一版；Laplacian.laplacian 的记号 Δ 是 scoped notation，不先 open 直接写 Δ 会得到 unknown identifier —— 所以这页坚持写全名。
- 红栏每一条都是在全部 8,624 个文件里 grep 出来的，口径是「不作为定义或定理出现」：curl 零代码命中（唯一那条命中在 Tactic/Polyrith.lean 的 docstring 里，说的是命令行 HTTP 工具 curl）、mollifier 零命中、smoothing 零代码命中（Akra–Bazzi 的 docstring 讲的是 smoothing function ε(x)=1/log x）、涡度与输运方程零命中、Euler 方程零命中（euler 的 588 条命中全是组合数学的 Eulerian trails）、弱解空间零命中（单数 weak solution 只在 Analysis/Distribution/TestFunction.lean 的 docstring 里出现过一次，是动机性文字）、Navier–Stokes 零命中、Stokes 只在一条 docstring 里出现过一次、根本没有 Analysis/PDE 目录。
- 落点句（照读）：Mathlib 有 Laplacian，却没有 curl。分析层在，PDE 层不在。

坑：一定要说清楚"这不是 Lean 做不了 PDE，是 PDE 这一层还没人做"。不要给任何时间表，也不要说"很快就会有人做"。""")
title_bar(s, "Where the analysis stands in Lean today (measured, not guessed)", color=C_COLOR)
textbox(s, 0.7, 1.12, 12, 0.45,
        "Lean 4.35.0 + Mathlib, 8,624 .lean files. Every green line was #check-ed on this machine; "
        "every red line appears in no definition or theorem.",
        size=12, color=BODY)
# ---- left: present ----
box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(1.65), Inches(6.0), Inches(4.7))
box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0xEC,0xFD,0xF5)
box.line.color.rgb = B_COLOR; box.line.width=Pt(1.5); box.shadow.inherit=False
textbox(s, 0.95, 1.78, 5.5, 0.4, "Already in Mathlib", size=17, bold=True, color=B_COLOR)
present = [
    ("Measure & integration",  "MeasureTheory.Measure, .integral, .Integrable"),
    ("Lp spaces",              "MeasureTheory.Lp"),
    ("Distributions, tests",   "Distribution, TestFunction, SchwartzMap"),
    ("Sobolev space (a type)", "BesselPotentialSpace  =  H^{s, p}(E,F)"),
    ("Sobolev inequality",     "MeasureTheory.eLpNorm_le_eLpNorm_fderiv"),
    ("Laplacian, harmonic fns","Laplacian.laplacian, InnerProductSpace.HarmonicAt"),
    ("Gronwall, Fourier",      "gronwallBound, IsPicardLindelof, FourierTransform"),
]
y = 2.3
for h, d in present:
    rich(s, 0.95, y, 5.6, 0.5, [
        [{"t": "✓  ", "c": B_COLOR, "b": True}, {"t": h, "c": INK, "b": True}],
        [{"t": "     " + d, "f": MONO, "c": MUTED, "sz": 10}],
    ], size=12, space_after=0)
    y += 0.53
textbox(s, 0.95, 5.96, 5.6, 0.3,
        'Note: "Δ" is a scoped notation — open it first, or type the full name.',
        size=10, color=MUTED)
# ---- right: absent ----
box2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.65), Inches(5.75), Inches(4.7))
box2.fill.solid(); box2.fill.fore_color.rgb = RGBColor(0xFD,0xEC,0xEC)
box2.line.color.rgb = ACCENT; box2.line.width=Pt(1.5); box2.shadow.inherit=False
textbox(s, 7.15, 1.78, 5.3, 0.4, "Not there (grep over all 8,624 files)", size=17, bold=True, color=ACCENT)
absent = [
    ("curl",                    "0 code hits"),
    ("mollifiers / smoothing",  "0 code hits"),
    ("vorticity, transport eq.", "0 code hits"),
    ("Euler equations",         "0 code hits"),
    ("weak solution spaces",    "0 code hits"),
    ("Navier-Stokes",           "0 code hits"),
    ("Stokes' theorem",         "1 hit, in a docstring"),
    ("a PDE library",           "no Analysis/PDE dir"),
]
y = 2.4
for h, d in absent:
    rich(s, 7.15, y, 5.35, 0.4, [
        [{"t": "✗  ", "c": ACCENT, "b": True}, {"t": h, "c": INK, "b": True},
         {"t": "   " + d, "f": MONO, "c": MUTED, "sz": 10}],
    ], size=12, space_after=0)
    y += 0.43
textbox(s, 7.15, 5.70, 5.35, 0.36,
        '"code hits" = definitions and theorems, not docstrings.\n'
        'Stray hits: "curl" (an HTTP-tool docstring), "smoothing" (Akra–Bazzi notes).',
        size=10, color=MUTED)
rich(s, 0.7, 6.48, 11.4, 0.55, [
    [{"t": "Mathlib has the Laplacian, but not ", "c": BODY},
     {"t": "curl", "f": SANS, "c": ACCENT, "b": True},
     {"t": " — the analysis layer is there; the PDE layer is not. That gap is where this group's expertise lives.", "c": BODY}],
], size=13, space_after=0)
page_num(s)

# ---------- metadata ----------
cp = prs.core_properties
cp.title = "The Map of Lean 4"
cp.subject = "Lean 4 for a 2D Euler research group: what Lean knows, how to name things, how to prove things"
cp.author = "Research group meeting"
cp.last_modified_by = "mavis"
cp.category = "teaching"
cp.keywords = "Lean 4; Mathlib; 2D Euler; PDE; formalization; teaching"
cp.comments = ("v16.5. Audience: PDE people, computer-science beginners. "
               "Every code block compiled on Lean 4.35.0 + Mathlib. "
               "Speaker notes carry the per-slide time budget.")
cp.revision = 11
cp.created = datetime(2026, 10, 29)
cp.modified = datetime(2026, 10, 29)

# ---------- save ----------
_os.makedirs(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "build"), exist_ok=True)
out = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "build", "Lean4_The_Map_v16.5.pptx")
prs.save(out)
print(f"Saved: {out}")
print(f"Slides: {len(prs.slides)}")
n_notes = sum(1 for sl in prs.slides if sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip())
print(f"Slides with speaker notes: {n_notes}/{len(prs.slides)}")
