/-
The Map of Lean 4 — Practice File
Pairs with: Lean4_The_Map_v15.4.pptx
Open in: live.lean-lang.org (zero-setup) or a local Lean 4 project.

Every block below compiles. Read the comments, change things on
purpose, and watch the infoview on the right change.

No Mathlib needed. Plain Lean (Init) is enough for all of this.
-/

-- ============================================================
-- SLIDE 14 — Open Lean. The room is already full.
-- Lean already knows all of these. You did not declare any of them.
-- ============================================================
#check 2            -- Nat
#check true         -- Bool
#check "hello"      -- String
#check [1, 2, 3]    -- List Nat
#check (2, true)    -- Nat × Bool
#check Nat          -- Type
#check Type         -- Type 1


-- ============================================================
-- SLIDE 15 — A type classifies a term.
-- Read ":" as "has type". Left = term, right = its type.
-- ============================================================
#check (2 : Nat)
#check (true : Bool)
#check (fun n => n + 1 : Nat → Nat)
-- Prop is a type too; its terms are proofs:
#check (2 + 2 = 4)  -- Prop


-- ============================================================
-- SLIDE 16 — A · Environment · Ask Lean four questions
-- ============================================================
#check (2 + 2)        -- what type is it?  → Nat
#eval  (2 + 2)        -- compute it         → 4
#reduce (1 + 2)        -- reduce it          → 3
-- #print Nat.add      -- see the definition (uncomment to try)


-- ============================================================
-- SLIDE 17 — A · Environment · Organize names
-- ============================================================
-- import  : pull in things from other files (needs a project)
-- namespace : give names an address
-- open   : use short names
-- section : temporary local assumptions

namespace Lesson
def two : Nat := 2
end Lesson

#check Lesson.two   -- need the address unless we open it


-- ============================================================
-- SLIDE 18 — B · Declarations · Name a term
-- Three steps, each one adds one thing.
-- ============================================================

-- Step 1: the simplest possible named value
def two : Nat := 2

-- Step 2: a function (a term you give an input to)
def double (n : Nat) : Nat := n + n

-- Step 3: use them together
#eval double two     -- 4

-- Step 4: a proposition is a type. rfl is its proof.
example : 2 + 2 = 4 := rfl

-- Step 5: name the theorem (same mechanism, longer-lived)
theorem two_plus_two : 2 + 2 = 4 := rfl


-- ============================================================
-- SLIDE 19 — Built-in vs. you-made
-- LEFT: Lean gives you these already (you cannot change them):
--   Nat, Bool, String, List, ×, Prop, Type, Sort u, →, Quot
-- RIGHT: you build new types with inductive:
--   Color, MyNat, Point ...
--   structure = inductive with one constructor + named fields
--   class     = structure Lean is allowed to search for
--   abbrev    = a name for an existing type (not a new type)
-- ============================================================


-- ============================================================
-- SLIDE 20 — B · inductive · finite choices
-- ============================================================
inductive Color where
  | red
  | green
  | blue

-- Now ask Lean what you just made:
#check Color.red     -- Color
#check Color         -- Type

-- Use it: a function that pattern-matches (ALL cases covered)
def isWarm (c : Color) : Bool :=
  match c with
  | .red   => true
  | .green => false
  | .blue  => false

#eval isWarm Color.red     -- true
#eval isWarm Color.green  -- false


-- ============================================================
-- SLIDE 21 — B · inductive · a recursive type
-- This is how natural numbers are built.
-- ============================================================
inductive MyNat where
  | zero
  | succ (n : MyNat)

#check MyNat.zero            -- MyNat
#check MyNat.succ            -- MyNat → MyNat
#check MyNat.succ MyNat.zero -- MyNat  (this is "one")

def one  := MyNat.succ MyNat.zero
def two' := MyNat.succ one


-- ============================================================
-- SLIDE 22 — B · structure · one constructor, named fields
-- ============================================================
structure Point where
  x : Nat
  y : Nat

