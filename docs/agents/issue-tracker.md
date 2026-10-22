# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in the repo, written in Portuguese like the rest of the docs.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`. The current one is `.scratch/enxuto/`.
- The spec is `docs/spec.md`, a single spec for the whole project. This is an exception to `.scratch/<feature-slug>/spec.md`. New work edits it in place, in the section it changes. `GRILL.md` holds the decisions the spec comes from.
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` and continuing from the last file. Never use a single combined tickets file.
- Ticket layout:
  - `# NN: <título>`
  - `**What to build:**` (one paragraph, pointing to the spec section)
  - `**Blocked by:**` (ticket numbers, or `—`)
  - `**Status:**` (see `triage-labels.md`)
  - a `- [ ]` checklist. The last item is always a "Teste com olhos de usuário" run in `exemplo\`.
  - `**Notas de entrega:**` and `**Onde está agora (depois da entrega):**`, filled in on delivery
- Comments and conversation history append to the bottom of the file under a `## Comments` heading.
- `.scratch/enxuto/HANDOFF.md` holds the current state across sessions. Update it when tickets close.

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/issues/` with the next number.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly (`3` → `.scratch/enxuto/issues/03-*.md`).

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md`, holding the Notes, Decisions-so-far and Fog body.
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`). A `Status:` line records `claimed` or `resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are open, unblocked and unclaimed. The lowest number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading and set `Status: resolved`. Then append a context pointer (gist + link) to the Decisions-so-far section of `map.md`.
