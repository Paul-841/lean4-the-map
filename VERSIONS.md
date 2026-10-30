# 版本台账

## 命名规则

| 级别 | 含义 | 例子 |
|---|---|---|
| **大版本 `X.0`** | 结构变 / **页数变** / 加章节 / 大改内容 | `v15.4` → **`v16.0`** |
| **小版本 `X.Y`** | 讲法 / 备注 / 措辞 / 排版细节 | `v16.1` → `v16.2` |

- 每份交付物**文件名必须带版本号**（pptx / pdf / 报告 / 脚本）。
- 旧版本**不删**，留在 `deck/` 里，便于对照。
- 生成脚本按版本分文件：`src/gen_v16_6.py` 是 v16.6 的真源，`src/gen_v16_5.py` 是 v16.5 的真源，`src/gen_v16_4.py` 是 v16.4 的真源，`src/gen_v16_3.py` 是 v16.3 的真源，`src/gen_v16_2.py` 是 v16.2 的真源，`src/gen_v16_1.py` 是 v16.1 的真源，`src/gen_v16_0.py` 是 v16.0 的真源，`src/gen_v14_2.py` 是 v15.4 的真源。
  （脚本名沿用 v14 时代的 `gen_v14_2` 命名，因为它产出过 v15.1–v15.4；v16.0 起脚本名与版本号对齐。）

---

---

---

---

---

## v16.6 —— 第三份外部审阅的逐条核实：13 处修正（当前最新版）

**2026-10-30**｜33 页（页数不变）｜时间预算 36.0 min｜元数据 `revision=12`

### 审阅是谁、说了什么

第三份外部审阅，逐页给了"照读成什么"的说法。它自己 #check 过 Mathlib、也读了源码，
但**没有重编译**，而且有两条事实性错误。本轮把它的每一条断言都上机核了（三轮探针）。

### 审阅成立、已修（4 处屏上 + 9 处备注）

| # | 位置 | 原文 | 改成 | 为什么 |
|---|---|---|---|---|
| 1 | p19 灰框 | "structure, class and abbrev are all inductive in disguise" | "structure and class are inductive in disguise; abbrev is only a nickname" | 实测 `abbrev MyAlias := Nat` → `@[reducible] def MyAlias : Type := Nat`，就是 def。**且这一页自己矛盾**：绿框写着"abbrev → just a name, not a type"，p24 写着"abbrev → not a new type at all" |
| 2 | p19 灰框第 2 段 | "Every type in Mathlib — Measure, Lp, Distribution, the Sobolev space" | "Measure, Lp, Distribution, the Sobolev space — all built out of that machinery: structures (inductives in disguise) and abbreviations over them" | 本机 Mathlib 里 `MeasureTheory.Lp` 是 `def Lp … : AddSubgroup (α →ₘ[μ] E)`（一个函数集合，不是类型），`Distribution` 是 abbrev |
| 3 | p10 Formation 行 | "you write inductive / def / structure" | "you write inductive / structure / class" | `def` 不声明类型：p18 自己写着"def: name a value"，`def two : Nat := 2` 是个项 |
| 4 | p10 Introduction 行 | "these are the ONLY ways to make a term" | "these are the ONLY ways to introduce a value" | 字面为假：`2 + 2` 是 Nat 的项，但不是构造子应用 |
| 5 | p10 Elimination 行 | "this is the ONLY way to USE a term" | "the ONLY way to take that type apart" | 限定到"把这个类型拆开" |
| 6 | p27 屏上 + 备注 | "let lives in term mode / have lives in proof mode" | "let: term mode (also a tactic). / have: proof mode (also works in a term)." + "Working rules, not laws." | 实测 `def fHave : Nat := have h : True := trivial; 1` **能编译**（Lean 4.35.0）；`let` 也能当 tactic（`example : True := by let x := 5; trivial` 通过） |
| 7 | p26 备注 | "表达式只有这五种样子，全场再没有第六种" | "到这里已经用过五种样子（第 27 页还会冒出第六种 let）" | 第 27 页就有第六种 |
| 8 | p6 备注（2 处） | "中间 Lean 真实写法" | "中间类型论词汇" | 中间那列的 `Π`/`Σ`/`⊕` 你在 Lean 里并不这么写（Lean 写的是 `∧ ∨ → ↔ ∀ ∃ =`） |
| 9 | p7 屏上末行 | "Lean writes … ∃ as ⟨witness, proof⟩" | "for ∃ the statement is ∃ x, P x, and the proof you hand over is ⟨witness, proof⟩" | 命题与证明不是一回事；同一页代码里写的就是 `example : ∃ k : Nat, …` |
| 10 | p7 备注 | — | 补一条：底下那行 P(0)/P(1) 是另一个谓词 | 别和左边代码的 P 混 |
| 11 | p32 代码注释 | "core already has Nat.zero_add; we rename it to avoid a name collision" | "core has Nat.zero_add, and Mathlib exports a root-level zero_add too -- so we pick a fresh name" | `Nat.zero_add` 带命名空间，本来就不撞；真正会撞的是 Mathlib 根命名空间的 `zero_add`（实测 `error: zero_add has already been declared`） |
| 12 | p23 备注 | — | 补一条：`+` 展开就是 `HAdd.hAdd` | 实测 `example : (2 : Nat) + 2 = HAdd.hAdd 2 2 := rfl` 通过；infoview 点 `+` 看到的是 HAdd |
| 13 | p33 备注（3 处） | "BesselPotentialSpace（这就是 H^{s,p}）" / "eLpNorm_le_eLpNorm_fderiv（Sobolev 不等式）" / 红栏 | 各自补精确读法 + 快照口径 | 见下 |

