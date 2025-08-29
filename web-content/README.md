# Secvara Public Website Content

This folder contains public‑facing Markdown pages derived from the SECURE program materials. Nothing in the original repository is moved or deleted; these pages reference the canonical sources in `Playbooks_and_templates/`.

## Information Architecture
- `index.md`: Landing page overview of the SECURE program and six principles.
- `secure-program.md`: Expanded overview and SECURE framework details.
- `tiers/`:
  - `aware.md`
  - `foundations.md`
  - `pillars.md`
  - `spire.md`
- `deliverables.md`: Public catalog of deliverables with short, client‑friendly definitions.
- `pricing.md`: Pricing ranges and disclaimers.
- `contact.md`: How to engage; CTA links.

## Interlinking Plan (When and How)
- Global navigation (header/footer on every page):
  - Home (`index.md`) → Program (`secure-program.md`) → Tiers (`tiers/*`) → Deliverables (`deliverables.md`) → Pricing (`pricing.md`) → Contact (`contact.md`).
- From `index.md`:
  - Link to the SECURE framework on `secure-program.md#the-secure-framework`.
  - Prominent CTAs to `tiers/foundations.md`, `tiers/pillars.md`, `tiers/spire.md`.
- From each tier page (`tiers/*.md`):
  - Link to specific deliverables anchors in `deliverables.md` (e.g., `deliverables.md#security-risk-assessment-sra`).
  - Link to `pricing.md` and `contact.md` for next steps.
- From `deliverables.md`:
  - For each deliverable, list “Included in Tiers” with links to the relevant tier pages.
  - CTA to `contact.md` for scoping and proposals.
- From `pricing.md`:
  - Link back to tier pages and to `contact.md` to request a proposal.
- Footer on all pages:
  - Link to `contact.md` and `pricing.md`.

## Source Mapping (Internal → Public)
- Service Catalog source: `Playbooks_and_templates/sales-gtm/service-catalog.md` → summarized in `index.md` and `secure-program.md`.
- Tier one‑pagers: `Playbooks_and_templates/tiers/*.md` → summarized in `website/tiers/*.md`.
- Deliverables: `Playbooks_and_templates/reference/deliverables-catalog.md` → curated in `website/deliverables.md`.
- Pricing: `Playbooks_and_templates/sales-gtm/pricing.md` → adapted in `website/pricing.md`.

## Assets
- Use logos from `icon/` for the public site. Do not move assets; reference them from the site generator or build pipeline.

## Next Steps
- If using a static site generator (e.g., GitHub Pages, Docusaurus, Astro), map these pages to routes and inject a shared header/footer to implement the interlinking above.
