# Intake refinement — chat workspace IDE (vibe + copilot modes)

SPEC-116 door NEW checklist for SPEC-147. Filed 2026-07-17.

## Request (verbatim)

> Agora, vamos seguir na trilha da integração de uma IDE na interface da nossa
> GUI. A ideia era ter uma IDE bem responsiva, quanto mais responsiva melhor.
> Teremos dois modos de visualização na janela de chat. Modo 1) modo vibe -
> janela dividida em duas, 3/5 da tela são o nosso chat atual, 2/5 da tela
> serão um visualizador de diffs avançado pra quando o usuário clicar pra
> visualizar algum chip de diff / update de código, algo que traga essa visão
> de diff pra dentro do chat, mas que o usuário queira visualizar. Modo 2)
> modo copilot - janela dividada em duas, 1/2 da tela são o nosso chat atual,
> a outra 1/2 é a IDE. Essa IDE deve ser bem responsiva, ter linter, highlight
> de sintaxe, diffs, todos os recursos de IDEs modernas, além do usuário poder
> visualizar e editar o código ali mesmo. Nesse modo, um botão flutuante
> aparece do lado esquerdo da parte de dentro da IDE pra abrir/esconder o
> explorador de arquivos do projeto. Quando expandido, ele deve ocupar 1/4 da
> tela, flutuando sobre a interface do chat, até ser recolhido. Nele o usuário
> vai poder navegar pelas pastas do projeto e escolher ações como abrir
> arquivos, excluir arquivos, renomear arquivos, criar arquivos, o pacote todo
> que um explorador de arquivos deve ter. |||| Detalhes importantes: essa IDE
> vai ser utilizada tanto pra visualizar as diffs no modo vibe quanto para a
> edição no modo copilot. Você precisa ver se usamos algo já pronto aqui ou
> desenvolvemos do zero. Estamos presando pela responsividade, capacidade de
> expandirmos e melhorarmos ela, possivel integração com uma funcionalidade de
> auto completar código em modo copiloto. Pesquise e prospecte bastante aqui

Follow-up (2026-07-17, zero-touch requirement): o harness deve instalar as
dependências automaticamente, como faz com o python, além de gerenciar as libs
e possivelmente iniciar algum script da IDE, tudo sem intervenção do usuário.
O usuário final só clica no ui.bat / ui.sh e tudo é resolvido; zero
preocupações.

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search editor workspace ide` | no hit (`[]`) |
| doc-find | `python scripts/harness.py doc-find ide editor monaco codemirror diff embed` | hit: `docs/roadmap/chat-workspace.md` — a roadmap CLAIM on the space, explicitly "Not started. When picked up: SPEC-116 intake → its own spec" |

Decision: **NEW** (the roadmap doc mandates this intake; no spec covers the
workspace). Technology selection closed by research round
`docs/research/ide-embedded-gui.md` (2026-07-17): CodeMirror 6, vendored;
Monaco/from-scratch/Ace rejected on evidence.

## Goal

An IDE-grade workspace inside the chat panel: a vibe mode (3/5 chat + 2/5
diff viewer fed by diff chips) and a copilot mode (1/2 chat + 1/2 real editor
with syntax highlight, ruff diagnostics and a floating project explorer), on a
vendored CodeMirror 6 surface, provisioned automatically with zero user steps.

## Scope

In scope:
- M1: mode toggle (chat/vibe/copilot), resizable split, CM6 vendoring +
  zero-touch provisioning, chip → full-diff pane (unified + side-by-side).
- M2: copilot editor (open/edit/save with confirm + conflict guard), ruff
  lint endpoint + in-editor diagnostics.
- M3: floating explorer (1/4-screen overlay): navigate, open, create, rename,
  delete files.

Out of scope (seams left, nothing built):
- AI ghost-text autocomplete (future: one CM6 extension + one read-shaped POST).
- LSP integration; directory create/rename/delete; multi-file tabs.

## Actors & surfaces

- Actors: the owner (panel user); the harness UI server; provisioning
  pipeline (setup/ui launchers).
- Surfaces: GUI (supervision panel) + server HTTP routes + `ui.bat`/`ui.sh`.
- UI surface? **yes → Gherkin required** (in SPEC-147).

## Proposed acceptance criteria

- [ ] Mode pillbtn cycles chat → vibe → copilot; layout splits 100/0, 60/40,
      50/50; choice persists across reloads; chat mode is byte-identical to
      today's panel.
- [ ] Clicking ⧉ on a diff chip in vibe mode opens the FULL (uncapped) diff
      in the pane; chips keep their capped payloads; a pane miss degrades to
      the capped chip diff with a truncation notice.
- [ ] All CM6 assets are served from token-gated `/vendor/codemirror/` with
      per-file sha256 pins; the page makes zero external requests (CSP
      unchanged).
- [ ] `ui.bat`/`ui.sh` alone provision everything: missing venv → setup runs;
      missing/outdated vendor assets → auto-fetched before serve; provisioning
      failure never blocks the panel (degrade mode).
- [ ] Editor saves require `confirm: true` via the ACTIONS registry; a stale
      `baseSha` yields a conflict, not a clobber; saves are refused while a
      gate run is in flight; `.harness/`, `.git/`, `vendor/` and protected
      instruction files are unwritable; paths never escape the repo root.
- [ ] `POST /api/lint` returns ruff diagnostics for .py content on stdin;
      ruff absent → `{ok:false}` and the editor disables lint (gate never
      requires ruff).
- [ ] Explorer file ops (create/rename/delete) are mutating ACTIONS with the
      same discipline; `m5_ui_panel.py` head_actions updated in the same
      commit as every ACTIONS change.
- [ ] With vendor assets unprovisioned, every workspace surface degrades
      gracefully (colorized text diff; inert editor with setup hint) — the
      panel never bricks.

## Risks / blast radius

- Touches the panel's write trust boundary (first file-write surface):
  confinement module `ws_files.py` + ACTIONS discipline; m5 frozen set is the
  enforcement.
- `harness_ui_page.py` splice ordering (importmap before first dynamic
  import) — string-asserted in scenario.
- CM6 version skew across ~25 pinned files — single co-resolved set in
  `vendor/codemirror/manifest.json`; bump = one commit.
- Rollback: one revertable commit per milestone; chat mode default keeps the
  feature additive; reverting the manifest de-provisions assets.

## Open questions for the human

- None blocking. Decisions ratified 2026-07-17: CM6 núcleo (research round);
  no-build importmap vendoring; writes as ACTIONS verbs with in-process
  handler; `testing/` stays writable from the editor.