**p33 三处精确读法（都是给 PDE 听众的）**：

- `BesselPotentialSpace` = Mathlib 自己的 docstring 原话："also known as the Sobolev space and usually denoted by `H^{s,p}`"，
  是 **Fourier 侧**的定义（缓分布的 Bessel potential 落在 `Lp` 里），不是弱导数那个 `W^{k,p}`；
  另有一个未打包的谓词 `TemperedDistribution.MemSobolev`。
- `eLpNorm_le_eLpNorm_fderiv` 的真实语句（实测 `#check`）：`ContDiff ℝ 1 u` + `support u ⊆ s` +
  `1 ≤ p` + `p < finrank ℝ E` + 有界 `s` + Haar 测度 ⇒ `eLpNorm u p μ ≤ C · eLpNorm (fderiv ℝ u) p μ`。
  是 **Gagliardo–Nirenberg 型**的估计，**不是 `H^{s,p}` 空间上的定理**；
  临界嵌入（指数更高）是同文件的 `eLpNorm_le_eLpNorm_fderiv_of_eq`（关系 `(p')⁻¹ = p⁻¹ - (finrank)⁻¹`）。
- `Distribution` 是**根命名空间**的名字（`MeasureTheory.Distribution` 这个名字不存在），
  是测试函数上的连续线性泛函 —— 念一句，免得有人听成"概率分布"。
- 红栏是 **4.35.0 + 那份 Mathlib 的快照**：Lean 4.36.0-rc2 已于 2026-10-27 发布
  （GitHub releases feed 实测），红栏可能随工具链移动。

### 审阅说错、我不改的

| 审阅的说法 | 实测结论 |
|---|---|
| "A top-level `zero_add` would also compile" | **错**。Mathlib 导出了根命名空间的 `zero_add`（`@zero_add : ∀ {M} [AddZeroClass M] (a : M), 0 + a = a`），顶层再写会 `error: zero_add has already been declared` |
| "Lᵖ sits on the quotient from the left box (functions modulo almost-everywhere equality)" | **与本机 Mathlib 不符**。`Mathlib/MeasureTheory/Function/LpSpace/Basic.lean:89`：`def Lp … : AddSubgroup (α →ₘ[μ] E) where carrier := { f | eLpNorm f p μ < ∞ }`；整个 `LpSpace/` 目录 grep 不到任何 `Quotient` |
| "⊤ / ⊥ are not core Lean tokens" | **对，但 deck 备注本来就这么写着**（p6 备注第 5 条：纯 core 连这两个 token 都没有）⇒ 不是新缺陷 |
| "Stop on the ↔ row / Iff is a structure with mp and mpr / hom-set 精确讲是一对箭头" | **deck 备注本来就这么写着**（p6 备注第 3、4 条与坑行）⇒ 不是新缺陷 |
| 第 32 页那段引文 | 内容对，但**不是逐字引文**：备注原文是"0 + n = n 必须归纳，n + 0 = n 才是 rfl" |
| "The title slide is dated 29 October 2026. Today is the 30th." | 用户已拍板：**保持 29 October 不动** |

### 验证结果

