# Harness panel design system — Phase 1 (tokens + global chrome)

Normative reference for the web GUI de-generic-ification (master plan:
`.harness/runs/webgui-design-system-sol.plan.md`, authored by gpt-5.6-sol; this
spec detailed and applied by the overseer). Phases 2–5 consult this file; where
this file and older CSS disagree, this file wins.

Direction (owner's reference doc §11): sophisticated technical dark tool —
GitHub/Vercel structure, Linear density, Railway surfaces. Not gamer, not
cyberpunk, not generic admin. Dark-only.

## 1. Token catalog

Single `:root` block in `scripts/harness_ui_page.py`. Every color in component
CSS must reference a token; the only hex literals live here.

### Typography

| Token | Value | Use |
|---|---|---|
| `--font-ui` | system neo-grotesque stack (`ui-sans-serif`, Segoe UI, …) | Everything except technical content. No external fonts (CSP + zero-request rule). |
| `--font-mono` | `ui-monospace`, Cascadia, Consolas stack | Code, diffs, logs, file paths, IDs, hashes, metrics, the transcript. Never whole-product. |
| `--text-xs` | 0.75rem (12px) | Metadata floor: badges, chips, timestamps, uppercase labels. Nothing essential goes below this. |
| `--text-sm` | 0.8125rem (13px) | Operational content: rows, cards, transcript, buttons, inputs. |
| `--text-md` | 0.875rem (14px) | Body default, dialog text, section headings. |
| `--text-lg` | 1rem (16px) | Page/dialog titles, stat numbers. |
| `--line-tight` 1.25 / `--line-ui` 1.4 / `--line-reading` 1.55 | | Headings / controls-rows / prose blocks. |

### Surfaces (darkest → brightest; a new feature never invents a new grey)

| Token | Value | Use |
|---|---|---|
| `--bg-base` | `#090b0f` | Page background, view backgrounds. |
| `--bg-inset` | `#0c0f14` | Sunken content wells: transcript, code `pre`, JSON boxes, inputs. |
| `--surface-1` | `#10141a` | Primary panels, cards, dialogs, bands. |
| `--surface-2` | `#161b22` | Elevated chrome: header, toolbars, dropdown menus. |
| `--surface-3` | `#1c232c` | Highest resting surface: quiet buttons, kbadges. |
| `--surface-hover` | `#202833` | Hover/selected wash for rows, cards, chips. |
| `--surface-control` | `#1a2028` | Resting form controls that must read as pressable. |
| `--overlay-bg` | `rgb(16 20 26 / 0.96)` | Floating HUD/overlays over content. |

Rules: flat surfaces separated by 1px borders and luminosity — no card-in-card
(structural sections are flat with dividers; only true objects are cards).
Shadows only on `dialog`, `.hud`, `#wsTree` (`--shadow-overlay`). No pure black,
no gradients, no glassmorphism, no decorative glow.

### Structure

`--border-subtle #202832` (internal dividers) · `--border #27303a` (component
edges, the default) · `--border-strong #34404d` (emphasis edges, neutral
button fills) · `--line: 1px solid var(--border)`.

### Text

`--text-primary #eef1f5` (content) · `--text-secondary #9aa5b2` (supporting
text, labels) · `--text-muted #7a8693` (tertiary metadata — nonessential only,
see contrast audit) · `--text-disabled #4e5865` (disabled controls only —
WCAG-exempt).

### Accent & semantics

Color is semantic, never decorative or per-vendor. Each family: full-strength
text/icon tone, `-bg` ~12% tint, `-border` ~34% tint, `-strong` filled-control
tone.

| Family | Text | Meaning |
|---|---|---|
| `--accent` `#8b7cff` (+ `-hover -contrast -bg -border`) | violet | Selection, primary action, focus. The one brand hue. |
| `--stream` `#5ccfe6` | cyan | Live execution / streaming / in-flight only. |
| `--success` `#65c49a` | green | Completed, passing. |
| `--warning` `#e0b66a` | amber | Attention, staleness, cost. |
| `--danger` `#e4777f` | red | Errors, destructive actions, escalations. |
| `--syntax-*` | | Code highlighting only (tree-sitter + CM6); never UI chrome. |

Status is never color alone: pair with text or icon (existing pills/badges all
carry labels — keep that invariant).

### Spacing, shape, density

Spacing scale `--space-1..6` = 4/6/8/12/16/24px — no off-scale gaps.
Radii: `--radius-xs 4px` (tags) · `--radius-sm 6px` (controls, rows) ·
`--radius-md 8px` (overlays, dialogs, object cards) · `--radius-pill` (true
pills/tags only). Chrome heights: `--topbar-h 52px`, `--subnav-h 38px`,
`--row-h 36px`, `--control-h 32px` (controls use min-height so wrapping never
clips).

## 2. Contrast audit (WCAG 2.1, computed)

AA: 4.5 body, 3.0 large/UI-graphics. Audited pairs:

| Pair | Ratio | Verdict |
|---|---|---|
| text-primary on bg-base / surface-1 / surface-3 | 17.4 / 16.3 / 14.0 | AAA |
| text-secondary on bg-base / surface-1 / surface-3 | 7.9 / 7.4 / 6.3 | AAA body |
| text-muted `#7a8693` on bg-base / inset / surface-1 / surface-2 | 5.3 / 5.2 / 5.0 / 4.7 | AA body |
| text-muted on surface-3 / hover | 4.3 / 4.0 | AA-large only → muted on elevated surfaces is metadata-only, ≥12px, nonessential |
| text-disabled (any surface) | 2.1–2.7 | exempt (disabled UI) — never for readable content |
| accent on surface-1 / on accent-bg tint | 5.7 / 4.9 | AA |
| stream / success / warning / danger on surface-1 | 10.1 / 8.7 / 9.7 / 6.4 | AA+ |
| same on their 12% tints | 8.1 / 7.1 / 7.9 / 5.5 | AA |
| accent-contrast (dark) on accent — primary button | 6.0 | AA (white on accent = 3.3, fails → primary buttons use dark text) |
| white on danger-strong `#b84a54` — danger button | 5.1 | AA |

Original plan value `--text-muted #687381` failed AA body (3.8 on surface-1)
and was brightened to `#7a8693`; hierarchy gap to secondary preserved.

## 3. Control specification

All controls: `font: var(--text-sm)/var(--line-ui) var(--font-ui)`,
`min-height: var(--control-h)`, `border-radius: var(--radius-sm)`,
padding `0 var(--space-4)` (inputs `var(--space-2) var(--space-3)`).
Focus is universal: `:focus-visible { outline: 2px solid var(--accent);
outline-offset: 2px; }` — never border-color alone.

| Control | Default | Hover | Active | Disabled |
|---|---|---|---|---|
| Button quiet (`.pillbtn`, `.snew`, `.iconbtn`, `.ebtn`) | transparent bg, `--text-secondary`, no border | `--surface-hover` bg, `--text-primary` | same + `brightness(0.96)` | 45% opacity, no hover |
| Button neutral (`.abadge` base) | `--border-strong` bg, `--text-primary` | `brightness(1.12)` | `brightness(0.95)` | 50% opacity |
| Button primary (`button.act`) | `--accent` bg, `--accent-contrast` text, no border | `--accent-hover` | `brightness(0.95)` | 45% opacity |
| Button danger (`.act.danger`, `.act.stop`, `.abadge-discard`) | `--danger-strong` bg, white text | `brightness(1.12)` | `brightness(0.95)` | 45% opacity |
| Input/select/textarea | `--bg-inset` bg, `--border` 1px, `--text-primary` | `--border-strong` | — | 45% opacity |
| Dialog | `--surface-1`, `--border` 1px, `--radius-md`, `--shadow-overlay`, backdrop `--backdrop` | | | |
| Table row | transparent, `--border-subtle` bottom divider, `--row-h` via padding | `--surface-hover` when interactive | | |

Alert-state quiet button (`.pillbtn.alert`): danger text + danger border —
keeps icon+text, color supplementary.

## 4. Header chrome (52px application bar)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Harness  Chat  Config  Tasks  Queue  Changelog  Specs  Research  Experiments │ 52px, surface-2,
│ [repo ▾] target · branch        ····spacer····  ⚠ Alerts  Advanced ▾         │ border-b --border
└──────────────────────────────────────────────────────────────────────────────┘
```

- Nav items: borderless text buttons (quiet spec), `--text-secondary`,
  no emojis in labels (emoji stays in `title` tooltips). Height fills the bar.
- Selected (`.navsel`): `--text-primary` + 2px `--accent` inset underline
  (`box-shadow: inset 0 -2px 0 var(--accent)`) — no filled pill, no `!important`.
- `#onboardChip` keeps its runtime repo label as a quiet control with a border
  (it is a switcher, not navigation). `#openAlerts` keeps ⚠ (status icon).
  `#navAdvanced` dropdown menu: `--surface-2`, `--radius-sm`, quiet items.
- All ids, order, handlers unchanged. `#modeBadge` stays in the input row.

## 5. Typography application map

- `body` → `--text-md`/`--line-ui` `--font-ui`, `--text-primary` on `--bg-base`.
- Transcript, cards, rows, chips-of-substance → `--text-sm`.
- Badges, counts, timestamps, uppercase micro-labels → `--text-xs` (floor; the
  old 0.60–0.72rem sizes are gone).
- Section/dialog headings → `--text-md`/`--text-lg`, `--line-tight`.
- Mono only via `--font-mono` (the scattered `'Cascadia Mono'`/`monospace`
  declarations are replaced); UI copy in mono is a smell except IDs/paths.
- rem sizes map to the four steps; em-relative sizes inside `.md`/tool lines
  stay relative.

## 6. Migration invariants (what Phase 1 does NOT touch)

- No JS handler logic, no ids, no markup structure except the header region's
  labels (ids/order preserved) — scenario pins re-verified: `#hud.min` boot
  state, `clip-path` diagonal mode selector (owner's design — tokenized, not
  retired), 50/50 workspace split, four experiment lanes, `rpillbtn` string,
  decisions sort/cap.
- No new endpoints, actions, CLI verbs, dependencies, fonts, assets.
- View-specific layout rework (board rows, experiments lanes, config sections,
  decisions inbox) is Phases 2–5; Phase 1 only re-bases their colors/type on
  tokens so those phases restyle structure, not palette.
- Deferred literals: colors inside JS template strings (SVG DAG fills etc.)
  are listed in the Phase 1 commit message and migrate in their view's phase.
- `prefers-reduced-motion: reduce` kills all animation/transitions globally.