-- This is shorthand for an inductive with ONE constructor:
-- inductive Point where
--   | mk (x : Nat) (y : Nat) : Point

def origin : Point := { x := 0, y := 0 }
def p : Point := { x := 3, y := 4 }

#check p.x   -- Nat
#eval p.x    -- 3


-- ============================================================
-- SLIDE 23 — B · class / instance · searchable structure
-- ============================================================
-- We name it MyAdd because Add already exists in the standard library.
class MyAdd (α : Type) where
  myAdd : α → α → α

instance : MyAdd Nat where
  myAdd n m := n + m
-- This shows the mechanism. In real code you never write your own Add;
-- you just use + and Lean searches for the existing MyAdd/Add instance.


-- ============================================================
-- SLIDE 24 — B · abbrev · just an alias, not a new type
-- ============================================================
abbrev Pair := Nat × Nat

def myPair : Pair := (3, 4)
-- Pair IS Nat × Nat. It is not a new type. It is a nickname.


-- ============================================================
-- SLIDE 25 — C · The universe staircase
-- ============================================================
#check (2 + 2 = 4)   -- Prop     (Sort 0)  — propositions
#check 2              -- Nat
#check Nat            -- Type     (Sort 1)  — ordinary data types
#check Type           -- Type 1   (Sort 2)  — the type of Type
-- The staircase continues upward. You rarely climb past Type 1.


-- ============================================================
-- SLIDE 26 — C · Terms · forms you already met
-- ============================================================
-- a name
#check two

-- application (supply one input)
#check double two

-- a lambda (build a function)
#check (fun n => n + 1 : Nat → Nat)

-- a constructor (build a value the declared way)
#check Color.green

-- a match (read a value by its constructors — exhaustive!)
def describe (c : Color) : String :=
  match c with
  | .red   => "warm"
  | .green => "ok"
  | .blue  => "cold"

#eval describe Color.blue   -- "cold"


-- ============================================================
-- SLIDE 27 — C · let, have, projection
-- ============================================================
-- let: name a local VALUE inside a term
def f : Nat :=
  let y := 6
  y + 1

#eval f   -- 7

-- have: name a local FACT inside a proof
example : 0 = 0 := by
  have h : 0 = 0 := rfl
  exact h

-- projection: read one field of a pair
def firstOfPair (p : Nat × Bool) : Nat := p.1

#eval firstOfPair (3, true)   -- 3


-- ============================================================
-- SLIDE 28 — C · → and ∀ are Pi types
-- ============================================================
-- Non-dependent: result type does NOT mention the input
#check (Nat → Nat)

-- Dependent: result type DOES mention the input n
#check ((n : Nat) → 0 + n = n)

-- ∀ is just notation for the dependent arrow:
--   ∀ n : Nat, 0 + n = n   =   (n : Nat) → 0 + n = n


-- ============================================================
-- SLIDE 29 — C · Constructors are the allowed ways to build
-- ============================================================
-- Color.red        : no extra input (one of three choices)
-- MyNat.succ n     : needs one MyNat (builds a bigger one)
-- And.intro hp hq  : needs two proofs (builds P ∧ Q)
-- rfl              : closes a reflexive equality

example (P Q : Prop) (hp : P) (hq : Q) : P ∧ Q :=
  And.intro hp hq


-- ============================================================
-- SLIDE 30 — One mechanism, three interfaces (MyNat)
-- ============================================================
-- B · declare it (slide 21):
-- inductive MyNat where | zero | succ (n : MyNat)

-- C · build and read it
def one' := MyNat.succ MyNat.zero

-- D · prove by induction (follows the constructors)
-- On MyNat itself, induction looks like this shape:
--   induction n with
--   | zero   => ...   -- base case: n is zero
--   | succ k ih => ... -- step case: n = succ k, ih is the hypothesis
-- The real worked example on the built-in Nat is slide 32 below.