| 项 | 结果 |
|---|---|
| 幻灯片数 / 演讲备注 / 时间预算 | 33 / 33 / 36.0 min（均不变） |
| 结构 QA | ISSUES: 0 |
| 字体缺字审计 | 与 v16.5 **零新增**（唯一变化：p7 的 `∃` 计数 5→6，同字符同页） |
| 按页序整份代码流（Mathlib / core-only） | exit=0 / exit=0 |
| 30 个代码块逐块编译 | 0 个真语法/类型错误 |
| 练习文件（Mathlib / core-only） | exit=0 / exit=0 |
| **v16.5 ↔ v16.6 逐页像素比对** | **只有 p01 / p07 / p10 / p19 / p27 / p32 变化，其余 27 页像素完全一致** |
| 渲染目视 | p07（末行仍单行未折行）/ p10（三行各单行）/ p19（灰框 4 行在框内）/ p27（第 4 条折 2 行）/ p32（注释 2 行）逐页看过 |
| 公开版 vs 教学版正文逐段 diff | 0 差异行（599 / 599 段） |
| 仓库自证 + 远端回验 | ALL GREEN |

v16.6 的真源脚本：`src/gen_v16_6.py`（由 `_review_v160/make_v16_6.py` 从 v16.5 真源打 23 步补丁生成，
末尾带一道 `compile()` 自检 —— 备注/代码块是 triple-quoted 字符串，整行替换吞掉收尾三引号的坑已经踩过两次）。

---

## v16.5 —— 第 19 页「内核只有三种形成类型的方式」字面过头（上一版）

**2026-10-30**｜33 页（页数不变）｜时间预算 36.0 min｜元数据 `revision=11`

### 起因

第 19 页（Two buckets: what Lean gives you, what you build）左栏原句：

> The kernel **only** knows three ways to form a type:
>   Sort   (Prop, Type, Type 1 ...)
>   → / ∀  (Pi type)
>   Quot   (quotient)

页面下方挂了对冲句（"This is a mechanism map, not a closed inventory — reduction and recursion also live here."），
备注里也写着"坑：不要说『内核只有这三个』"。所以有一个审计方判定"有对冲句就没事"。

另一个审计方指出措辞要更准（`Nat.rec` 是 term 不是 type；内核的 declaration 里确实有 inductive declaration）。
我随后上机核了 Lean 4.35.0 内核源码 `src/kernel/declaration.h`，逐字如下：

```cpp
enum class declaration_kind { Axiom, Definition, Theorem, Opaque, Quot,
                             MutualDefinition, Inductive };
enum class constant_info_kind { Axiom, Definition, Theorem, Opaque, Quot,
                                Inductive, Constructor, Recursor };
```

同文件另有 `inductive_decl (lparams) (nparams) (types : List InductiveType) (isUnsafe)`
与 `struct InductiveType { name, type, ctors }`。

⇒ 内核除了 Sort / Pi / Quot，还有**第 4 种形成类型的机制：归纳类型声明**
（`inductDecl`，连带构造子 `Constructor` 与递归子 `Recursor`）。
对冲句能挡"这是封闭清单"的读法，**挡不住 `only` 这个字本身** ——
内核确实不只三种方式形成类型。

### 裁定

**改**。理由不是"措辞不够谨慎"，而是这句可以用内核源码直接证伪；
本 deck 的体例是"屏上每句话都能被实测/源码钉住"，明知有反例还留着是自砸招牌。

### 改法（只动第 19 页左栏，页数不变）

| | 文本 |
|---|---|
| 标题 | `Kernel: three type-formers`（不动） |
| 首句 | `The kernel only knows three ways to form a type:` → `The kernel has exactly three type-formers:` |
| 新增一行 | `inductive`（等宽 + 绿色，与右栏同一套）+ ` is not one of these three (see right).` |

- 去掉 `only`，把"形成类型的方式"换成有精确边界的 **type-former**（值级的类型构造子）：
  Sort / Pi / Quot 正好三个；`inductive` 不是 former，是**声明**，所以归右栏。
- 新增那行把第 4 种机制**点名并划界**；`inductive` 用与右栏相同的绿 / 等宽 / 粗体，视线直接接上。
- 备注同步：主旨行 + 坑行。
- `Lean4_practice.lean` 同步：版本行；SLIDE 19 注释把 LEFT 桶拆成"三个 type-former + Lean 预装的类型"，
  并补一句"Nat/Bool/List 虽是预装，但写法和你的一样 —— 也是 inductive"
  （原注释把它们和 Sort / → / Quot 混在一桶，与屏上右栏"AND Nat, Bool, List!"对不上）。

### 未做（记录，避免下一轮重复讨论）

- 底部面板 `There is exactly ONE way to add a type` 不动：同句自带限定语
  （structure / class / abbrev 全是 inductive 换皮）。残留边角：
  `axiom Foo : Type` / `opaque Foo : Type` 也能造出一个类型（无构造子、不可消去），属退化用法，
  本轮只记录，不动屏。
- 第 9 页不动（v16.4 刚拍板）。
- deck 整体重排仍未做（选项 A/B/C 仍待用户拍板）。

