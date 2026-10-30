# The Map of Lean 4

**给"PDE 是主场、Lean 是客场"的研究组讲的一份 Lean 4 入门讲义。**
33 页 · 16:9 · 36.0 分钟幻灯片 + 20 分钟讨论 ｜ 当前版本 **v16.4**

> 版本台账见 [VERSIONS.md](VERSIONS.md)。`deck/` 里同时保留 v15.4、v16.0、v16.1、v16.2、v16.3 与 v16.4 六版，便于对照。

---

## 这份讲义是给谁做的

讲给**懂偏微分方程 / 2D Euler，但计算机零基础**的同事。

这个定位决定了全部取舍：不按"CS 零基础"排（那是给程序员的），也不按"PDE 专家"排（那是给形式化专家的）。所以：

- 不讲安装、不讲终端、不讲编辑器配置 —— 只讲**每个词住在哪个房子里**；
- 代码块全部**真编译过**，不是伪代码；
- 最后一页专门回答"PDE 背景的人最该关心的问题：你们的分析在 Lean 里到哪一步了"；
- 讲完之后直接把话头留给在座的专家，而不是替他们总结。

## 讲义结构

| 段落 | 页 | 内容 |
|---|---|---|
| 前置 | 1–4 | 数学比 Lean 大 · 图灵 vs 丘奇 · 从希尔伯特到机器检查 |
| **A** 词汇 | 5–14 | Curry–Howard 对应（逻辑/类型/范畴）· 类型是什么 · 四条规则 · A/B/C/D 四个"家" |
| **B** 声明 | 15–24 | 给项命名 · `def` / `inductive` / `structure` / `class` / `abbrev` |
| **C** 项 | 25–30 | 宇宙阶梯 · 项的五种形式 · Pi 类型 · 构造子 |
| **D** 证明 | 31–32 | tactic 是什么 · 一个每步都看得见的完整证明 |
| 收尾 | 33 | **Lean 里分析的现状（实测）** —— 分析层在，PDE 层不在 |

## 验证结论（全部可复现）

在 **Lean 4.35.0 + Mathlib** 上实测：

| 项 | 结果 |
|---|---|
| 按页序整份代码流（Mathlib 环境） | `exit=0`，零 error 零 warning |
| 按页序整份代码流（core-only，无 Mathlib） | `exit=0` |
| 30 个代码块逐块独立编译 | **0** 个真语法/类型错误 |
| 页码 | 33/33 |
| 演讲备注 | 33/33（教学版） |
| 形状越界 / 文本溢出 | 0 / 0 |
| 水印扫描 | CLEAN |
| 页内引用 | 全部指向真实页码 |
| 渲染目视 | LibreOffice → PDF → 33 页 PNG 逐页看过 |
| 字体覆盖审计（fontTools 逐 run） | `⇒ ⊤ ⊥` **0 处回退**（全部由 Cambria Math 覆盖） |

第 33 页的每一个断言都有实测背书：

- **绿栏（Mathlib 里已有）** —— `MeasureTheory.Measure` / `.integral` / `.Integrable`、`MeasureTheory.Lp`、`Distribution`、`TestFunction`、`SchwartzMap`、`BesselPotentialSpace`（= Sobolev 空间 `H^{s,p}`，是一个真正的类型）、`MeasureTheory.eLpNorm_le_eLpNorm_fderiv`（Sobolev 不等式）、`InnerProductSpace.laplacian`、`HarmonicAt`、`gronwallBound`、`IsPicardLindelof`、`FourierTransform` —— 逐个 `#check` 通过。
- **红栏（还没有）** —— `curl`、mollifier、涡度与输运方程、Euler 方程、弱解空间、Navier–Stokes：在全部 **8,624** 个 `.lean` 文件里 grep **零命中**；`Stokes` 只有 1 次命中且在一条 docstring 里；没有 `Analysis/PDE` 目录。

> 一句话落点：**Mathlib 有 Laplacian，但没有 curl。分析层在，PDE 层不在。**

## 目录结构

```
lean4-the-map/
├── README.md
├── VERSIONS.md                      ← 版本台账（规则 + 每版改了什么）
├── LICENSE                          ← MIT
├── deck/
│   ├── Lean4_The_Map_v16.4.pptx     ← 当前版：33 页，无演讲备注
│   ├── Lean4_The_Map_v16.4.pdf
│   ├── Lean4_The_Map_v16.3.pptx     ← 上一版（33 页），保留供对照
│   ├── Lean4_The_Map_v16.3.pdf
│   ├── Lean4_The_Map_v16.2.pptx     ← 更早版（33 页），保留供对照
│   ├── Lean4_The_Map_v16.2.pdf
│   ├── Lean4_The_Map_v16.1.pptx     ← 更早版（33 页），保留供对照
│   ├── Lean4_The_Map_v16.1.pdf
│   ├── Lean4_The_Map_v16.0.pptx     ← 更早版（33 页），保留供对照
│   ├── Lean4_The_Map_v16.0.pdf
│   ├── Lean4_The_Map_v15.4.pptx     ← 更早版（36 页），保留供对照
│   └── Lean4_The_Map_v15.4.pdf
├── src/
│   ├── gen_v16_4.py                 ← v16.4 的真源生成脚本
│   ├── gen_v16_3.py                 ← v16.3 的真源生成脚本
│   ├── gen_v16_2.py                 ← v16.2 的真源生成脚本
│   ├── gen_v16_1.py                 ← v16.1 的真源生成脚本
│   ├── gen_v16_0.py                 ← v16.0 的真源生成脚本
│   ├── gen_v14_2.py                 ← v15.4 的真源生成脚本（产出过 v15.1–15.4）
│   ├── make_public_deck.py          ← 去备注步骤（吃版本号参数）
│   ├── Lean4_practice.lean          ← 配套练习文件（20 个页码锚点，slide 14–33）
│   └── qa_deck.py                   ← 结构化 QA（页码/备注/越界/溢出/水印/引用/时间预算）
└── build/                           ← 构建产物，已 gitignore
```