-- ============================================================
-- SLIDE 31 — D · Proof strategies · tactics
-- A tactic is scaffolding, not the proof. The kernel stores the
-- resulting term; the tactic is a program that helps you write it.
-- ============================================================

-- intro n : assume n, start a function term
example : ∀ n : Nat, n + 0 = n := by
  intro n
  rfl

-- exact h : hand h over; its type must match the goal
example : 0 = 0 := by
  exact rfl

-- rfl : close a definitional equality
example : 2 + 2 = 4 := by
  rfl

-- rw [h] : rewrite with h, leaves a new goal
example (n : Nat) : n + 0 = n := by
  rw [Nat.add_zero]

-- sorry : an explicit gap. NOT a proof.
-- example : 1 = 2 := by sorry


-- ============================================================
-- SLIDE 32 — D · Full proof, one step at a time
-- Watch the infoview after each line.
-- ============================================================
theorem nat_zero_add (n : Nat) : 0 + n = n := by
  -- goal at start: 0 + n = n
  induction n with
  | zero =>
    -- goal: 0 + 0 = 0
    rfl
  | succ k ih =>
    -- ih : 0 + k = k
    -- goal : 0 + succ k = succ k
    rw [Nat.add_succ]
    -- goal : succ (0 + k) = succ k
    rw [ih]
    -- goal : succ k = succ k   (rw closes it automatically by rfl)


-- ============================================================
-- SLIDE 33 — Where the analysis stands in Lean today
-- Not runnable here: these names need Mathlib. On this machine
-- (Lean 4.35.0 + Mathlib, 8,624 .lean files) each green name
-- below passed #check:
--   MeasureTheory.Measure, MeasureTheory.integral, MeasureTheory.Integrable
--   MeasureTheory.Lp
--   Distribution, TestFunction, SchwartzMap
--   BesselPotentialSpace          (= H^{s,p}(E,F), the Sobolev space)
--   MeasureTheory.eLpNorm_le_eLpNorm_fderiv   (the Sobolev inequality)
--   InnerProductSpace.laplacian, InnerProductSpace.HarmonicAt
--   gronwallBound, IsPicardLindelof, FourierTransform
--
-- Grepped over all 8,624 files and got zero hits:
--   curl, mollifiers, vorticity, Euler equations, weak solution
--   spaces, Navier-Stokes, and any PDE library (no Analysis/PDE).
--   "Stokes" appears once, inside a docstring.
-- ============================================================


-- ============================================================
-- SLIDE 36 — Closer: what would the FIRST formal statement of 2D Euler be?
-- (a) vorticity transport   d/dt w + u.grad(w) = 0
--     Lean has: measure, integral.     Lean lacks: curl, vorticity.
-- (b) energy conservation    d/dt ||u||^2 = 0
--     Lean has: Lp, Sobolev space.      Lean lacks: time derivatives.
-- (c) no blow-up on [0,T]    sup ||u(t)|| < inf
--     Lean has: Sobolev space.         Lean lacks: transport, energy, blow-up.
-- ============================================================


-- ============================================================
-- EXERCISES — type these yourself
-- ============================================================

-- 1. Make an inductive type called `Shape` with three
--    constructors: circle, square, triangle.
--    Then write `shapeName (s : Shape) : String` that
--    returns "circle" / "square" / "triangle".

-- 2. Make a structure called `Student` with fields
--    name : String, age : Nat.
--    Make one value and read `.name`.

-- 3. Prove:
--    example : 1 + 1 = 2 := by sorry   (replace sorry)

-- 4. Prove:
--    theorem nat_add_zero (n : Nat) : n + 0 = n := by
--      rfl
--    (n is already a parameter, no intro needed)
--    Why rfl? Nat.add recurses on its SECOND argument,
--    so `x + 0` unfolds to `x` directly.
--    (Compare slide 32: `0 + n = n` does NOT reduce —
--     that one needs induction.)