### 验证结果

| 项 | 结果 |
|---|---|
| 幻灯片数 / 演讲备注 / 时间预算 | 33 / 33 / 36.0 min（均不变） |
| 结构 QA | ISSUES: 0 |
| 字体缺字审计 | 与 v16.4 **逐条相同**（15 条历史项，零新增；run 数 382→383 / 284→285 = 新增那一行） |
| 按页序整份代码流（Mathlib / core-only） | exit=0 / exit=0 |
| 30 个代码块逐块编译 | 0 个真语法/类型错误 |
| 练习文件（Mathlib / core-only） | exit=0 / exit=0 |
| **v16.4 ↔ v16.5 逐页像素比对** | **只有 p01（版本号）/ p19 变化，其余 31 页像素完全一致** |
| 渲染目视 | p19 整页 + 左栏 300 dpi 放大复核：新行单行未折行、未溢出蓝框 |
| 公开版 vs 教学版正文逐段 diff | 0 差异行（599 / 599 段） |
| 公开版 notesSlide 残留 | 0 |

v16.5 的真源脚本：`src/gen_v16_5.py`（由 `_review_v160/make_v16_5.py` 从 v16.4 真源打 8 步补丁生成）。

---

## v16.4 —— 第 9 页落点句加作用域（上一版）

**2026-10-30**｜33 页（页数不变）｜时间预算 36.0 min｜元数据 `revision=10`

### 起因

第三方审计翻到第 9 页（"What IS a type? Four rules — not a set"）底部那句：

> No analogy. No 'set of functions'. **The four rules ARE the definition.**
> **Every type you meet — Nat, Sum, Sigma, Empty — works the same way.**

前两句没问题，第三句越界了。上机实测：

| 类型 | Introduction | Elimination | Computation |
|---|---|---|---|
| `A → B`（页上这套） | `fun x => t` | `f a` | β 归约 |
| `Nat` | `Nat.zero` / `Nat.succ` | `Nat.rec` / `Nat.casesOn` | 递归子展开 |
| `Sum` | `Sum.inl` / `Sum.inr` | `Sum.rec` | 递归子展开 |
| `Sigma` | `Sigma.mk` | `Sigma.rec` | 递归子展开 |
| `Empty` | **零构造子 ⇒ 没有 introduction 规则** | `Empty.rec` / `Empty.elim` | — |

⇒ "works the same way" 字面为假：只有 `A → B` 这一族是 λ / app / β；
`Empty.intro` 直接报 `Unknown constant`。

而且第 10 页明写的是相反且更精确的说法（"one declaration pins down all four rules"、
"introduction & computation are per-constructor; formation & elimination are per-type"）——
第 9 页这半句等于和它自己下一页打架。

**体例问题**：第 19 页讲"内核三个原语"这类简化时，页面专门挂了对冲句
（"This is a mechanism map, not a closed inventory"），备注还写着"一定要念页面上的对冲句"。
第 9 页做了同类简化却没挂 —— 违反 deck 自己的规矩。

### 两个审计方的最终裁定

事实全部成立；**严重度从"硬错误 / 与第 10 页冲突"下调一档到"措辞级 P2（缺对冲句）"**：
四规则是统一施加于所有类型形成者的**框架**，Empty 是"零条引入规则"的合法实例而非反例；
而且第 9 页右栏本来就写着 "(lambda / constructor)" / "(application / match)"，读者手上的线索是齐的。
用户已拍板：**只修底部那半句**。

### 改法

```
No analogy. No 'set of functions'. Every type is defined by four rules —
formation, introduction, elimination, computation. Same four slots every time,
different content: inductives use constructors and recursors (next slide);
Empty has zero constructors, so no introduction rule at all.
```

保留 "No analogy. No 'set of functions'."（这一页的立身之本是拆掉"类型 = 集合"的直觉），
把越界的两句换成"每个类型都被四条规则钉住，但四格内容不同"，并显式点名 Empty 的零构造子、
指向下一页。备注同步加一条"落点句（照读页面底部）"。

### 验证结果

| 项 | 结果 |
|---|---|
| 幻灯片数 / 演讲备注 / 时间预算 | 33 / 33 / 36.0 min（均不变） |
| 结构 QA | ISSUES: 0 |
| 字体缺字审计 | 与 v16.3 **逐条相同**（15 条历史项，零新增） |
| 按页序整份代码流（Mathlib / core-only） | exit=0 / exit=0 |
| 30 个代码块逐块编译 | 0 个真语法/类型错误 |
| 练习文件（Mathlib / core-only） | exit=0 / exit=0 |
| **v16.3 ↔ v16.4 逐页像素比对** | **只有 p01（版本号）/ p09 变化，其余 31 页像素完全一致** |
| 渲染目视 | 33 页 PNG 逐页看过；p09 重点复核（落点面板 2 行，未溢出） |
| 公开版 vs 教学版正文逐段 diff | 0 差异行（598 / 598 段） |