## 怎么重建

```bash
pip install python-pptx

# v16.4（当前版）
python src/gen_v16_4.py                     # → build/Lean4_The_Map_v16.4.pptx（带演讲备注）
python src/make_public_deck.py v16.4        # → deck/Lean4_The_Map_v16.4.pptx（去备注）+ build/…_notes.md
python src/qa_deck.py deck/Lean4_The_Map_v16.4.pptx

# v16.3
python src/gen_v16_3.py                     # → build/Lean4_The_Map_v16.3.pptx
python src/make_public_deck.py v16.3        # → deck/Lean4_The_Map_v16.3.pptx

# v16.2
python src/gen_v16_2.py                     # → build/Lean4_The_Map_v16.2.pptx
python src/make_public_deck.py v16.2        # → deck/Lean4_The_Map_v16.2.pptx

# v16.1
python src/gen_v16_1.py                     # → build/Lean4_The_Map_v16.1.pptx
python src/make_public_deck.py v16.1        # → deck/Lean4_The_Map_v16.1.pptx

# v16.0
python src/gen_v16_0.py                     # → build/Lean4_The_Map_v16.0.pptx
python src/make_public_deck.py v16.0        # → deck/Lean4_The_Map_v16.0.pptx

# v15.4（更早版，36 页）
python src/gen_v14_2.py                     # → build/Lean4_The_Map_v15.4.pptx
python src/make_public_deck.py v15.4        # → deck/Lean4_The_Map_v15.4.pptx
```

PDF 用 LibreOffice 转：

```bash
soffice --headless --convert-to pdf --outdir deck deck/Lean4_The_Map_v16.4.pptx
```

需要 Lean 环境做代码验证的话：Lean **4.35.0** + Mathlib，练习文件在 `src/Lean4_practice.lean`。

> 与作者本机版本的唯一差别：`src/gen_v16_4.py` / `src/gen_v16_3.py` / `src/gen_v16_2.py` / `src/gen_v16_1.py` / `src/gen_v16_0.py` / `src/gen_v14_2.py` 的输出路径已改成**相对脚本目录**（原为 Windows 绝对路径），以便任何人克隆后直接跑。其余一字未改。

## 关于"公开版"和"教学版"

这份 PPT 有两个版本：

| | 演讲备注 | 用途 |
|---|---|---|
| **公开版**（本仓库 `deck/`） | **已移除**（逐页删除 `notesSlide` 关系，zip 内零残留） | 对外分享 |
| 教学版 | 33 条三段式备注（主旨 / 要点 / 坑） | 讲课时用 |

两份的**正文逐字一致**（595/595 段，差异 0 行）。备注是讲者备课材料（时间预算、每页可能被问倒的地方），不属于讲义内容，因此不进公开仓库；它由 `make_public_deck.py` 导出到 `build/`（已 gitignore）。

## 许可

MIT，见 [LICENSE](LICENSE)。

---

## English summary

**The Map of Lean 4** — a 33-slide teaching deck for a PDE research group that knows 2D Euler but not computer science.

Every Lean code block was compiled on **Lean 4.35.0 + Mathlib** (whole-file run in page order: `exit=0`, zero errors, zero warnings; 30 blocks compiled individually with 0 genuine syntax/type errors; the deck also compiles in a Mathlib-free core-only environment). Structural QA passes clean: 33/33 page numbers, 33/33 speaker notes, 36.0 min total time budget, 0 shapes out of bounds, 0 text overflows, no watermarks, all in-deck page references valid. All 33 pages were rendered to PDF and inspected visually.

The last slide reports where analysis stands in Lean today, measured rather than guessed: the green column was `#check`-ed on this machine (`MeasureTheory.Measure`, `Lp`, `Distribution`, `BesselPotentialSpace` = the Sobolev space `H^{s,p}` as an actual type, `MeasureTheory.eLpNorm_le_eLpNorm_fderiv`, `InnerProductSpace.laplacian`, `gronwallBound`, `FourierTransform`, …); the red column was grepped for across all **8,624** `.lean` files and got zero hits (`curl`, mollifiers, vorticity, Euler equations, weak solution spaces, Navier–Stokes). The deck does **not** claim Lean will prove 2D Euler global regularity — it states plainly that the analysis layer is there and the PDE layer is not, and leaves the next move to the experts in the room.

The published deck carries **no speaker notes** (the notes are internal prep material and live in the gitignored `build/` directory); the slide body is byte-identical to the teaching version.