v16.4 的真源脚本：`src/gen_v16_4.py`（由 `_review_v160/make_v16_4.py` 从 v16.3 真源打 6 步补丁生成）。

---

## v16.3 —— 审计清单 7 项修正（上一版）

**2026-10-30**｜33 页（页数不变）｜时间预算 36.0 min｜元数据 `revision=9`

### 起因

第三方审计提了一份 2×P0 + 2×P1 + 6×P2 的清单。我逐条上机复核后**认下 7 项**
（两个审计方最终收敛到同一张表）；其中 2 条经复测后由审计方主动撤回。

### 7 项清单

| # | 位置 | 问题 | 修法 |
|---|---|---|---|
| 1 | p33 绿栏 | `InnerProductSpace.laplacian` / `HarmonicAt` 在 Mathlib v4.35.0 里**不存在** | 改成 `Laplacian.laplacian` / `InnerProductSpace.HarmonicAt`（两者都 `#check` 过） |
| 2 | p33 备注 | 备注里重复了同样的两个错名 | 同步改正，并补 `InnerProductSpace.laplacianWithin` 备查 |
| 3 | p28 脚注 | "`← and <-> are not types`" 说法错 | 改成三个箭头各司其职：`=>` 是 fun/match 的分隔符、`←` 是反向重写标记、`↔` 是 `Iff`（structure，所以它**是**类型，产出的命题仍在 Prop 里） |
| 4 | p33 红栏 | `curl` 的 "0 hits" 站不住 | 改 "0 code hits"（唯一一条命中是 `Tactic/Polyrith.lean` 里讲命令行 HTTP 工具的 docstring） |
| 5 | p33 红栏 | `mollifiers / smoothing` 的 "0 hits" 站不住 | 同上（命中全在 Akra–Bazzi 的 docstring） |
| 6 | p18 备注 | "`#eval double two` 依赖 slide 17 的 two" | 改掉：这页自己就声明了全局 `two`，**是自足的** |
| 7 | p32 bullet | "succ case: rewrite, rewrite, rfl" 与代码不符 | 改成 "two rewrites; the second closes it"（succ 分支**没有**显式 `rfl`） |

附带（同口径，事实断言不变）：p33 红栏其余 4 条 "0 hits" 统一成 "0 code hits"；
p33 两栏各补一行小字澄清（`Δ` 是 scoped notation；stray hits 的出处）；
p28 备注补一条讲稿兜底；`Lean4_practice.lean` 的版本行与第 33 页注释同步。

### 为什么页面上写全名而不是 Δ

`Laplacian.laplacian` 的记号 `Δ` 是 **scoped notation**
（`Analysis/Distribution/DerivNotation.lean:270`）—— 不 `open scoped` 直接写会得到
`unknown identifier`（实测 exit=1）⇒ 页面上写全名，另加一行小字提醒。

### 验证结果

| 项 | 结果 |
|---|---|
| 幻灯片数 / 演讲备注 | 33 / 33 |
| 时间预算 | 36.0 min（不变） |
| 教学版 QA | ISSUES: 0 |
| 公开版 vs 教学版正文逐段 diff | **0 差异行**（598 / 598 段） |
| 公开版 zip 内 notesSlide 片段 | 0（parts 0），非空备注页 0 |
| 按页序整份代码流（Mathlib / core-only） | exit=0 / exit=0 |
| 30 个代码块逐块编译 | 0 个真语法/类型错误 |
| 练习文件（Mathlib / core-only） | exit=0 / exit=0 |
| 字体缺字审计 | **无新增回退**（`↔ ← → Δ` 均由 Calibri 覆盖） |
| v16.2 ↔ v16.3 逐页像素比对 | **只有 p01 / p28 / p32 / p33 变化，其余 29 页像素完全一致** |
| 渲染目视 | 33 页 PNG 逐页看过；p18 / p28 / p32 / p33 重点复核 + 400 dpi 放大 |

v16.3 的真源脚本：`src/gen_v16_3.py`（由 `_review_v160/make_v16_3.py` 从 v16.2 真源打 14 步补丁生成，可复现）。

---

## v16.2 —— 第 5 页推导顺序修正（上一版）

**2026-10-29**｜33 页（页数不变）｜时间预算 36.0 min｜元数据 `revision=8`

### 起因

用户看渲染图时提了一个问题：

> "你不应该先说就是什么都对应什么？你怎么先说了一个 P 到 Q 呢？你不应该先说 P 是不是就是先是命题，就相当于是这个类型，然后它的证明就是项吗？你怎么先先来了一个从 P 到 Q 就相当于从类型到那个映射呢，这这是不对的吧。"

**他说得对，而且问题比第 5 页内部更深。**

### 诊断：两层问题

**第一层（本版已修）：第 5 页的推导链缺了前两步。**

原版第 5 页第一句就是 `What IS a proof of P→Q? It is a method: give me a proof of P, I give you a proof of Q.`
—— 直接从 `P→Q` 出发，跳过了"命题 = 类型""证明 = 项"这两个前提。听众手里还没有这两个概念，
这句话就只能当句子背，记不住。

**第二层（本版未动，留给用户拍板）：deck 的整体顺序也断了。**

| 内容 | 在第几页 |
|---|---|
| Curry–Howard (1)(2)(2b)(3) | **5–8** |
| "What IS a type? Four rules — not a set" | **9** |
| "A type classifies a term"（term 是什么） | **15** |

⇒ 讲"P→Q 是函数"的时候，**类型**要到第 9 页才定义、**项**要到第 15 页才定义。
本版把第 5 页改成自洽（页内把对应讲全），但结构顺序没动 —— 那属于大版本重排。

### 改了什么（逐条）

| 位置 | 改动 |
|---|---|
| 第 5 页标题 | `Curry-Howard (1): why P→Q is a function` → **`Curry-Howard (1): propositions are types, proofs are terms`** |
| 第 5 页正文 | 顶部换成三步对应块（`rich()` 多 run，关键术语紫色加粗）：① A proposition P **is a type** ② A proof of P **is a term** of that type ③ So `P → Q` **is the function type**, and its proof is a **function** |
| 第 5 页正文 | 代码块 2.0→2.55（高度 2.2→1.75 收紧留白），modus ponens 对照块 4.5→4.55 |
| 第 5 页备注 | 整段重写：三步按顺序念 + 两个坑（"别一上来就说 P→Q 是函数，顺序错了这页就废了" / "term 是全 deck 第一次出现，正式定义在第 15 页"）+ 指向第 25 页宇宙阶梯 |
| 第 5 页时间预算 | 1 min → **1.5 min**（总预算 35.5 → **36.0 min**） |
| 标题页备注 | "幻灯片约 35 分钟" → "幻灯片约 **36 分钟**" |
| 第 6 页备注 | 新增一句桥接："这是第 5 页那条对应的完整版：一行一个联结词……" |
| 文档元数据 | `cp.comments` / `cp.revision` 7→8 |
| 输出路径 | → `Lean4_The_Map_v16.2.pptx` |
| 脚本 | `src/gen_v16_2.py`（由 `src/gen_v16_1.py` 经 `_review_v160/make_v16_2.py` 补丁生成；新正文/备注放在 `_review_v160/v162/` 片段文件里，避免嵌套引号） |

### 验证结果

| 项 | 结果 |
|---|---|
| 幻灯片数 / 演讲备注 | 33 / 33/33 ✓ |
| 时间预算 | 36.0 min（与备注一致） |
| 结构 QA | `ISSUES: 0` |
| `⇒ ⊤ ⊥` 字体回退 | 0 处 |
| 按页序整份代码流（Mathlib / core-only） | exit=0 / exit=0 |
| 30 个代码块逐块编译 | 0 个真语法/类型错误 |
| 练习文件（Mathlib / core-only） | exit=0 / exit=0 |
| 渲染目视 | 33 页 PNG + 3 张联系表全看；p05 另做 200dpi 整页复核 |
| 公开版 vs 教学版正文 diff | **0 差异行**（595/595 段） |
| 公开版 notesSlide | zip 内 0 片段，0 页非空备注 |

---

## v16.1 —— 箭头一致性 + 符号可读性（上一版）

**2026-10-29**｜33 页（页数不变）｜时间预算 35.5 min｜元数据 `revision=7`

### 起因

用户看渲染图时提了两个问题：

1. "P 能推出 Q 对应的箭头你确定对吗？类型论双横、逻辑单横，第 3 行两个横、第 4 行一个横，为啥？"
2. "逻辑里边倒数第 2 行为什么是空的？"

两个都查实了，**都是真问题**，已修。

### 问题 1：第 6 页同一列两种箭头 —— 是 bug，不是约定

第 6 页（Curry-Howard (2)）的 Type theory 列 10 行里，第 3 行写的是 `P ⇒ Q`（U+21D2 双横），
其余 9 行全是 Lean 真实语法；同行的 Why 列又写 "function: P→Q"（单横），第 5 页的真 Lean 代码
`(P → Q) → P → Q` 也是单横 —— 共 4 处互相矛盾。

**Lean 实测结论：Lean 4.35 根本没有 `⇒` 这个记号。**

| 断言 | 证据 |
|---|---|
| `P ⇒ Q` 在 Lean 里是 parse error | `error: unexpected token '⇒'; expected ':=', 'where' or '\|'`（core-only 与 Mathlib 两个环境表现一致） |
| `⇒` 在整个 Lean 4.35 源码里只出现 1 个文件 | `Init/Grind/Attr.lean:130` `syntax grindLR := patternIgnore("⇒" <\|> "=>")` —— 是 grind 策略的语法修饰符，与蕴含无关 |
| `→` 是右结合 | `example (P Q R : Prop) : (P → Q → R) = (P → (Q → R)) := rfl` 通过 |

**改法**：第 3 行改成 Lean 真实写法 `P → Q`——**不是**把第 4 行也改成双横（那样整列就不再是 Lean 了，
第 3 行才是这一列唯一的异类）。表底补一条箭头约定说明，演讲备注补一条给讲者。

> 用户的记忆本身是对的：逻辑书蕴含用单箭头，类型论文献里确实会看到双箭头（⇒，U+21D2），
> 用来把 `A→B` 的两种读法（函数类型 / 蕴含命题）区分开。问题在于**这一列写的是 Lean**，
> 而 Lean 没有 `⇒`。新脚注把这条约定写清楚了，免得听众回去踩坑。

### 问题 2：`⊤` 不是空，是看不清

第 6 页 Logic 列倒数第 2 行是 `⊤`(U+22A4)。Consolas 没有这个码位，渲染时回退到细衬线字体，
11pt 下细到几乎看不见——**不是空格子，是看不清的符号**。

**字体覆盖审计**（fontTools 逐 run 检查，33 页 657 个 run）：19 处缺字回退。
其中只有 `⊤` 真正不可读；其余 18 处回退后目视仍清晰（改 285 个 run 的风险大于收益，不动）。

**改法**：`⊤` / `⊥` 两格改用 **Cambria Math**——Windows 7+ / Office 自带，跨机器放映最稳。
（DejaVu Sans Mono 本机也有，但它不是 Windows 自带字体，换机器放映会掉回细衬线。）

### 连带查实：`⊤` / `⊥` 在 Lean 里到底是什么

| 环境 | `⊤` | `⊥` |
|---|---|---|
| Lean 4.35 core-only | parse error（`expected token`） | parse error |
| Lean 4.35 + Mathlib | `⊤ = True`（`rfl` 可证） | `⊥ = False`（`rfl` 可证） |

⇒ 第 6 页 Logic 列的 `⊤`/`⊥` 是**逻辑记号**（本来就该这么写），不是 Lean 语法；
Lean 写的是 `True` / `False`。演讲备注补了这条，避免听众回去敲 `⊤` 报 parse error。

### 改了什么（逐条）

| 位置 | 改动 |
|---|---|
| 第 6 页表 · Type theory 列第 3 行 | `P ⇒ Q` → `P → Q` |
| 第 6 页表 · Logic 列第 9/10 格 | `⊤` / `⊥` 改用 Cambria Math 渲染 |
| 第 6 页表底 | 新增箭头约定说明（`⇒` 单独用 Cambria Math——Calibri 缺 U+21D2，会回退） |
| 第 6 页演讲备注 | 新增 2 条：箭头约定；`⊤`/`⊥` 与 Lean 的 `True`/`False` 的关系 |
| `code_block()` | 新增可选 `font=` 参数 |
| 文档元数据 | `cp.comments` / `cp.revision` 6→7 |
| 输出路径 | → `Lean4_The_Map_v16.1.pptx` |
| 脚本 | `src/gen_v16_1.py`（由 `src/gen_v16_0.py` 经 11 步补丁生成，**重跑可复现**——实测重生成文件与手改版逐行一致） |

### 验证结果

| 项 | 结果 |
|---|---|
| 幻灯片数 / 演讲备注 / 时间预算 | 33 / 33/33 / 35.5 min（与 v16.0 完全一致） |
| 结构 QA | `ISSUES: 0` |
| `⇒ ⊤ ⊥` 字体回退 | **0 处**（Cambria Math runs=3，覆盖 OK） |
| 按页序整份代码流（Mathlib / core-only） | exit=0 / exit=0 |
| 30 个代码块逐块编译 | 0 个真语法/类型错误 |
| 练习文件（Mathlib / core-only） | exit=0 / exit=0 |
| 渲染目视 | 33 页 PNG + 3 张联系表全看；p06 另做 300 / 500 / 2400 dpi 三级放大复核 |
| 公开版 vs 教学版正文 diff | **0 差异行**（593/593 段） |
| 公开版 notesSlide | zip 内 0 片段，0 页非空备注 |

---

## v16.0 —— 减法版（上一版）

**2026-10-29**｜33 页｜时间预算 35.5 min｜元数据 `revision=6`

### 改了什么

删掉 3 页（用户 2026-10-29 12:17 指令）：

| 删掉的页 | 原标题 | 为什么删 |
|---|---|---|
| v15.4 的 34 | What to practice first | 布置作业式的语气，对研究组听众不必要 |
| v15.4 的 35 | Close the deck. Answer before looking back | 四道自测题，同上 |
| v15.4 的 36 | Closer: what would the FIRST formal statement of 2D Euler be? | 三张卡 + 提问，最后一页不再需要单独收尾 |

**保留**：v15.4 的 31（tactics）、32（完整证明）、33（分析现状桥接页）——页码不变，仍是 31/32/33。

### 连带必须修的（已全部修完并逐条断言）

| 位置 | 改动 |
|---|---|
| 标题页副标题 | `v15.4` → `v16.0` |
| 标题页结尾句 | "We end on a question, not a summary: what would the FIRST formal statement of 2D Euler be?" → **"We end on the gap: the analysis layer is there; the PDE layer is not."** |
| 标题页备注 · 落点预告 | 两个落点 → 只剩一个（"最后一页是给你们的：第 33 页…"，删掉"第 36 页把问题交回给在座各位"） |
| 标题页备注 · 坑 | "第 36 页正面讲" → "第 33 页正面讲" |
| 标题页备注 · 时间预算 | 约 40 分钟 → **约 35 分钟** |
| slide 13 备注 | "第 33 页是给他们的，第 36 页是留给他们的" → "第 33 页（最后一页）是给你们的" |
| slide 13 正文 | "Slide 33 tells you…; slide 36 is the question we end on." → "**Slide 33 — the last one — tells you…**" |
| 文档元数据 | `cp.comments` / `cp.revision` 4→6 |
| 输出路径 | → `Lean4_The_Map_v16.0.pptx` |
| `Lean4_practice.lean` | 删掉 `SLIDE 36` 锚点段；文件头版本号 → v16.0；其余 20 个锚点（14–33）**页码不变** |

### 验证结果

| 项 | 结果 |
|---|---|
| 幻灯片数 | 33 |
| 演讲备注 | 33/33 |
| 时间预算 | 35.5 min |
| 按页序整份代码流（Mathlib） | exit=0，零 error 零 warning |
| 按页序整份代码流（core-only） | exit=0 |
| 30 个代码块逐块编译 | 0 个真语法/类型错误 |
| 练习文件（Mathlib / core-only） | exit=0 / exit=0 |
| 形状越界 / 文本溢出 / 水印 | 0 / 0 / CLEAN |
| 页内引用 | 全部指向真实页码（QA 逐条校验） |
| 残留对 34–39 页的引用 | **0 处**（全文 grep 确认） |
| 渲染目视 | 33 页 PNG 逐页看过；p01 / p13 / p31 / p32 / p33 重点复核 |

---

## v15.4 —— 加法版（上一版）

**2026-10-29**｜36 页｜时间预算 40.5 min｜元数据 `revision=4`

v15.3 → v15.4 的改动见早期报告。相对 v15.3：**新增 slide 33 桥接页 + slide 36 closer 页**、
**补齐 36 条演讲备注**、修掉 slide 10 的自相矛盾、slide 17 的 `import Mathlib.Tactic` 标为可选、
slide 7 的 `refine` 写法修正、slide 19 / 22 打磨、元数据重写、标题页改成对组员说话。

v15.4 的真源脚本：`src/gen_v14_2.py`（产出 v15.1–v15.4 这四个版本）。

> ⚠️ v15.4 里加的 36 / 34 / 35 三页在 v16.0 被删掉了。**如果你觉得删多了，**
> `git log` 里有 v15.4 的完整快照，可以随时取回。

---

## v15.5 —— 另一条分支（已审计，未采纳为交付物）

`Lean4_The_Map_v15.5.pptx` 与 v15.4 逐段 diff 只差封面版本号字符串（641 段中仅 1 段不同），
**没有独立产物、没有脚本分支**。其真实贡献是 2 处措辞修正（slide 3 / slide 25），已并入 v15.4。

完整审计见 `Lean4_The_Map_v15.5_审阅报告.md`（不在本仓库，属内部文档）。
